from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Comment


class MyUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('country', 'city', 'birthday')}),
    )

admin.site.register(User, MyUserAdmin)


class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('created_dt', )
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
