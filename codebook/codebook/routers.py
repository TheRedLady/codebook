from rest_framework.routers import DefaultRouter

from profiles.restapi.views import ProfileViewSet
from posts.restapi.views import (
    QuestionViewSet,
    AnswerViewSet,
    CommentViewSet,
    TagViewSet
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, base_name='profile')
router.register(r'questions', QuestionViewSet, base_name='question')
router.register(r'answers', AnswerViewSet, base_name='answer')
router.register(r'comments', CommentViewSet, base_name='comment')
router.register(r'tags', TagViewSet, base_name='tag')
