from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
import django.utils.timezone as timezone
from django.utils.timezone import make_aware
from giftsharingapp.tokens import generate_invite_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from sendgrid.helpers.mail import *
import os
import sendgrid
from django.db.models import Q
sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("yulia@yuliashea.com")

# Create your models here.

class Occasion(models.Model):
    recurring = models.BooleanField(default=False)
    date = models.DateField(blank=True)
    is_common_holiday = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class GifterGroup(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_visible_gifts(self, request):
        today = date.today()
        members_memberships = self.groups_memberships.all()
        gifts = []
        for m in members_memberships:
            if m.member != request.user:
                member_gifts_unlimited = m.member.gifts_suggested_for_user.filter(
                    active_til__gte=today,
                    limited_sharing=False,
                    received=False
                )
                member_gifts_limited = m.member.gifts_suggested_for_user.filter(
                    active_til__gte=today,
                    limited_sharing=True,
                    shared_with_groups__id=self.id,
                    received=False
                )
                gifts.extend(member_gifts_limited)
                gifts.extend(member_gifts_unlimited)

    def send_multiple_invites(self, string_of_emails, message, current_site):
        emails = [email.strip() for email in string_of_emails.split(',')]
        print(emails)
        for email in emails:
            invite = FriendInvite(sent_by_user=self.created_by,
                                  email_to=email,
                                  message = message,
                                  is_group_invite=True,
                                  invited_to_group=self)
            invite.save()
            invite.send_invite(current_site)
        return True


class Gift(models.Model):
    # needed for form
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, null=True, blank=True)
    link = models.URLField(max_length=2000, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    desirability_rank = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    active_til = models.DateField(blank=True, null=True)
    occasion = models.ManyToManyField(Occasion)
    limited_sharing = models.BooleanField(default=False)
    shared_with_groups = models.ManyToManyField(GifterGroup)
    shared_with_users = models.ManyToManyField(User)
    image_url = models.URLField(blank=True, null=True)

    # needed for views
    taken = models.BooleanField(default=False)
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="gift_filled_by_user")
    received = models.BooleanField(default=False)

    # privacy and ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="gifts_added_by_user")
    created_for = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="gifts_suggested_for_user")
    gift_visible_for_receiver = models.BooleanField(default=True)
    taken_visible_for_receiver = models.BooleanField(default=False)

    # metadata
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_last_changed = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    date_received = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('giftsharingapp:gift-detail', args=[str(self.id)])

    class Meta:
        ordering = ['owner']

    @property
    def is_expired(self):
        if self.active_til and date.today() > self.active_til:
            return True
        return False


class GiftNote(models.Model):
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="note_added_by_user")
    message = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.message


class GiftQuestion(models.Model):
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="question_added_by_user")
    question = models.TextField(max_length=2000, null=True, blank=True)
    answer = models.TextField(max_length=2000, null=True, blank=True)
    anonymous = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class FriendInvite(models.Model):
    sent_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invitations_sent")
    date_sent = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    sent_to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invitations_received")
    email_to = models.EmailField(max_length=200)
    message = models.TextField(max_length=2000, null=True, blank=True)
    date_accepted = models.DateTimeField(blank=True, null=True)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    date_declined = models.DateTimeField(blank=True, null=True)
    is_group_invite = models.BooleanField(default=False)
    invited_to_group = models.ForeignKey(GifterGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="groups_invitations")
    token = models.TextField(max_length=2000, null=True, blank=True)

    def send_invite(self, current_site):
        invitation_token = generate_invite_token(self.sent_by_user_id, self.email_to)
        self.token = invitation_token
        self.save()
        email_subject = self.sent_by_user.first_name.capitalize() + ' wants to be your Smart Santa!'
        if self.is_group_invite:
            email_template = 'giftsharingapp/email-templates/group-invite.html'
        else:
            email_template = 'registration/friend_invite_email.html'
        if User.objects.filter(email=self.email_to).exists():
            self.sent_to_user_id = User.objects.get(email=self.email_to).id
            self.save()
            email_subject = self.sent_by_user.first_name.capitalize() + ' invites you to a Smart Santa group!'
            if self.is_group_invite:
                message = "{name} invites you to join {group} group".format(
                    name=self.sent_by_user.first_name.capitalize(),group=self.invited_to_group.name
                )
            else:
                message = "{name} wants to be your Smart Santa".format(
                                      name=self.sent_by_user.first_name.capitalize())
            notify = Notification(owner_id=self.sent_to_user_id,
                                  issuer_type=ContentType.objects.get_for_model(self),
                                  issuer_id=self.id,
                                  message=message)
            notify.save()

        text = render_to_string(email_template, {
            'sent_by_user': self.sent_by_user,
            'domain': current_site.domain,
            'email_to': self.email_to,
            'sent_to_user': self.sent_to_user,
            'token': invitation_token
        })
        to_email = Email(self.email_to)
        content = Content("text/plain", text)
        mail = Mail(from_email, email_subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True


    def accept_invite(self):
        timestamp = timezone.datetime.now()
        aware_timestamp = make_aware(timestamp)
        message = ""
        if self.sent_by_user_id != self.sent_to_user_id and not self.accepted and not self.declined:
            friendship_exists = Friendship.objects.filter(Q(user1=self.sent_by_user,user2=self.sent_to_user) | Q(user1=self.sent_to_user,user2=self.sent_by_user)).exists()
            if not self.is_group_invite and not friendship_exists:
                new_friendship = Friendship(user1=self.sent_by_user, user2=self.sent_to_user, friendinvite=self,
                                        friends_since=aware_timestamp)
                new_friendship.save()
                message = "Hooray! You and {user} are now each other's Smart Santas".format(
                    user=self.sent_by_user.first_name.capitalize())
            if self.is_group_invite and friendship_exists:
                new_membership = GroupMembership(member=self.sent_to_user,giftergroup=self.invited_to_group, groupinvite=self)
                new_membership.save()
                message = "Congrats on joining {user} in {group} group. Let's go {group}s!".format(
                    user=self.sent_by_user.first_name.capitalize(), group=self.invited_to_group.name.capitalize())
            if not self.is_group_invite and friendship_exists:
                message = "You and {user} are already friends on Smart Santa".format(user=self.sent_by_user.first_name.capitalize())
            self.accepted = True
            self.date_accepted = aware_timestamp
            self.save()
            return True, message

        elif self.accepted:
            message = "You and {user} are already Smart Santa friends".format(user=self.sent_by_user.first_name.capitalize())
        elif self.declined:
            message = "You have previously declined {user}'s request. Try sending them a friend request".format(user=self.sent_by_user.first_name.capitalize())
        elif self.sent_by_user_id == self.sent_to_user_id:
            message = "You seem to be trying to befriend yourself :)"
        return False, message

    def decline_invite(self):
        timestamp = timezone.datetime.now()
        aware_timestamp = make_aware(timestamp)
        if not self.accepted and not self.declined:
            message = "You have declined {user}'s request to connect".format(user=self.sent_by_user.first_name.capitalize())
            self.declined = True
            self.date_declined = aware_timestamp
            self.save()
        else:
            message = "You have already responded to this request"
        return True, message

    def __str__(self):
        return self.sent_by_user.first_name + " invited " + self.email_to


class UserInfo(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='userinfo')
    email_confirmed = models.BooleanField(default=False)
    invited = models.ForeignKey(FriendInvite, on_delete=models.CASCADE, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.owner.username

    def unviewed_notifications(self):
        return self.owner.notification_set.filter(viewed=False)


class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_initiated")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_accepted")
    friendinvite = models.ForeignKey(FriendInvite, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    friends_since = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user1.username + " - " + self.user2.username


class GiftUpdateRequest(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="giftupdate_requests_sent")
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="giftupdate_requests_received")
    message = models.TextField(max_length=2000, null=True, blank=True)
    date_sent = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    anonymous = models.BooleanField(default=True)


class FriendNote(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    friendship = models.ForeignKey(Friendship, on_delete=models.SET_NULL, null=True)
    note = models.TextField(max_length=10000, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class GroupMembership(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_memberships")
    giftergroup = models.ForeignKey(GifterGroup, on_delete=models.CASCADE, related_name="groups_memberships")
    groupinvite = models.ForeignKey(FriendInvite, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    member_since = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_admin = models.BooleanField(default=False)


class GiftPreferences(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    favorite_colors = models.TextField(max_length=2000, null=True, blank=True)


class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    viewed = models.BooleanField(default=False)
    message = models.TextField(max_length=2000, null=True, blank=True)
    issuer_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    issuer_id = models.PositiveIntegerField(null=True)
    action_link = models.TextField(max_length=2000, null=True, blank=True)
    # dismissable


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        ui = UserInfo.objects.create(owner=instance)
        # gg = GifterGroup.objects.get(name="default")
        # ui.gifter_groups.add(gg)


@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.userinfo.save()


@receiver(post_save, sender=Notification)
def save_action_link(sender, instance, created, **kwargs):
    if created and instance.issuer_type.model == 'friendinvite':
        print("i'm here")
        friendinvite = instance.issuer_type.get_object_for_this_type(id=instance.issuer_id)
        print(friendinvite)
        instance.action_link = reverse('giftsharingapp:review_invite', args=[friendinvite.id, instance.id])
        instance.save()