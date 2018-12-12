from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from giftsharingapp.forms import CreateGiftForm, MarkGiftFilled, SignUpForm
from giftsharingapp.models import Gift, UserInfo, GifterGroup, Friendship, FriendInvite
from giftsharingapp.tokens import account_activation_token


import datetime
import sendgrid
from sendgrid.helpers.mail import *
import os

sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
from_email = Email("yulia@yuliashea.com")



def index(request):
    my_gifts = Gift.objects.all()
    print(my_gifts)
    context = {
        'my_gifts': my_gifts
    }
    return render(request, 'index.html', context=context)


def redirect_root(request):
    return HttpResponseRedirect(
            reverse_lazy('giftsharingapp:my-gifts'))

# def invite_friends(request):
#     if request.method == 'POST':
#         form = InviteFriendForm(request.POST)
#         if form.is_valid():
#
#     else:
#         form = InviteFriendForm()
#     return render(request, 'invite-friends.html', {'form': form})


def signup(request):
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
            print(urlsafe_base64_encode(force_bytes(user.pk)))
            text = render_to_string('registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            # user.email_user(subject, message)
            to_email = Email(username)
            content = Content("text/plain", text)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)

            # message.add_to(username)
            # message.set_from('SmartSant')
            # message.set_subject(subject)
            # message.set_html(text)
            # sg.send(message)

            # send_mail(subject, message, 'yulia.shea@gmail.com', [username], fail_silently=False)

            return redirect('account_activation_sent')

            # user.refresh_from_db()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # # first_name = form.cleaned_data.get('first_name')
            # # print(form.cleaned_data)
            # user.email = username
            # # user.first_name = first_name
            # user.save()
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            # send_mail('Test email', 'Here is the message.', 'yulia.shea@gmail.com', [username],
            #           fail_silently=False)
            # return redirect('giftsharingapp:my-gifts')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

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


class MyGiftListView(LoginRequiredMixin, generic.ListView):
    model = Gift
    context_object_name = 'gifts'
    # queryset = Gift.objects.filter(filled=False)
    template_name = 'giftsharingapp/list_my_gifts.html'
    paginate_by = 30

    def get_queryset(self):
        return Gift.objects.filter(owner=self.request.user).order_by('date_saved')


class GiftDetailView(LoginRequiredMixin, generic.DetailView):
    model = Gift
    template_name = 'giftsharingapp/gift-view.html'


class GiftDelete(DeleteView):
    model = Gift
    success_url = reverse_lazy('giftsharingapp:my-gifts')


class GiftCreate(CreateView):
    model = Gift
    fields = ['name', 'description', 'link', 'price', 'active_til']

class FriendInviteCreate(CreateView):
    model = FriendInvite
    fields = ['friend_email', 'message']

class GiftUpdate(UpdateView):
    model = Gift
    fields = ['name', 'description', 'link', 'price', 'active_til']


class FriendsGiftListView(LoginRequiredMixin, generic.ListView):
    model = Gift
    context_object_name = 'gifts'
    template_name = 'giftsharingapp/list_friends_gifts.html'
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
            owner_friend_gifts = owner_friend.requested_gifts.all()
            # owner_friend_gifts = owner_friend.owner.requested_gifts.filter(~Q(owner=owner))
            owner_friends_gifts.extend(owner_friend_gifts)

        return owner_friends_gifts
        # return ordered

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
                owner_id=request.user.id
            )
            new_gift.save()
            return HttpResponseRedirect(reverse('giftsharingapp:my-gifts'))
    else:
        proposed_active_til = datetime.date.today() + datetime.timedelta(weeks=12)
        form = CreateGiftForm(initial={'active_til': proposed_active_til})
        context = {
            'form': form
        }
        return render(request, 'giftsharingapp/gift-add.html', context)


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
            'form': form
        }
        return render(request, 'giftsharingapp/gift-edit.html', context)

def mark_taken(request, pk, value):
    gift = get_object_or_404(Gift, pk=pk)

    gift.filled = value
    gift.filled_by = request.user
    gift.save()

    return HttpResponseRedirect(reverse('giftsharingapp:friends-gifts'))

def fill_gift(request, pk):
    gift = get_object_or_404(Gift, pk=pk)

    # if the gift is taken and not by me
    if gift.filled == True and gift.filled_by != request.user:
        context = {
            'pk': gift.id,
            'gift': gift
        }
        return render(request, 'giftsharingapp/gift-fill.html', context)

    # if the gift is not taken or taken by me
    else:
        if request.method == 'POST':
            form = MarkGiftFilled(request.POST)
            if form.is_valid():
                gift.filled = form.cleaned_data['filled']
                gift.filled_by = request.user
                gift.save()

                return HttpResponseRedirect(reverse('giftsharingapp:friends-gifts'))
        else:
            form = MarkGiftFilled({'filled': gift.filled})
            context = {
                'form': form,
                'gift': gift
            }
            return render(request, 'giftsharingapp/gift-fill.html', context)





#
# def edit_gift(request, pk=None):
#
#
#     owner = request.user
#
#     if request.method == 'POST':
#         form = CreateGiftForm(request.POST)
#
#         if form.is_valid():
#             # if creating a new gift
#             if pk is None:
#                 new_gift = Gift(
#                     name=form.cleaned_data['name'],
#                     description=form.cleaned_data['description'],
#                     link=form.cleaned_data['link'],
#                     price=form.cleaned_data['price'],
#                     desirability_rank=form.cleaned_data['desirability_rank'],
#                     active_til=form.cleaned_data['active_til'],
#                     owner_id=owner.id
#                 )
#                 new_gift.save()
#
#             # if editing a gift
#             else:
#                 gift = get_object_or_404(Gift, pk=pk)
#                 # if this is not my gift, allow to fill
#                 if gift.owner != request.user:
#                     formToFill = MarkGiftFilled(request.POST)
#                     return HttpResponseForbidden()
#                 # if this is my gift, edit
#                 else:
#                     gift.name = form.cleaned_data['name']
#                     gift.description = form.cleaned_data['description']
#                     gift.link = form.cleaned_data['link']
#                     gift.price = form.cleaned_data['price']
#                     gift.desirability_rank = form.cleaned_data['desirability_rank']
#                     gift.active_til = form.cleaned_data['active_til']
#                     gift.save()
#
#             return HttpResponseRedirect(reverse('giftsharingapp:my-gifts'))
#
#     else:
#         if pk is None:
#             proposed_active_til = datetime.date.today() + datetime.timedelta(weeks=12)
#             form = CreateGiftForm(initial={'active_til': proposed_active_til})
#         else:
#             gift = get_object_or_404(Gift, pk=pk)
#             if gift.owner != request.user:
#                 form = MarkGiftFilled({
#                     'filled': True
#                 })
#                 # return HttpResponseForbidden()
#             else:
#                 form = CreateGiftForm({
#                     'name': gift.name,
#                     'description': gift.description,
#                     'link': gift.link,
#                     'price': gift.price,
#                     'desirability_rank': gift.desirability_rank,
#                     'active_til': gift.active_til,
#                     'owner_id': gift.owner_id
#                 })
#
#     context = {
#         'form': form,
#         'gift': gift
#     }
#
#     if pk is None:
#         return render(request, 'giftsharingapp/gift-add.html', context)
#     else:
#         if gift.owner != request.user:
#             return render(request, 'giftsharingapp/gift-view.html', context)
#         else:
#             return render(request, 'giftsharingapp/gift-edit.html', context)
#
