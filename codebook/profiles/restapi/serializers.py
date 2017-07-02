from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import MyUser, Profile
from ..utils import perform_reputation_check


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
        ]
        extra_kwargs = {'id': {'read_only': True}, 'email': {'read_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='profiles:profile-detail')
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'full_name', 'url']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class CreateProfileSerializer(serializers.ModelSerializer):

    user = CreateUserSerializer()

    class Meta:
        model = Profile
        fields = [
            'user',
            'follows'
        ]

    def create(self, validated_data):
        new_user = CreateUserSerializer().create(validated_data.pop('user'))
        new_profile = Profile.objects.get(user_id=new_user.id)
        new_profile.save()
        return new_profile


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    reputation = serializers.CharField(max_length=8, read_only=True)
    follows = FollowSerializer(read_only=True, many=True)
    url = serializers.HyperlinkedIdentityField(view_name='profiles:profile-detail')
    questions_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    followed_by = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'url',
            'user',
            'reputation',
            'follows',
            'questions_count',
            'answers_count',
            'followed_by'
        ]

    def get_questions_count(self, obj):
        return obj.user.questions.count()

    def get_answers_count(self, obj):
        return obj.user.answers.count()

    def get_followed_by(self, obj):
        return obj.profile_set.count()


class UpdateProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = Profile
        fields = [
            'user',
            'reputation',
            'follows',
        ]

    def validate_follows(self, value):
        if self.instance in value:
            raise serializers.ValidationError(_('User cannot follow self'))
        return value

    def validate_reputation(self, value):
        if value != perform_reputation_check(self.instance.user):
            raise serializers.ValidationError(_('Selected reputation is not valid for this user'))
        return value

    def update(self, instance, validated_data):
        UserSerializer().update(instance.user, validated_data.pop('user'))
        instance.reputation = validated_data.get('reputation', instance.reputation)
        if validated_data['follows']:
            instance.follows.add(*validated_data['follows'])
        instance.save()
        return instance


class AuthorSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='profiles:profile-detail')
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = [
            'id',
            'email',
            'url',
            'full_name',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()
