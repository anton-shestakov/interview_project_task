from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from posts.models import User, Post, UserVerification, Comment
from posts.forms import RegistrationForm, LoginForm, CommentForm, PostSearchForm
from posts.utils import get_verification_code, send_verification_email
from posts.validators import check_user_exists, check_username_exists


class RegistrationView(View):

    @transaction.atomic
    def post(self, request):

        if request.is_ajax():

            # initialize form for validation
            form = RegistrationForm(request.POST)

            if form.is_valid():
                # add inactive user
                user = User.objects.create(
                    email=form.cleaned_data['email'],
                    password=make_password(form.cleaned_data['password']),
                    username=form.cleaned_data['username'],
                    birthday=form.cleaned_data['birthday'],
                    country=form.cleaned_data['country'],
                    city=form.cleaned_data['city'],
                    is_active=False
                )

                # create verification entry
                verification = UserVerification.objects.create(
                    user=user,
                    verification_code=get_verification_code(user.email)
                )

                # send email with link and code
                host = request.build_absolute_uri()
                send_verification_email(host, verification.verification_code, user.email)

                return JsonResponse({'type': 'success', 'msg': f'''Verification link has been sent to {user.email}.
                                                               Please visit that link to activate your account.'''})

            else:
                # collect error messages and return as JsonResponse
                return JsonResponse({'type': 'error', 'msg': dict([(k, [str(e) for e in v]) for k, v in form.errors.items()])})


class VerificationCompleteView(View):

    @transaction.atomic
    def get(self, request, verification):

        try:
            verification_record = UserVerification.objects.get(verification_code=verification)
        except UserVerification.DoesNotExist:
            messages.error(request, "Verification record not found")
            return redirect('home_page')

        if verification_record.expires_at > timezone.now():
            verification_record.user.is_active = True
            verification_record.user.save()

            # clean verification record
            verification_record.delete()

            messages.info(request, "Your account has been activated. You can now login using email and password.")
            return redirect('home_page')
        else:
            messages.error(request, "Verification record expired!")
            return redirect('home_page')


class LoginView(View):

    def post(self, request):

        if request.is_ajax():
            email = request.POST.get('email').lower()
            password = request.POST.get('password')
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)

                messages.info(request, f'Hello, {request.user.username}!')

                return JsonResponse({'type': 'success', 'msg': f'Hello, {request.user.username}!'})
            else:
                return JsonResponse({'type': 'error', 'msg': 'Invalid email and/or password'})


class LogoutView(View):

    def get(self, request):

        logout(request)

        messages.info(request, "You have been successfully logged out!")

        return redirect('home_page')


class HomePageView(TemplateView):

    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # redirect to PostListView
            view = PostListView.as_view()
            return view(request, *args, **kwargs)
        return super(HomePageView, self).dispatch(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    form_class = PostSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()

        liked_set = self.request.user.likes_set.all()
        for post in context['posts']:
            if post in liked_set:
                post.is_liked_ = True

        return context


class PostSearchView(ListView):
    model = Post
    template_name = 'post_list_search.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):

        filter_keys = {'keyword', 'country', 'city'}

        filters = self.request.GET
        queryset = Post.objects.all()

        for filter_key in filters:
            if filters[filter_key] and filter_key in filter_keys:
                if filter_key == 'keyword':  # body filter
                    queryset = queryset.filter(body__search=filters[filter_key])
                else:  # country/city - User filter
                    d = {f'created_by__{filter_key}__exact': filters[filter_key]}
                    queryset = queryset.filter(**d)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        liked_set = self.request.user.likes_set.all()
        for post in context['posts']:
            if post in liked_set:
                post.is_liked_ = True

        return context


class PostView(View):

    def get(self, request, slug):

        post_ = get_object_or_404(Post, slug=slug)

        # paginate comments
        comments = post_.comments.all()
        page = request.GET.get('page', 1)

        paginator = Paginator(comments, 5)

        try:
            comments_page = paginator.page(page)
        except PageNotAnInteger:
            comments_page = paginator.page(1)
        except EmptyPage:
            comments_page = paginator.page(paginator.num_pages)

        post_.is_liked_ = post_.is_liked(request.user)

        return render(request, 'post_detail.html', {'post': post_,
                                                    'comments': comments_page})


class CommentView(View):

    def post(self, request, slug):

        post_ = get_object_or_404(Post, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.created_by = request.user
            comment.post = post_
            comment.save()

        return redirect(post_.get_absolute_url())


class LikePostView(View):

    # to-do enable csrf
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):

        post_id = request.POST.get('post_id')

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'type': 'error'})

        user_like = post.is_liked(request.user)

        if user_like:
            # remove like
            post.likes.remove(request.user)
        else:
            # add like
            post.likes.add(request.user)

        post.save()

        out_data = {
            'type': 'success',
            'is_liked': post.is_liked(request.user),
            'likes_count': post.total_likes
        }

        return JsonResponse(out_data)
