from . import models


def update_votes(vote, obj, created=False):
    obj.votes = obj.votes + (1 if vote == models.Vote.UP else -1)
    obj.save()
