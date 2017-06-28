from __future__ import unicode_literals
from collections import Counter

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    '''
    Should be moved to core.models (if there are enough models for that app)
    '''
    created = models.DateTimeField(_('date published'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Question(TimeStampedModel):
    '''
    null is false by default
    '''
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('questions'))
    question_title = models.CharField(_('title'), max_length=150)
    question_content = models.TextField(_('content'), max_length=5000, editable=True)
    votes = models.IntegerField(_('votes'), default=0)
    tags = models.ManyToManyField('Tag', related_name='questions', blank=True)

    def __str__(self):
        return "'{}' by {}".format(self.question_title, self.author.get_full_name())

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Question, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.id})

    @classmethod
    def get_latest(cls):
        return cls.objects.order_by('-created')[:100]

    @classmethod
    def get_popular(cls):
        pass

    @property
    def answers_count(self):
        return self.answers.all().count()

    @property
    def is_popular(self):
        pass
'''
    @staticmethod
    def add_vote(set_of_questions, user):
        for question in set_of_questions:
            try:
                Vote.objects.get(voted_by=user, question=question)
                question.voted_for_by_user = True
            except Vote.DoesNotExist:
                question.voted_for_by_user = False
        return set_of_questions
'''


@python_2_unicode_compatible
class Tag(models.Model):
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
        tag_counts = Counter(latest_tags).most_common(5)
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
    is_trending.short_description = 'Trending'


@python_2_unicode_compatible
class Answer(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('answers'))
    content = models.TextField(_('content'), max_length=5000, editable=True)
    votes = models.IntegerField(_('number of votes'), default=0)
    question = models.ForeignKey(Question, related_name=_('answers'))

    def __str__(self):
        return 'Answer by {} to "{}"'.format(self.author.get_full_name(), self.question.question_title)

    @property
    def is_top_answer(self):
        pass


class Comment(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('comments'))
    answer = models.ForeignKey(Answer, related_name=_('comments'))
    content = models.TextField(_('content'), max_length=1000, editable=True)

    def __str__(self):
        return 'Comment by {} to {}'.format(self.author.get_full_name(), self.answer)
