from django.utils.crypto import get_random_string


REPUTATION_RANGES = {
    'amateur': {
        'questions': range(0, 50),
        'answers': range(0, 50)
    },
    'seasoned': {
        'questions': range(50, 100),
        'answers': range(50, 150),
    },
    'topuser': {
        'questions': range(100, 200),
        'answers': range(150, 300),
    }
}
allowed_chars = 'abcdefghtuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def generate_random_username(length=10, allowed_characters=allowed_chars):
    username = get_random_string(length, allowed_characters)
    # import didn't work otherwise
    from .models import MyUser
    try:
        MyUser.objects.get(username=username)
        return generate_random_username(length, allowed_characters)
    except MyUser.DoesNotExist:
        return username


def perform_reputation_check(user):
    answers = user.answers.all()
    answers_count = len([answer for answer in answers if answer.is_top_answer])
    questions = user.questions.all()
    questions_count = len([question for question in questions if question.is_popular])
    from .models import Profile
    if answers_count in REPUTATION_RANGES['amateur']['answers'] \
            or questions_count in REPUTATION_RANGES['amateur']['questions']:
        return Profile.AMATEUR
    if answers_count in REPUTATION_RANGES['seasoned']['answers'] \
            or questions_count in REPUTATION_RANGES['seasoned']['questions']:
        return Profile.SEASONED
    if answers_count in REPUTATION_RANGES['topuser']['answers'] \
            or questions_count in REPUTATION_RANGES['topuser']['questions']:
        return Profile.TOP_USER
    return Profile.GURU
