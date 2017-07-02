from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.filters import DjangoFilterBackend, OrderingFilter

from . import serializers
from .permissions import UserPermission, CreateAndViewPermission
from ..models import (
    Question,
    Answer,
    Comment,
    Vote,
    Tag
)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all().order_by('votes')
    permission_classes = [UserPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['author__email', 'author__first_name', 'author__last_name', 'title', 'content']

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateQuestionSerializer
        if self.action == 'update':
            return serializers.UpdateQuestionSerializer
        return serializers.QuestionSerializer

    @detail_route(methods=['post'])
    def upvote(self, request, pk=None):
        question = self.get_object()
        request.user.vote_for_question(question, Vote.UP)
        serializer = serializers.VoteSerializer(Vote.objects.get(voted_by=request.user, question=question))
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def downvote(self, request, pk=None):
        question = self.get_object()
        request.user.vote_for_question(question, Vote.DOWN)
        serializer = serializers.VoteSerializer(Vote.objects.get(voted_by=request.user, question=question))
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def vote(self, request, pk=None, vote=None):
        question = self.get_object()
        try:
            vote_object = Vote.objects.get(voted_by=request.user, question=question)
            return Response({
                'status': True,
                'question_id': question.id,
                'message': '{} has {}voted answer with id {}'.format(request.user, vote_object.vote, question.id),
                'vote': vote_object.vote,
                'total_votes': question.votes
            })
        except Vote.DoesNotExist:
            return Response({
                'status': False,
                'question_id': question.id,
                'message': '{} has not voted for answer with id {}'.format(request.user, question.id),
                'vote': None,
                'total_votes': question.votes
            })

    @list_route(methods=['get'])
    def popular(self, request):
        popular_questions = Question.get_popular()

        page = self.paginate_queryset(popular_questions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(popular_questions, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def latest(self, request):
        latest_questions = Question.get_latest()

        page = self.paginate_queryset(latest_questions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(latest_questions, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def answers(self, request, pk=None):
        question = self.get_object()
        answers = question.answers.all().order_by('votes')
        page = self.paginate_queryset(answers)
        if page is not None:
            serializer = serializers.AnswerSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.AnswerSerializer(answers, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    lookup_field = 'tag'
    serializer_class = serializers.TagSerializer
    permission_classes = [CreateAndViewPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['tag']

    @list_route(methods=['get'])
    def trending(self, request):
        trending_tags = Tag.get_trending()

        page = self.paginate_queryset(trending_tags)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(trending_tags, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def questions(self, request, tag=None):
        tag = self.get_object()
        questions = tag.questions.all()
        page = self.paginate_queryset(questions)
        if page is not None:
            serializer = serializers.QuestionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all().order_by('votes')
    permission_classes = [UserPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['question__title', 'author__first_name', 'author__last_name', 'content', 'votes']

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateAnswerSerializer
        if self.action == 'update':
            return serializers.UpdateAnswerSerializer
        return serializers.AnswerSerializer

    @detail_route(methods=['post'])
    def upvote(self, request, pk=None):
        answer = self.get_object()
        request.user.vote_for_answer(answer, Vote.UP)
        serializer = serializers.VoteSerializer(Vote.objects.get(voted_by=request.user, answer=answer))
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def downvote(self, request, pk=None):
        answer = self.get_object()
        request.user.vote_for_answer(answer, Vote.DOWN)
        serializer = serializers.VoteSerializer(Vote.objects.get(voted_by=request.user, answer=answer))
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def vote(self, request, pk=None, vote=None):
        answer = self.get_object()
        try:
            vote_object = Vote.objects.get(voted_by=request.user, answer=answer)
            return Response({
                'status': True,
                'answer_id': answer.id,
                'message': '{} has {}voted answer with id {}'.format(request.user, vote_object.vote, answer.id),
                'vote': vote_object.vote,
                'total_votes': answer.votes
            })
        except Vote.DoesNotExist:
            return Response({
                'status': False,
                'answer_id': answer.id,
                'message': '{} has not voted for answer with id {}'.format(request.user, answer.id),
                'vote': None,
                'total_votes': answer.votes
            })

    @detail_route(methods=['get'])
    def comments(self, request, pk=None):
        answer = self.get_object()
        comments = answer.comments.all()
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [UserPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ['content', 'author__first_name', 'author__last_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateCommentSerializer
        if self.action == 'update':
            return serializers.UpdateCommentSerializer
        return serializers.CommentSerializer
