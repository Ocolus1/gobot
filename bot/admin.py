from django.contrib import admin
from .views import (Cmd, Verification, Command, Email, Telegram,
Tweet, Facebook, Instagram, Youtube, Reddit, Ethaddress, Link)

# Register your models here.
admin.site.register(Cmd)
admin.site.register(Verification)
admin.site.register(Command)
admin.site.register(Email)
admin.site.register(Telegram)
admin.site.register(Facebook)
admin.site.register(Instagram)
admin.site.register(Youtube)
admin.site.register(Reddit)
admin.site.register(Ethaddress)
admin.site.register(Link)
admin.site.register(Tweet)