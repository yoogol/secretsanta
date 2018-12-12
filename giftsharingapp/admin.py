from django.contrib import admin
from giftsharingapp.models import Gift, GifterGroup, UserInfo, Friendship

# Register your models here.
admin.site.register(Gift)
admin.site.register(GifterGroup)
admin.site.register(UserInfo)
admin.site.register(Friendship)

