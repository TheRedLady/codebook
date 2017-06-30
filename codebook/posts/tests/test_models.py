import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Question, Answer, Comment, Tag
from profiles.models import MyUserManager


class QuestionModelTests(TestCase):

    def setUp(self):
        self.user = MyUserManager().create_user(
            email='tom@gmail.com',
            first_name='Tom',
            last_name='Hanks'
        )
        Question.objects.create(
            author=self.user,
            title='How to do I write unit tests in Django',
            content='I need to write these tests :/'
        )

    def test_was_published_recently(self):
        question = Question.objects.first()
        self.assertTrue(question.was_published_recently)
        question.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        self.assertFalse(question.was_published_recently)

    def test_answers_count(self):
        question = Question.objects.first()
        self.assertEqual(question.answers_count, 0)
        Answer.objects.create(author=self.user, content='You should use Djangos TestCase', question=question)
        self.assertEqual(list(question.answers.all()), [Answer.objects.first()])
        self.assertEqual(question.answers_count, 1)

    def test_is_popular_with_recent_question(self):
        question = Question.objects.first()
        question.votes = Question.POPULAR_QUESTION_VOTES/3 + 1
        self.assertTrue(question.is_popular)
        question.votes = Question.POPULAR_QUESTION_VOTES/3 - 1
        self.assertFalse(question.is_popular)

    def test_is_popular_with_old_question_with_votes(self):
        question = Question.objects.first()
        question.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        question.votes = Question.POPULAR_QUESTION_VOTES + 1
        Answer.objects.create(author=self.user, content='You should use Djangos TestCase', question=question)
        self.assertTrue(question.is_popular)
        answer = Answer.objects.first()
        answer.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        answer.save()
        self.assertFalse(question.is_popular)
        Answer.objects.first().delete()
        self.assertFalse(question.is_popular)

    def test_is_popular_with_old_question_without_votes(self):
        question = Question.objects.first()
        question.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        question.votes = Question.POPULAR_QUESTION_VOTES - 1
        Answer.objects.create(author=self.user, content='You should use Djangos TestCase', question=question)
        self.assertFalse(question.is_popular)

    def test_get_popular(self):
        self.assertEqual(Question.get_popular(), [])
        question = Question.objects.first()
        question.votes = Question.POPULAR_QUESTION_VOTES + 1
        question.save()
        self.assertEqual(Question.get_popular(), [Question.objects.first()])

    def test_get_latest(self):
        question = Question.objects.first()
        self.assertEqual(list(Question.get_latest()), [Question.objects.first()])
        question.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        question.save()
        self.assertEqual(list(Question.get_latest()), [])


class AnswerModelTests(TestCase):

    def setUp(self):
        self.user = MyUserManager().create_user(
            email='jenny@gmail.com', first_name='Jenny', last_name='Andrews'
        )
        self.question = Question.objects.create(
            author=self.user,
            title='How to do I write tests in Django',
            content='I need to write these tests :/'
        )
        self.answer = Answer.objects.create(
            author=self.user,
            question=self.question,
            content='You should use TestCase.'
        )
        Answer.objects.create(
            author=self.user,
            question=self.question,
            content='You should maybe use pytest.'
        )
        Answer.objects.create(
            author=self.user,
            question=self.question,
            content='How about py mommy?'
        )

    def test_was_published_recently(self):
        self.assertTrue(self.answer.was_published_recently)
        self.answer.created = timezone.now() - datetime.timedelta(days=Answer.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        self.assertFalse(self.answer.was_published_recently)

    def test_is_top_answer(self):
        different_answer = Answer.objects.last()
        self.assertFalse(self.answer.is_top_answer())
        self.assertTrue(different_answer.is_top_answer())
        self.answer.votes = 500
        self.answer.save()
        self.assertTrue(self.answer.is_top_answer())
        different_answer.votes = 500
        different_answer.save()
        self.assertTrue(different_answer.is_top_answer())
        self.assertFalse(self.answer.is_top_answer())


class CommentModelTests(TestCase):

    def setUp(self):
        self.user = MyUserManager().create_user(
            email='jenny@gmail.com', first_name='Jenny', last_name='Andrews'
        )
        self.question = Question.objects.create(
            author=self.user,
            title='How to do I write tests in Django',
            content='I need to write these tests :/'
        )
        self.answer = Answer.objects.create(
            author=self.user,
            question=self.question,
            content='You should use TestCase.'
        )
        self.comment = Comment.objects.create(
            author=self.user,
            answer=self.answer,
            content="That's a very useful answer."
        )
        Comment.objects.create(
            author=self.user,
            answer=self.answer,
            content="I don't agree, py mommy is a lot more helpful."
        )
        Comment.objects.create(
            author=self.user,
            answer=self.answer,
            content="I'd argue in favour of factory boy."
        )


class TagModelTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(tag='testing')
        self.user = MyUserManager().create_user(
            email='jenny@gmail.com',
            first_name='Jenny',
            last_name='Andrews'
        )
        Question.objects.create(
            author=self.user,
            title='How to do I create unit tests in Django',
            content='I need to write these tests :/'
        )
        Question.objects.create(
            author=self.user,
            title='How to do I create dummy data in bulk for testing in Django',
            content='I think I should have used py mommy.'
        )

    def test_add_to_question(self):
        first_q, second_q = Question.objects.all()
        first_q.tags.add(self.tag)
        self.assertEqual(list(first_q.tags.all()), [self.tag])
        new_tag = Tag.objects.create(tag='dummy-data')
        first_q.tags.add(new_tag)
        self.assertEqual(list(first_q.tags.all()), [self.tag, new_tag])
        self.assertEqual(list(second_q.tags.all()), [])
        self.assertEqual(list(self.tag.questions.all()), [first_q])
        self.assertEqual(list(new_tag.questions.all()), [first_q])
        second_q.tags.add(new_tag)
        self.assertEqual(list(new_tag.questions.all()), [first_q, second_q])

    def test_detach_from_question(self):
        new_tag = Tag.objects.create(tag='dummy-data')
        first_q, second_q = Question.objects.all()
        first_q.tags.add(self.tag)
        first_q.tags.add(new_tag)
        second_q.tags.add(new_tag)
        first_q.delete()
        self.assertEqual(list(self.tag.questions.all()), [])
        self.assertEqual(list(new_tag.questions.all()), [second_q])
        second_q.tags.add(self.tag)
        new_tag.delete()
        self.assertEqual(list(second_q.tags.all()), [self.tag])
        second_q.delete()
        self.assertEqual(list(self.tag.questions.all()), [])

    def test_occurrences(self):
        self.assertEqual(self.tag.occurrences, 0)
        for question in Question.objects.all():
            question.tags.add(self.tag)
        self.assertEqual(self.tag.occurrences, 2)
        Question.objects.first().delete()
        self.assertEqual(self.tag.occurrences, 1)
        Question.objects.first().delete()
        self.assertEqual(self.tag.occurrences, 0)

    def test_is_trending(self):
        new_tag = Tag.objects.create(tag='dummy-data')
        first_q, second_q = Question.objects.all()
        first_q.tags.add(self.tag)
        first_q.tags.add(new_tag)
        second_q.tags.add(self.tag)
        self.assertTrue(self.tag.is_trending())
        first_q.tags.remove(self.tag)
        second_q.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        second_q.save()
        self.assertFalse(self.tag.is_trending())

    def test_get_trending(self):
        new_tag = Tag.objects.create(tag='dummy-data')
        first_q, second_q = Question.objects.all()
        first_q.tags.add(self.tag)
        first_q.tags.add(new_tag)
        second_q.tags.add(self.tag)
        self.assertEqual(Tag.get_trending(), [self.tag, new_tag])
        first_q.tags.remove(self.tag)
        second_q.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        second_q.save()
        self.assertEqual(Tag.get_trending(), [new_tag])
        first_q.created = timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA + 1)
        first_q.save()
        self.assertEqual(Tag.get_trending(), [])

