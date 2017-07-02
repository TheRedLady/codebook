from django.urls import reverse

from rest_framework import serializers

from ..models import (
    Question,
    Answer,
    Comment,
    Vote,
    Tag
)
from profiles.restapi.serializers import AuthorSerializer


class TagSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='posts:tag-detail', lookup_field='tag')

    class Meta:
        model = Tag
        fields = ('id', 'tag', 'occurrences', 'is_trending', 'url')
        read_only_fields = ('id', 'occurrences', 'is_trending', 'url')


class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'author', 'title', 'content', 'tags')
        read_only_fields = ('id',)


class UpdateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'author', 'title', 'content', 'tags', 'votes')
        read_only_fields = ('id', 'author', 'votes')


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='posts:question-detail')

    class Meta:
        model = Question
        fields = ('id', 'url', 'author', 'title', 'votes', 'content', 'created', 'tags', 'is_popular')


class VoteSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ('question', 'answer', 'voted_by', 'total_votes')

    def get_total_votes(self, obj):
        if obj.question:
            return obj.question.votes
        return obj.answer.votes


class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'author', 'question', 'content')
        read_only_fields = ('id',)


class UpdateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'author', 'question', 'content', 'votes')
        read_only_fields = ('id', 'author', 'question', 'votes')


class AnswerSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    question = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'author', 'question', 'content', 'votes', 'is_top_answer', 'created')
        read_only_fields = ('id', 'author', 'question', 'votes', 'question', 'is_top_answer', 'created')

    def get_question(self, obj):
        return {
            'id': obj.question.id,
            'url': reverse('posts:question-detail', args=(obj.id,)),
            'title': obj.question.title
        }


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'author', 'content', 'votes', 'is_top_answer')


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'answer', 'content')


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'answer', 'content')
        read_only_fields = ('id', 'author', 'answer')


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'answer', 'author', 'content', 'created')

    def get_answer(self, obj):
        return {
            'id': obj.answer.id,
            'title': obj.answer.content
        }