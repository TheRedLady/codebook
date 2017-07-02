from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.filters import DjangoFilterBackend, OrderingFilter

from ..models import Profile
from .permissions import UserPermission
from .serializers import (
    ProfileSerializer,
    CreateProfileSerializer,
    UpdateProfileSerializer,
)
from posts.restapi.serializers import QuestionSerializer, AnswerSerializer


def get_follow_status(user, profile):
    if user.user_id == profile.user_id:
        return False
    return profile in user.follows.all()


class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [UserPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['user__email', 'user__first_name', 'user__last_name', 'reputation', 'follows']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProfileSerializer
        if self.action == 'retrieve':
            return ProfileSerializer
        if self.action == 'update':
            return UpdateProfileSerializer
        return ProfileSerializer

    @detail_route(methods=['get', 'post'])
    def follow(self, request, pk=None):
        profile = self.get_object()
        profile_data = ProfileSerializer(profile, context={'request': request}).data
        current_user_profile = Profile.objects.get(user_id=self.request.user.id)
        following = get_follow_status(current_user_profile, profile)
        if request.method == 'GET':
            profile_data['following'] = following
            return Response(profile_data)
        if request.method == 'POST':
            if not following:
                current_user_profile.follows.add(profile)
                current_user_profile.save()
                following = True
            profile_data['following'] = following
            return Response(profile_data)

    @detail_route(methods=['get', 'post'])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        current_user_profile = Profile.objects.get(user_id=self.request.user.id)
        profile_data = ProfileSerializer(profile, context={'request': request}).data
        following = get_follow_status(current_user_profile, profile)
        if request.method == 'GET':
            profile_data['following'] = following
            return Response(profile_data)
        if request.method == 'POST':
            if following:
                current_user_profile.follows.remove(profile)
                current_user_profile.save()
                following = False
            profile_data['following'] = following
            return Response(profile_data)

    @detail_route(methods=['get'])
    def questions(self, request, pk=None):
        user = self.get_object().user
        questions = user.questions.all().order_by('-created')
        page = self.paginate_queryset(questions)
        if page is not None:
            serializer = QuestionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def answers(self, request, pk=None):
        user = self.get_object().user
        answers = user.answers.all().order_by('-created')
        page = self.paginate_queryset(answers)
        if page is not None:
            serializer = AnswerSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = AnswerSerializer(answers, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def feed(self, request, pk=None):
        profile = self.get_object()
        follows = [profile.user for profile in profile.follows.all()]
        questions = [question for followee in follows for question in followee.questions.all() if
                     question.was_published_recently]
        answers = [answer for followee in follows for answer in followee.answers.all() if
                     answer.was_published_recently]
        response = dict()
        response['questions'] = QuestionSerializer(questions, many=True, context={'request': request}).data
        response['answers'] = AnswerSerializer(answers, many=True, context={'request': request}).data
        return Response(response)
