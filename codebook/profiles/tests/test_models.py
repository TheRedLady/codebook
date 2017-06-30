from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import MyUserManager, MyUser, Profile
from ..utils import perform_reputation_check


test_email = 'elizabeth@gmail.com'
test_first_name = 'Elizabeth'
test_last_name = 'Taylor'
test_password = 'abcd1234'


class MyUserManagerModelTests(TestCase):

    def test_create_user(self):
        new_user = MyUserManager().create_user(email=test_email, first_name=test_first_name,
                                               last_name=test_last_name)
        self.assertEqual(new_user.first_name, test_first_name)
        self.assertEqual(new_user.last_name, test_last_name)
        self.assertEqual(new_user.email, test_email)
        self.assertIs(new_user.is_active, True)
        self.assertIs(new_user.is_staff, False)
        self.assertIs(new_user.is_superuser, False)
        self.assertEqual(new_user, MyUser.objects.first())

    def test_create_superuser(self):
        new_user = MyUserManager().create_superuser(email=test_email, password=test_password,
                                                    first_name=test_first_name, last_name=test_last_name)
        self.assertEqual(new_user.first_name, test_first_name)
        self.assertEqual(new_user.last_name, test_last_name)
        self.assertEqual(new_user.email, test_email)
        self.assertIs(new_user.is_active, True)
        self.assertIs(new_user.is_staff, True)
        self.assertIs(new_user.is_superuser, True)
        self.assertEqual(new_user, MyUser.objects.first())


class MyUserModelTests(TestCase):
    pass


class ProfileModelTests(TestCase):

    def setUp(self):
        MyUserManager().create_user(email='anna@gmail.com', first_name='Anna', last_name='Tomlin')
        MyUserManager().create_user(email='george@gmail.com', first_name='George', last_name='Thomas')

    def test_create_profile(self):
        new_user = MyUserManager().create_user(email=test_email,
                                               first_name=test_first_name,
                                               last_name=test_last_name)
        profile = Profile.objects.get(user_id=new_user.id)
        self.assertEqual(profile.user, new_user)

    def test_profile_follow_self(self):
        profile = Profile.objects.first()
        self.assertRaises(ValidationError, profile.follows.add(profile))

    def test_profile_follow_others(self):
        anna = Profile.objects.get(user_id=1)
        george = Profile.objects.get(user_id=2)
        anna.follows.add(george)
        self.assertEqual(list(anna.follows.all()), [george])

    def test_profile_reputation_check(self):
        user_profile = Profile.objects.first()
        self.assertEqual(user_profile.reputation, Profile.AMATEUR)
        self.assertEqual(perform_reputation_check(user_profile.user), Profile.AMATEUR)
