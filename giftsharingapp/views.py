from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden,HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import pytz



from giftsharingapp.forms import CreateGiftForm, MarkGiftFilled, SignUpForm, InviteFriend, CreateGroupForm, InviteFormSet
from giftsharingapp.models import *
from giftsharingapp.tokens import account_activation_token, generate_invite_token

import json
import datetime
import sendgrid
from sendgrid.helpers.mail import *
import os

from django.contrib.auth.decorators import login_required

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("yulia@yuliashea.com")


@login_required
@csrf_exempt
def dismiss_notification(request):
    n = Notification.objects.get(id=request.POST.get('notification_id'))
    if request.user.id != n.owner_id:
        return HttpResponse(
            json.dumps({'result': 'Error'}),
            content_type='application/json'
        )
    n.viewed = True
    n.save()
    response_data = {}
    response_data['result'] = 'Success'
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


def signup(request, token=None):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            username = form.cleaned_data.get('username')
            user.email = username
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your SmartSanta Account'
            text = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = Email(username)
            content = Content("text/plain", text)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)

            return redirect('account_activation_sent')

    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'my_email': "unknown", 'inviter_email': "unknown"})


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.userinfo.email_confirmed = True
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('giftsharingapp:my-gifts')
        else:
            # invalid link
            return render(request, 'registration/account_activation_invalid.html')


@login_required
def my_wishlist_view(request):
    order_by = request.GET.get('order_by')
    if not order_by:
        order_by ='date_created'
    active_gifts = Gift.objects.filter(owner=request.user, received=False).order_by(order_by)
    received_gifts = Gift.objects.filter(owner=request.user, received=True).order_by(order_by)
    print(active_gifts),
    print(received_gifts)
    return render(request, 'giftsharingapp/menu-level-templates/my_wishlist.html', {'active_gifts': active_gifts, 'received_gifts': received_gifts})


class MyGiftListView(LoginRequiredMixin, generic.ListView):
    model = Gift
    context_object_name = 'gifts'
    template_name = 'giftsharingapp/menu-level-templates/my_wishlist.html'
    # paginate_by = 30

    def get_queryset(self):
        return Gift.objects.filter(owner=self.request.user).order_by('date_created')


class GiftDelete(LoginRequiredMixin, DeleteView):
    model = Gift
    success_url = reverse_lazy('giftsharingapp:my-gifts')

# class GiftCreate(CreateView):
#     model = Gift
#     fields = ['name', 'description', 'link', 'price', 'active_til']
#
#
# class GiftUpdate(UpdateView):
#     model = Gift
#     fields = ['name', 'description', 'link', 'price', 'active_til']


@login_required
def smart_santa_list_view(request):

    # gift_group_id_dict = {}
    # gift_group_id_list = []
    # owner_friends_gifts = []

    owner = request.user
    owner_groups = [membership.giftergroup for membership in GroupMembership.objects.filter(member=request.user)]

    owner_friendships = Friendship.objects.filter(Q(user1=owner) | Q(user2=owner))
    owner_friends = []
    owner_friends_gifts = []
    owner_groups_gifts = []

    for owner_friendship in owner_friendships:
        if owner_friendship.user1 == owner:
            owner_friends.append(owner_friendship.user2)
        else:
            owner_friends.append(owner_friendship.user1)

    for owner_friend in owner_friends:
        # owner_friend_gifts = owner_friend.gifts_added_by_user.all()
        owner_friends_gifts.extend(owner_friend.userinfo.get_visible_gifts(request))
        # owner_friends_gifts.extend(owner_friend_gifts)

    for owner_group in owner_groups:
        owner_groups_gifts.extend(owner_group.get_visible_gifts(request))

    dedup_list = list(set(owner_friends_gifts) | set(owner_groups_gifts))
    # for gift in owner_friends_gifts:
    #     gifts_group_ids = []
    #     for group in owner_groups:
    #         if gift.owner.users_memberships.filter(giftergroup=group).exists():
    #             gift_group_id_list.append((group.id, gift.id))
    #             gifts_group_ids.append(group.id)
    #     if gifts_group_ids:
    #         for group_id in gifts_group_ids:
    #             if hasattr(gift_group_id_dict, str(gift.id)):
    #                 gift_group_id_dict[gift.id].append(group_id)
    #             else:
    #                 gift_group_id_dict[gift.id] = [group_id]
    #     else:
    #         gift_group_id_dict[gift.id] = ["no group"]
    # print(gift_group_id_list)
    context = {
        # "gift_group_id_dict": gift_group_id_dict,
        # "gift_group_id_list": gift_group_id_list,
        "gifts": dedup_list,
        "groups": owner_groups,
        "friends": owner_friends
    }

    return render(request, 'giftsharingapp/menu-level-templates/santas_list.html', context)


@csrf_exempt
def smart_santa_list_filter(request):
    if request.user.is_authenticated:
        friend_id = request.GET.get('friend_id')
        group_id = request.GET.get('group_id')
        gifts = []
        error = ""
        context = {}
        if friend_id:
            if User.objects.filter(id=friend_id).exists() and request.user.userinfo.am_i_friends_with(friend_id):
                friend = User.objects.get(id=friend_id)
                context['selected_friend'] = friend
                gifts = friend.userinfo.get_visible_gifts(request)
            elif not User.objects.filter(id=friend_id).exists():
                error = "Sorry, this friend is no longer on Smart Santa :("
            elif not request.user.userinfo.am_i_friends_with(friend_id):
                error = "Sorry, you are no longer friends with this user :("
        if group_id:
            if GifterGroup.objects.filter(id=group_id).exists() and request.user.userinfo.am_i_member_of(group_id):
                group = GifterGroup.objects.get(id=group_id)
                gifts = group.get_visible_gifts(request)
                context['selected_group'] = group
            elif not GifterGroup.objects.filter(id=group_id).exists():
                error = "Sorry, this group no longer exists"
            elif not request.user.userinfo.am_i_member_of(group_id):
                error = "Sorry, you are not a member of this group"

        context['gifts'] = gifts
        context['error'] = error
        # context = {
        #     'gifts': gifts,
        #     'error': error
        # }
        return render(request, 'giftsharingapp/menu-level-templates/subtemplates/gift-list.html', context)
    else:
        return redirect('login')


class FriendsGiftListView(LoginRequiredMixin, generic.ListView):
    model = Gift
    context_object_name = 'gifts'
    template_name = 'giftsharingapp/menu-level-templates/santas_list.html'
    # paginate_by = 30

    def get_queryset(self):
        owner = self.request.user
        owner_friendships = Friendship.objects.filter(Q(user1=owner) | Q(user2=owner))

        # owner = self.request.user
        # owner_groups = UserInfo.objects.get(owner = owner).gifter_groups.all()
        #
        owner_friends = []
        owner_friends_gifts = []

        for owner_friendship in owner_friendships:
            print(owner_friendship.user1)
            if owner_friendship.user1 == owner:
                owner_friends.append(owner_friendship.user2)
            else:
                owner_friends.append(owner_friendship.user1)

        # for owner_group in owner_groups:
        #     owner_group_members = owner_group.userinfo_set.all()
        #     owner_friends.extend(owner_group_members)

        for owner_friend in owner_friends:
            owner_friend_gifts = owner_friend.gift_added_by_user.all()
            # owner_friend_gifts = owner_friend.owner.requested_gifts.filter(~Q(owner=owner))
            owner_friends_gifts.extend(owner_friend_gifts)

        return owner_friends_gifts
        # return ordered


@csrf_exempt
def accept_invite(request, token=None):
    if token:
        # invite = FriendInvite.objects.get(token=token)
        return HttpResponseRedirect(reverse('signup', args=(token,)))
    else:
        invite_id = request.POST.get('invite_id')
        invite = FriendInvite.objects.get(id=invite_id)
    if request.user.id != invite.sent_to_user_id:
        return HttpResponse(
            json.dumps({'result': 'Error'}),
            content_type='application/json'
        )
    success, message = invite.accept_invite()
    response_data = {}
    response_data['redirect_url'] = reverse('giftsharingapp:friends-gifts')
    response_data['message'] = message
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


@csrf_exempt
def decline_invite(request):
    invite_id = request.POST.get('invite_id')
    invite = FriendInvite.objects.get(id=invite_id)
    if request.user.id != invite.sent_to_user_id:
        return HttpResponse(
            json.dumps({'result': 'Error'}),
            content_type='application/json'
        )
    success, message = invite.decline_invite()
    response_data = {}
    response_data['result'] = 'Success'
    response_data['redirect_url'] = reverse('giftsharingapp:friends-gifts')
    response_data['message'] = message
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


def review_invite(request, invite_id, notification_id):
    invite = FriendInvite.objects.get(id=invite_id)
    notification = Notification.objects.get(id=notification_id)
    if request.user.id != invite.sent_to_user_id or request.user.id != notification.owner_id:
        return redirect('/login/!next=%s' % request.path)
    context = {}
    context['invite'] = invite
    notification.viewed = True
    notification.save()
    return render(request, 'giftsharingapp/single-item-templates/review_invite.html', context)


def invite_friend(request, group_id):
    print(group_id)
    if request.method == 'POST':
        form = InviteFriend(request.POST)
        if form.is_valid():
            # create invitation
            # invitation_token = generate_invite_token(request.user.id, form.cleaned_data['email_to'])

            new_invite = FriendInvite(
                sent_by_user_id=request.user.id,
                email_to=form.cleaned_data['email_to'],
                message=form.cleaned_data['message'],
                # token=invitation_token
            )
            if group_id:
                new_invite.is_group_invite = True
                new_invite.invited_to_group_id = group_id
            new_invite.save()
            current_site = get_current_site(request)
            ready = new_invite.send_invite(current_site)

            # check if friend already registered
            # if User.objects.filter(email=new_invite.email_to).exists():
            #     new_invite.sent_to_user_id = User.objects.get(email=new_invite.email_to).id
            #     new_invite.save()
            #     notify = Notification(owner_id=new_invite.sent_to_user_id,
            #                           issuer_type=ContentType.objects.get_for_model(new_invite),
            #                           issuer_id=new_invite.id,
            #                           message="{name} wants to be your Smart Santa".format(name=new_invite.sent_by_user.first_name.capitalize()))
            #     notify.save()
            #
            # current_site = get_current_site(request)
            # subject = request.user.first_name.capitalize() + ' wants to be your Smart Santa!'
            # text = render_to_string('registration/friend_invite_email.html', {
            #     'sent_by_user': new_invite.sent_by_user,
            #     'domain': current_site.domain,
            #     'email_to': new_invite.email_to,
            #     'sent_to_user': new_invite.sent_to_user,
            #     'token': invitation_token
            # })
            # to_email = Email(new_invite.email_to)
            # content = Content("text/plain", text)
            # mail = Mail(from_email, subject, to_email, content)
            # response = sg.client.mail.send.post(request_body=mail.get())
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)

        return HttpResponseRedirect(reverse('giftsharingapp:friends-gifts'))
    else:
        form = InviteFriend()
        context = {
            'form': form
        }
        return render(request, 'giftsharingapp/single-item-templates/fiend.html', context)


@login_required
def manage_group(request, group_id=None):
    context = {}
    # group name + save button
    if request.method == 'POST':
        friends_emails = request.POST.get('emails')
        message = request.POST.get('message')
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            new_group = GifterGroup(
                name=form.cleaned_data['name'],
                created_by=request.user,
            )
            new_group.save()
            group_id = new_group.id
            new_membership = GroupMembership(
                member=request.user,
                giftergroup=new_group,
                is_admin=True
            )
            new_membership.save()
            current_site = get_current_site(request)
            new_group.send_multiple_invites(friends_emails, message, current_site)
            return HttpResponseRedirect(reverse('giftsharingapp:manage_group', args=(group_id,)))

        # create group or edit name

    if group_id:
        this_group = GifterGroup.objects.get(id=group_id)
        user_is_active_member = this_group.groups_memberships.filter(member=request.user,is_active=True).exists()
        context['user_is_active_member'] = user_is_active_member
        if user_is_active_member:
            memberships = this_group.groups_memberships.filter(is_active=True).exclude(member=request.user)
            context['memberships'] = memberships
            context['group'] = this_group
            gifts = this_group.get_visible_gifts(request)

            # for membership in memberships:
            #     gifts.extend(membership.member.gifts_added_by_user.all())
            context['gifts'] = gifts
    else:
        form = CreateGroupForm()
        emailform = InviteFormSet()
        context['form'] = form
        context['emailforms'] = emailform

    return render(request, 'giftsharingapp/single-item-templates/manage_group.html', context)


def add_my_gift(request):
    if request.method == 'POST':
        form = CreateGiftForm(request.POST)
        if form.is_valid():
            new_gift = Gift(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                link=form.cleaned_data['link'],
                price=form.cleaned_data['price'],
                # desirability_rank=form.cleaned_data['desirability_rank'],
                active_til=form.cleaned_data['active_til'],
                owner_id=request.user.id,
                created_for_id=request.user.id
            )
            new_gift.save()
            return HttpResponseRedirect(reverse('giftsharingapp:my-gifts'))
    else:
        proposed_active_til = datetime.date.today() + datetime.timedelta(weeks=12)
        form = CreateGiftForm(initial={'active_til': proposed_active_til})
        context = {
            'form': form
        }
        return render(request, 'giftsharingapp/single-item-templates/manage_gift.html', context)


def edit_my_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)
    if request.method == 'POST':
        form = CreateGiftForm(request.POST)
        if form.is_valid():
            gift.name = form.cleaned_data['name']
            gift.description = form.cleaned_data['description']
            gift.link = form.cleaned_data['link']
            gift.price = form.cleaned_data['price']
            # gift.desirability_rank = form.cleaned_data['desirability_rank']
            gift.active_til = form.cleaned_data['active_til']
            gift.save()
            return HttpResponseRedirect(reverse('giftsharingapp:my-gifts'))
    else:
        form = CreateGiftForm({
            'name': gift.name,
            'description': gift.description,
            'link': gift.link,
            'price': gift.price,
            'desirability_rank': gift.desirability_rank,
            'active_til': gift.active_til,
            'owner_id': gift.owner_id
        })
        context = {
            'form': form,
            'gift': gift
        }
        return render(request, 'giftsharingapp/single-item-templates/manage_gift.html', context)


def mark_taken(request, pk, value):
    gift = get_object_or_404(Gift, pk=pk)

    gift.taken = value
    gift.taken_by = request.user
    gift.save()

    return HttpResponseRedirect(reverse('giftsharingapp:friends-gifts'))


def mark_received(request, pk, value):
    gift = get_object_or_404(Gift, pk=pk)

    gift.received = value
    gift.date_received = timezone.now()
    gift.save()

    return HttpResponseRedirect(reverse('giftsharingapp:my-gifts'))


def fill_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)

    # if the gift is taken and not by me
    if gift.taken == True and gift.taken_by != request.user:
        context = {
            'pk': gift.id,
            'gift': gift
        }
        return render(request, 'giftsharingapp/single-item-templates/view_and_fill_gift.html', context)

    # if the gift is not taken or taken by me
    else:
        if request.method == 'POST':
            form = MarkGiftFilled(request.POST)
            if form.is_valid():
                gift.taken = form.cleaned_data['taken']
                gift.taken_by = request.user
                gift.save()

                return HttpResponseRedirect(reverse('giftsharingapp:friends-gifts'))
        else:
            form = MarkGiftFilled({'taken': gift.taken})
            context = {
                'form': form,
                'gift': gift
            }
            return render(request, 'giftsharingapp/single-item-templates/view_and_fill_gift.html', context)


@login_required()
def account(request):
    return render(request, 'giftsharingapp/menu-level-templates/account.html')


@login_required()
def friend_profile(request, friend_id):
    print(friend_id)
    return render(request, 'giftsharingapp/single-item-templates/friend_profile.html')