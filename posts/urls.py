"""posts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from posts.views import RegistrationView, VerificationCompleteView, \
    LoginView, LogoutView, HomePageView, PostView, PostSearchView, CommentView, LikePostView

urlpatterns = [
    url(r'^$', ensure_csrf_cookie(HomePageView.as_view()), name='home_page'),
    url(r'^search/$', login_required(PostSearchView.as_view()), name='post_list_search'),
    url(r'^registration/$', RegistrationView.as_view(), name='registration_page'),
    url(r'^registration/([0-9a-f]{32})$', VerificationCompleteView.as_view(), name='verification_page'),
    url(r'^login/', LoginView.as_view(), name='login_page'),
    url(r'^logout/', login_required(LogoutView.as_view(), redirect_field_name=None), name='logout_page'),
    url(r'^post/(?P<slug>[\w-]+)/$', login_required(PostView.as_view(), redirect_field_name=None), name='post_detail'),
    url(r'^post/(?P<slug>[\w-]+)/comment/$', login_required(CommentView.as_view(), redirect_field_name=None), name='post_add_comment'),
    url(r'^admin/', admin.site.urls),
    url(r'^like_post/', login_required(LikePostView.as_view(), redirect_field_name=None), name='like_post'),
]
