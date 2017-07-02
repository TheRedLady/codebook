from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Question, Vote, Answer
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

    def test_create_question(self):
        user = MyUser.objects.first()
        data = {
            'title': 'This is a test question',
            'content': 'This is test content',
            'author': user.id,
        }

        self.client.force_authenticate(user=user)
        url = reverse('restapi:question-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)


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

    def test_get_vote_for_question(self):
        question = Question.objects.first()
        user = MyUser.objects.first()
        self.client.force_authenticate(user=user)
        url = reverse('restapi:question-vote', args=(question.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['vote'], None)

        user.vote_for_question(question, Vote.UP)

        question = Question.objects.first()
        user = MyUser.objects.first()
        self.client.force_authenticate(user=user)
        url = reverse('restapi:question-vote', args=(question.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(response.data['vote'], Vote.UP)


class AnswerTests(APITestCase):

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

    def test_create_answer(self):
        user = MyUser.objects.first()
        question = Question.objects.first()
        data = {
            'question': question.id,
            'content': 'This is test content',
            'author': user.id,
        }

        self.client.force_authenticate(user=user)
        url = reverse('restapi:answer-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 1)

    def test_vote_for_answer(self):
        question = Question.objects.first()
        user = MyUser.objects.first()
        answer = Answer.objects.create(
            question=question,
            content='answer',
            author=user
        )
        self.client.force_authenticate(user=user)
        url = reverse('restapi:answer-upvote', args=(answer.id,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote, Vote.UP)

        url = reverse('restapi:answer-downvote', args=(question.id,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().vote, Vote.DOWN)
        print(answer.votes)

    def test_get_vote_for_answer(self):
        question = Question.objects.first()
        user = MyUser.objects.first()
        answer = Answer.objects.create(
            question=question,
            content='answer',
            author=user
        )
        self.client.force_authenticate(user=user)
        url = reverse('restapi:answer-vote', args=(answer.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['vote'], None)

        user.vote_for_answer(answer, Vote.UP)

        url = reverse('restapi:answer-vote', args=(answer.id,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(response.data['vote'], Vote.UP)


