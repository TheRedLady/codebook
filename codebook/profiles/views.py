from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile


class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'profiles/profile.html'


class GoToProfile(LoginRequiredMixin, generic.base.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        kwargs['pk'] = self.request.user.id
        self.url = '/profile/{}/'.format(kwargs['pk'])
        return super(GoToProfile, self).get_redirect_url(*args, **kwargs)
