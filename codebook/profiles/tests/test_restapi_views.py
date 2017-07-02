from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import MyUser, Profile


class ProfileTests(APITestCase):

    def create_profile(self):
        user1 = MyUser.objects.create(
            email='testuser@gmail.com',
            password='testthis',
            first_name='First',
            last_name='User'
        )
        user2 = MyUser.objects.create(
            email='othertestuser@gmail.com',
            password='testthis',
            first_name='Second',
            last_name='User'
        )
        self.test_user1 = Profile.objects.get(user=user1)
        self.test_user2 = Profile.objects.get(user=user2)

    def test_create_profile(self):
        url = reverse('restapi:profile-list')
        data = {
            'user': {'email': 'testuser@gmail.com',
                     'password': 'testthis',
                     'first_name': 'test',
                     'last_name': 'test'
                     },
            'reputation': 'amateur',
            'follows': []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.get().user.email, 'testuser@gmail.com')

        self.client.login(email='testuser@gmail.com', password='testthis')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        self.create_profile()

        url = reverse('restapi:profile-detail', args=(1,))
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.test_user2.user)
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.create_profile()

        url = reverse('restapi:profile-detail', args=(1,))
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.test_user2.user)
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('restapi:profile-detail', args=(2,))
        response = self.client.put(url, {'user': {'first_name': 'Tesssst'}, 'follows': ['1']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Profile.objects.get(user_id=2).user.first_name, 'Tesssst')

    def test_delete(self):
        self.create_profile()

        url = reverse('restapi:profile-detail', args=(1,))
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.test_user2.user)
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('restapi:profile-detail', args=(2,))
        response = self.client.delete(url, {'user': {}, 'follows': ['1']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_follow(self):
        self.create_profile()

        url = reverse('restapi:profile-follow', args=(1,))
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.test_user2.user)
        url = reverse('restapi:profile-follow', args=(1,))
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], False)

        url = reverse('restapi:profile-follow', args=(2,))
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], False)

        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('restapi:profile-follow', args=(1,))
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.test_user1, Profile.objects.get(user_id=2).follows.all())
        self.assertEqual(response.data['following'], True)

    def test_unfollow(self):
        self.create_profile()

        url = reverse('restapi:profile-unfollow', args=(1,))
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.test_user2.user)
        url = reverse('restapi:profile-follow', args=(1,))
        self.client.post(url, {}, format='json')

        url = reverse('restapi:profile-unfollow', args=(1,))
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], False)
        self.assertNotIn(self.test_user1, Profile.objects.get(user_id=2).follows.all())

        url = reverse('restapi:profile-unfollow', args=(2,))
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following'], False)
