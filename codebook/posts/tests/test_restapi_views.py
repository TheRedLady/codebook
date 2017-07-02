from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Question, Vote
from profiles.models import MyUser


class QuestionTests(APITestCase):

    def setUp(self):
        MyUser.objects.create(
            email='george.michael@gmail.com',
            password='test',
            first_name='George',
            last_name='Michael'
        )
        Question.objects.create(
            title='ABC',
            content='DEFG',
            author=MyUser.objects.first()
        )

    def test_vote_for_question(self):
        question = Question.objects.first()
        user = MyUser.objects.first()
        self.client.force_authenticate(user=user)
        url = reverse('restapi:question-upvote', args=(question.id,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote, Vote.UP)

        url = reverse('restapi:question-downvote', args=(question.id,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote, Vote.DOWN)

