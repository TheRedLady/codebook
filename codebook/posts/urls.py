from django.conf.urls import url


from . import views


urlpatterns = [
    url(r'^question/(?P<pk>[0-9]+)/$', views.QuestionView.as_view(), name='question-detail'),
    url(r'^tag/(?P<tag>[-\w]+)/$', views.TagView.as_view(), name='tag-detail'),
    url(r'^questions/$', views.QuestionsList.as_view(), name='questions-list'),
    url(r'^questions/popular/$', views.PopularQuestionsList.as_view(), name='popular-questions'),
    url(r'^questions/latest/$', views.LatestQuestionsList.as_view(), name='latest-questions'),
    url(r'^tags/$', views.TagsList.as_view(), name='tags-list'),
    url(r'^tags/trending/$', views.TrendingTagsList.as_view(), name='trending-tags'),
]
