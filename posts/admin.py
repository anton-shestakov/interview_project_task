from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Comment, UserVerification
from .utils import send_verification_email
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect


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


class UserVerificationAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'userverification_actions',
    )
    readonly_fields = (
        'user',
        'expires_at',
        'userverification_actions',
    )

    def send_email(self, request, verification_id, *args, **kwargs):
        host = request.build_absolute_uri(reverse('registration_page'))
        obj = self.get_object(request, verification_id)
        try:
            send_verification_email(host, obj.verification_code, obj.user.email)
            self.message_user(request, 'Email notification has been sent successfully')
        except Exception as e:
            self.message_user(request, f'Error during sending email {str(e)}', level=messages.ERROR)

        redirect_url = reverse('admin:%s_%s_change' % self.get_model_info(),
                      args=[obj.pk],
                      current_app=self.admin_site.name)

        return HttpResponseRedirect(redirect_url)

    def get_model_info(self):
        # module_name is renamed to model_name in Django 1.8
        app_label = self.model._meta.app_label
        try:
            return (app_label, self.model._meta.model_name,)
        except AttributeError:
            return (app_label, self.model._meta.module_name,)

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        custom_urls = [
            url(
                r'^(?P<verification_id>.+)/sendemail/$',
                self.admin_site.admin_view(self.send_email),
                name='%s_%s_sendemail' % info
            )
        ]

        return custom_urls + urls

    def userverification_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Resend email notification</a>&nbsp;',
            reverse('admin:%s_%s_sendemail' % self.get_model_info(), args=[obj.pk])
        )

    userverification_actions.short_description = 'Verification Actions'
    userverification_actions.allow_tags = True


admin.site.register(UserVerification, UserVerificationAdmin)
