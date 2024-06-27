from django.contrib import admin
from Authentication.models import UserProfile,User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['username','email','full_name','id','is_active']
    search_fields = ['email']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','username','full_name','id']

admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(User,UserAdmin)