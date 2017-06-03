from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from posts.utils import get_expire_date


class User(AbstractUser):
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=255, null=False, blank=True)
    city = models.CharField(max_length=255, null=False, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


class Post(models.Model):
    title = models.CharField(max_length=140, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    body = models.TextField()
    likes = models.ManyToManyField(User, related_name='likes_set', blank=True)
    created_dt = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='+')

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', None, {'slug': self.slug})

    @models.permalink
    def get_comment_url(self):
        return ('post_add_comment', None, {'slug': self.slug})

    @property
    def total_likes(self):
        cnt = self.likes.count()
        return "" if cnt == 0 else cnt

    def is_liked(self, user):
        return self.likes.filter(id=user.id).exists()

    class Meta:
        ordering = ('-created_dt', )


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments")
    body = models.TextField()
    created_dt = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    class Meta:
        ordering = ('-created_dt', )


class UserVerification(models.Model):
    user = models.ForeignKey(User)
    verification_code = models.CharField(max_length=50, default=uuid.uuid4)
    expires_at = models.DateTimeField(default=get_expire_date)
