from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import password_validation
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError, FieldError
from django.utils.translation import gettext_lazy as _

from .utils import generate_random_username, perform_reputation_check
from posts.models import Vote


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, first_name, last_name,
                     **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = MyUser(email=email, first_name=first_name, last_name=last_name,
                      **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, first_name, last_name, password=None,
                    **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, first_name, last_name, **extra_fields)


class MyUser(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': "A user with that email address already exists.",
        }
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyUserManager()

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        self.username = generate_random_username()
        self.full_clean()
        super(MyUser, self).save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def get_absolute_url(self):
        return reverse('profiles:profile-detail', kwargs={'pk': self.id})

    def vote_for_question(self, question, vote):
        if vote not in (Vote.UP, Vote.DOWN):
            raise FieldError(_('Invalid value for field "Vote"'))
        try:
            vote_object = Vote.objects.get(voted_by=self, question=question)
            if vote_object.vote != vote:
                vote_object.vote = vote
                vote_object.save()
        except Vote.DoesNotExist:
            Vote.objects.create(voted_by=self, question=question, vote=vote)

    def vote_for_answer(self, answer, vote):
        if vote not in (Vote.UP, Vote.DOWN):
            raise FieldError(_('Invalid value for field "Vote"'))
        try:
            vote_object = Vote.objects.get(voted_by=self, answer=answer)
            if vote_object.vote != vote:
                vote_object.vote = vote
                vote_object.save()
        except Vote.DoesNotExist:
            Vote.objects.create(voted_by=self, answer=answer, vote=vote)


@python_2_unicode_compatible
class Profile(models.Model):
    AMATEUR = 'amateur'
    SEASONED = 'seasoned'
    TOP_USER = 'topuser'
    GURU = 'guru'
    REPUTATION_CHOICES = (
        (AMATEUR, _('Amateur')),
        (SEASONED, _('Seasoned')),
        (TOP_USER, _('Top User')),
        (GURU, _('Guru')),
    )
    reputation = models.CharField(
        max_length=8,
        choices=REPUTATION_CHOICES,
        default=AMATEUR
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    follows = models.ManyToManyField('Profile', symmetrical=False, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Profile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('profiles:profile', kwargs={'pk': self.user_id})

    def clean_fields(self, exclude=None):
        super(Profile, self).clean_fields(exclude=exclude)
        if self in self.follows.all():
            raise ValidationError({'follows': _('User cannot follow self')})
        if perform_reputation_check(self.user) != self.reputation:
            raise ValidationError({'reputation': _('Selected reputation level has not been reached')})
