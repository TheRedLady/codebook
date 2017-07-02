from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Question, Tag


class QuestionView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'posts/question.html'


class TagView(LoginRequiredMixin, generic.DetailView):
    model = Tag
    slug_field = 'tag'
    slug_url_kwarg = 'tag'
    template_name = 'posts/tag.html'


class QuestionsList(generic.ListView):
    queryset = Question.objects.all()
    template_name = 'posts/questions_list.html'


class PopularQuestionsList(generic.ListView):
    queryset = Question.get_popular()
    template_name = 'posts/popular_questions_list.html'


class LatestQuestionsList(generic.ListView):
    queryset = Question.get_latest()
    template_name = 'posts/latest_questions_list.html'


class TagsList(generic.ListView):
    queryset = Tag.objects.order_by('tag')
    template_name = 'posts/tags_list.html'


class TrendingTagsList(generic.ListView):
    queryset = Tag.get_trending()
    template_name = 'posts/trending_tags_list.html'
