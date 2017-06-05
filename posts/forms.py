from django import forms
from posts.models import Comment
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.urlresolvers import reverse_lazy
from posts.validators import check_user_exists, check_username_exists
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions, StrictButton


class RegistrationForm(forms.Form):

    email = forms.CharField(required=True, validators=[validate_email, check_user_exists])
    username = forms.CharField(required=True, validators=[check_username_exists])
    password = forms.CharField(required=True, widget=forms.PasswordInput(), validators=[validate_password])
    password_confirmation = forms.CharField(widget=forms.PasswordInput())
    birthday = forms.DateField(required=False)
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password != password_confirmation:
            msg = "Passwords must match!"
            self.add_error("password_confirmation", msg)


class PostSearchForm(forms.Form):

    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    keyword = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        if not any([cleaned_data[i] for i in cleaned_data]):
            self.add_error(None, 'Search criteria is not specified')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('post_list_search')
        self.helper.layout = Layout(
            'country',
            'city',
            'keyword',
            Submit('search', 'Search', css_class="btn-default")
        )


class LoginForm(forms.Form):

    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_email(self):
        return self.cleaned_data['email'].lower()


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)
