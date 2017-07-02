from __future__ import unicode_literals
from collections import Counter
import datetime

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .utils import update_votes


class TimeStampedModel(models.Model):
    PUBLISHED_RECENTLY_TIMEDELTA = 14
    created = models.DateTimeField(_('date published'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Question(TimeStampedModel):
    POPULAR_QUESTION_VOTES = 400

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('questions'))
    title = models.CharField(_('title'), max_length=150)
    content = models.TextField(_('content'), max_length=5000, editable=True)
    votes = models.IntegerField(_('votes'), default=0)
    tags = models.ManyToManyField('Tag', related_name='questions', blank=True)

    def __str__(self):
        return "'{}' by {}".format(self.title, self.author.get_full_name())

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Question, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.id})

    @classmethod
    def get_latest(cls):
        return cls.objects.filter(
            created__gte=timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA)
        )

    @classmethod
    def get_popular(cls):
        objects = cls.objects.all()
        objects = [question for question in objects if question.is_popular]
        return objects

    @property
    def answers_count(self):
        return self.answers.all().count()

    @property
    def was_published_recently(self):
        return self.created > timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA)

    @property
    def is_popular(self):
        """Determines whether question is popular.
        A question is popular if it has been published recently and has more than a certain amount of votes
        (a predetermined constant) or has answers published in the last seven days and has more than a
         certain amount of votes (again predetermined constant).
        """
        answers = self.answers.filter(
            created__gte=timezone.now() - datetime.timedelta(days=Question.PUBLISHED_RECENTLY_TIMEDELTA)
        )
        return (self.votes > Question.POPULAR_QUESTION_VOTES and answers.count() != 0) \
            or (self.was_published_recently and (self.votes >= Question.POPULAR_QUESTION_VOTES/3))


@python_2_unicode_compatible
class Answer(TimeStampedModel):
    PUBLISHED_RECENTLY_TIMEDELTA = 7

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('answers'))
    content = models.TextField(_('content'), max_length=5000, editable=True)
    votes = models.IntegerField(_('number of votes'), default=0)
    question = models.ForeignKey(Question, related_name=_('answers'))

    def __str__(self):
        return 'Answer by {} to "{}"'.format(self.author.get_full_name(), self.question.title)

    @property
    def was_published_recently(self):
        return self.created > timezone.now() - datetime.timedelta(days=Answer.PUBLISHED_RECENTLY_TIMEDELTA)

    def is_top_answer(self):
        """Determines whether answer is top answer for the associated question.
        Top answer for a question is the most recently published one and with the most votes.
        """
        most_votes = self.question.answers.all().aggregate(models.Max('votes'))['votes__max']
        top_answers = self.question.answers.filter(votes=most_votes).order_by('-created')
        return self == top_answers.first()

    is_top_answer.boolean = True
    is_top_answer.short_description = _('Top Answer?')


class Comment(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('comments'))
    answer = models.ForeignKey(Answer, related_name=_('comments'))
    content = models.TextField(_('content'), max_length=1000, editable=True)

    def __str__(self):
        return 'Comment by {} to {}'.format(self.author.get_full_name(), self.answer)


@python_2_unicode_compatible
class Tag(models.Model):
    TRENDING_TAGS_COUNT = 20

    tag = models.CharField(
        _('tag'),
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$',
                message='Tag must be alphanumerics separated by a dash'
            ),
        ]
    )

    def __str__(self):
        return "Tag #{}".format(self.tag)

    def get_absolute_url(self):
        return reverse('posts:tag', kwargs={'tag': self.tag})

    @classmethod
    def get_trending(cls):
        latest_questions = Question.get_latest()
        latest_tags = [tag for question in latest_questions for tag in question.tags.all()]
        tag_counts = Counter(latest_tags).most_common(Tag.TRENDING_TAGS_COUNT)
        for pair in tag_counts:
            pair[0].occurrences_count = pair[1]
        return [pair[0] for pair in tag_counts]

    @property
    def occurrences(self):
        return self.questions.all().count()

    def is_trending(self):
        latest_tags = Tag.get_trending()
        return self in latest_tags

    is_trending.boolean = True
    is_trending.short_description = _('Trending')


class Vote(models.Model):
    UP = 'up'
    DOWN = 'down'
    VOTE_CHOICES = (
        (UP, _('Up')),
        (DOWN, _('Down'))
    )
    vote = models.CharField(
        max_length=8,
        choices=VOTE_CHOICES,
        default=UP
    )
    question = models.ForeignKey(Question, null=True, blank=True)
    answer = models.ForeignKey(Answer, null=True, blank=True)
    voted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes')

    class Meta:
        unique_together = (
            ('voted_by', 'question'),
            ('voted_by', 'answer')
        )

    def __init__(self, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)
        self.__original_vote = self.vote

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """
        Override save method to update question or answer votes. Alternative to signals.
        """
        obj = self.question if self.question is not None else self.answer
        if self.__original_vote != self.vote:
            update_votes(self.vote, obj, self.pk is None)
        super(Vote, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_vote = self.vote

    def __str__(self):
        return "{}vote by {}".format(self.vote, self.voted_by)
