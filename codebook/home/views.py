from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model


from .forms import SignUpForm


MyUser = get_user_model()


def home(request):
    if request.user.is_authenticated():
        return render(request, 'home/feed.html', {})
    else:
        return render(request, 'home/welcome.html', {})


@csrf_protect
def sign_up(request):
    registered = False
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            registered = True
    else:
        form = SignUpForm()
    return render(request, 'home/signup.html', {'form': form, 'registered': registered})
