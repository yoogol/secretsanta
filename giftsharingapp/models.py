from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Gift(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, null=True, blank=True)
    link = models.URLField(max_length=2000, null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    desirability_rank = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    date_saved = models.DateTimeField(auto_now_add=True, blank=True)
    filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="filled_gifts")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="requested_gifts")
    active_til = models.DateField(blank=True, null=True)

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


class GifterGroup(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_groups")
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name


class FriendInvite(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    friend_email = models.EmailField(max_length=200)
    message = models.TextField(max_length=2000, null=True, blank=True)
    date_invited = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.inviter + " invited " + self.friend_email


class UserInfo(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    gifter_groups = models.ManyToManyField(GifterGroup)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.owner.username


class Friendship(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_initiator")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendship_acceptor")

    def __str__(self):
        return self.user1.username + " - " + self.user2.username


@receiver(post_save, sender=User)
def create_user_info(sender, instance, created, **kwargs):
    if created:
        ui = UserInfo.objects.create(owner=instance)
        # gg = GifterGroup.objects.get(name="default")
        # ui.gifter_groups.add(gg)


@receiver(post_save, sender=User)
def save_user_info(sender, instance, **kwargs):
    instance.userinfo.save()
