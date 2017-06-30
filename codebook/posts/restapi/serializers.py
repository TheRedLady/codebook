from rest_framework import serializers

from ..models import (
    Question,
    Answer,
    Comment,
    Vote,
    Tag
)
from profiles.restapi.serializers import UserSerializer, AuthorSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'tag', 'occurrences', 'is_trending')
        read_only_fields = ('id', 'occurrences', 'is_trending')


class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('author', 'title', 'content', 'tags')


class UpdateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'author', 'title', 'content', 'tags', 'votes')
        read_only_fields = ('id', 'author', 'votes')


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Question
        fields = ('id', 'author', 'title', 'votes', 'content', 'created', 'tags', 'is_popular')


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ('voted_by__get_full_name', 'question__title', 'vote')


class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('author', 'question', 'content')


class UpdateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'author', 'question', 'content', 'votes')
        read_only_fields = ('id', 'author', 'question', 'votes')


class AnswerSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    question = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'author', 'question', 'content', 'votes', 'is_top_answer')
        read_only_fields = ('id', 'author', 'question', 'votes', 'question', 'is_top_answer')

    def get_question(self, obj):
        return {
            'id': obj.question.id,
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
    author = UserSerializer()
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'answer', 'author', 'content')

    def get_answer(self, obj):
        return {
            'id': obj.answer.id,
            'title': obj.answer.content
        }