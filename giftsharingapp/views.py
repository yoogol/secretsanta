from django.shortcuts import render
from giftsharingapp.models import Gift, UserInfo
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls import reverse
import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q

from giftsharingapp.forms import CreateGiftForm, MarkGiftFilled
from django.views.generic.edit import CreateView, UpdateView, DeleteView

import operator

# Create your views here.

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
        owner_groups = UserInfo.objects.get(owner = owner).gifter_groups.all()

        owner_friends = []
        owner_friends_gifts = []

        for owner_group in owner_groups:
            owner_group_members = owner_group.userinfo_set.all()
            owner_friends.extend(owner_group_members)

        for owner_friend in owner_friends:
            owner_friend_gifts = owner_friend.owner.requested_gifts.filter(~Q(owner=owner))
            owner_friends_gifts.extend(owner_friend_gifts)

        # def getName(elem):
        #     print(elem)
        #     user = elem.owner
        #     name = user.username
        #     print(name)
        #     return name

        # print(owner_friends_gifts.sort(key=getName))
        # print(owner_friends_gifts)
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
