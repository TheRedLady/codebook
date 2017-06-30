from . import models


def update_votes(vote, obj, created=False):
    if created:
        obj.votes += 1 if vote == models.Vote.UP else -1
        obj.save()
        return
    obj.votes += 2 if vote == models.Vote.UP else -2
    obj.save()
