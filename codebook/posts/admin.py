from django.contrib import admin

from .models import Question, Answer, Tag, Comment


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1


class TagInline(admin.TabularInline):
    model = Tag
    extra = 3


class QuestionModelAdmin(admin.ModelAdmin):
    list_display = ['question_title', 'author', 'created', 'votes', 'answers_count']
    list_filter = ['created']
    fieldsets = [
        ('Question', {'fields': ['author', 'created', 'question_title', 'question_content', 'tags']})
    ]
    readonly_fields = ('created',)
    search_fields = ['question_title', 'author__email']
    inlines = [AnswerInline]
    filter_horizontal = ('tags',)

    class Meta:
        model = Question


class AnswerModelAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'question', 'votes']
    list_filter = ['author']
    fieldsets = [
        ('Answer', {'fields': ['author', 'question', 'content', 'votes']})
    ]
    readonly_fields = ('created',)
    search_fields = ['question__question_title', 'author__email', 'content']

    class Meta:
        model = Answer


class QuestionInline(admin.TabularInline):
    model = Question.tags.through
    verbose_name = 'Question'
    verbose_name_plural = 'Questions'


class TagModelAdmin(admin.ModelAdmin):
    list_display = ['tag', 'occurrences', 'is_trending']
    fieldsets = [
        ('Tag', {'fields': ['tag']})
    ]
    search_fields = ['tag']
    inlines = [QuestionInline]

    class Meta:
        model = Tag


class CommentModelAdmin(admin.ModelAdmin):
    list_display = ['content', 'author', 'answer', 'created']
    fieldsets = [
        ('Comment', {'fields': ['answer', 'author', 'content']})
    ]
    readonly_fields = ('created',)
    search_fields = ['content', 'author__email', 'answer__content']

    class Meta:
        model = Comment


admin.site.register(Question, QuestionModelAdmin)
admin.site.register(Answer, AnswerModelAdmin)
admin.site.register(Tag, TagModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
