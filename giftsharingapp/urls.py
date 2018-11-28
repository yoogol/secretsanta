from django.urls import path
from . import views

app_name = "giftsharingapp"

urlpatterns = [
    path('', views.redirect_root),
    path('my-gifts/', views.MyGiftListView.as_view(), name='my-gifts'),
    path('friends-gifts/', views.FriendsGiftListView.as_view(), name='friends-gifts'),
    path('gift/<int:pk>', views.GiftDetailView.as_view(), name='gift-detail'),
    path('gift/create', views.GiftCreate.as_view(), name='gift-create'),
    path('gift/update/<int:pk>', views.GiftUpdate.as_view, name='gift-update'),
    path('gift/delete/<int:pk>', views.GiftDelete.as_view(), name='gift-delete'),
    path('gift/add-new/', views.add_my_gift, name='add-my-gift'),
    path('gift/edit/<int:pk>', views.edit_my_gift, name='edit-my-gift'),
    path('gift/fill/<int:pk>', views.fill_gift, name='fill-gift'),
    path('gift/mark-taken/<int:pk>/<value>', views.mark_taken, name='mark-taken'),
]