from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'email', 'role',
        'is_superuser', 'first_name', 'last_name',
    )
    list_editable = ('role',)
    search_fields = ('username', 'role',)
    list_filter = ('email','username', 'first_name')

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'user', 'author' )
    # list_editable = ('role',)
    # search_fields = ('username', 'role',)
