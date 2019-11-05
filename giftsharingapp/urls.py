from django.urls import path
from . import views

app_name = "giftsharingapp"

urlpatterns = [
    # path('', views.redirect_root),
    path('', views.my_wishlist_view, name='my-gifts'),
    # path('', views.MyGiftListView.as_view(), name='my-gifts'),
    path('friends-gifts/invite-friend/', views.invite_friend, name='invite-friend'),
    path('manage_group/<int:group_id>/invite-friend/', views.invite_friend, name='invite-friend-to-group'),
    # path('friends-gifts/', views.FriendsGiftListView.as_view(), name='friends-gifts'),
    path('friends-gifts/', views.smart_santa_list_view, name='friends-gifts'),
    # path('gift/<int:pk>', views.GiftDetailView.as_view(), name='gift-detail'),
    # path('gift/create', views.GiftCreate.as_view(), name='gift-create'),
    # path('gift/update/<int:pk>', views.GiftUpdate.as_view, name='gift-update'),
    path('gift/delete/<int:pk>', views.GiftDelete.as_view(), name='gift-delete'),
    path('gift/add-new/', views.add_my_gift, name='add-my-gift'),
    path('gift/edit/<int:pk>', views.edit_my_gift, name='edit-my-gift'),
    path('gift/fill/<int:pk>', views.fill_gift, name='fill-gift'),
    path('gift/mark-taken/<int:pk>/<value>', views.mark_taken, name='mark-taken'),
    path('dismiss_notification', views.dismiss_notification, name='dismiss-notification'),
    path('accept_invite/', views.accept_invite, name='accept_invite'),
    path('decline_invite/', views.decline_invite, name='decline_invite'),
    path('review_invite/<int:invite_id>/<int:notification_id>', views.review_invite, name='review_invite'),
    path('manage_group/<int:group_id>',views.manage_group, name='manage_group'),
    path('create_group/', views.manage_group, name='create_group'),
    path('account/', views.account, name="account"),
    path('gift/mark-receievd/<int:pk>/<value>', views.mark_received, name='mark-received'),
    path('friend-profile/<int:friend_id>', views.friend_profile, name='friend-profile'),
    path('smart_santa_list_filter/', views.smart_santa_list_filter, name='smart_santa_list_filter'),



    # path('invite-friend/', views.FriendInviteCreate.as_view(), name='invite-friend'),

]
