'''
Reasons for not using this: too much common ground with AbstractUser, redundancy
class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
        error_messages={
            'unique': 'A user with that email address already exists.',
        }
    )
    is_admin = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

'''
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import password_validation
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import generate_random_username, perform_reputation_check


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
        return reverse('profiles:profile', kwargs={'pk': self.id})


@python_2_unicode_compatible
class Profile(models.Model):
    AMATEUR = 'amateur'
    SEASONED = 'seasoned'
    TOP_USER = 'topuser'
    GURU = 'guru'
    REPURATION_CHOICES = (
        (AMATEUR, 'Amateur'),
        (SEASONED, 'Seasoned'),
        (TOP_USER, 'Top User'),
        (GURU, 'Guru'),
    )
    reputation = models.CharField(
        max_length=8,
        choices=REPURATION_CHOICES,
        default=AMATEUR
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    follows = models.ManyToManyField('Profile', related_name='followed_by',
                                     symmetrical=False, blank=True)

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



