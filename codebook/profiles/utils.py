from django.utils.crypto import get_random_string


REPUTATION_RANGES = {
    'amateur': {
        'answers': range(0, 50),
        'top_answers': (0, 5)
    },
    'seasoned': {
        'answers': range(50, 150),
        'top_answers': (15, 30)
    },
    'topuser': {
        'answers': range(150, 300),
        'top_answers': (30, 70)
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
    answers_count = answers.count()
    top_answers_count = len([answer for answer in answers if answer.is_top_answer])
    from .models import Profile
    if answers_count in REPUTATION_RANGES['amateur']['answers'] \
            or top_answers_count in REPUTATION_RANGES['amateur']['top_answers']:
        return Profile.AMATEUR
    if answers_count in REPUTATION_RANGES['seasoned']['answers'] \
            or top_answers_count in REPUTATION_RANGES['seasoned']['top_answers']:
        return Profile.SEASONED
    if answers_count in REPUTATION_RANGES['topuser']['answers'] \
            or top_answers_count in REPUTATION_RANGES['topuser']['top_answers']:
        return Profile.TOP_USER
    return Profile.GURU
