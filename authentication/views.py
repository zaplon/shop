import json
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.contrib.auth import authenticate, login, logout
from .admin import UserCreationForm
from authentication.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse, HttpResponseRedirect,render, render_to_response, RequestContext


@csrf_exempt
class RegistrationView(CreateView):
    form_class = UserCreationForm
    model = User

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.set_password(User.objects.make_random_password())
        obj.save()

        return redirect('accounts:register-password')

    def form_invalid(self, form):
        if 'source' in form.data and form.data['source'] == 'checkout':
            return render_to_response('checkout.djhtml', {'creationForm': form,
                                      'products_in_cart': True}, context_instance=RequestContext(self.request))


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            if 'source' in request.POST:
                return HttpResponseRedirect("/" + request.POST['source'] + "/")
            else:
                return HttpResponseRedirect("/zarejestruj/")
    else:
        form = UserCreationForm()
    if 'source' in request.POST and request.POST['source'] == 'checkout':
        return render_to_response('checkout.djhtml', {'creationForm': form,
                                                      'products_in_cart': True},
                                  context_instance=RequestContext(request))
    else:
        return render(request, "registerView.html", {
            'form': form,
        })



@csrf_exempt
def loginView(request):
    user = authenticate(email=request.POST['email'], password=request.POST['password'])
    if user is not None:
        # the password verified for the user
        if user.is_active:
            login(request, user)
            if 'source' in request.POST:
                return HttpResponseRedirect(request.POST['source'])
            else:
                return HttpResponse(json.dumps({'success': True}))
        else:
            if 'source' in request.POST:
                return HttpResponseRedirect(request.POST['source'])
            else:
                return HttpResponse(json.dumps({'success': False,
                                                'message': "The password is valid, but the account has been disabled!"}))
    else:
        # the authentication system was unable to verify the username and password
        return HttpResponse(json.dumps({'success': False, 'message': "The username and password were incorrect."}))


def logoutView(request):
    logout(request)
    url = request.META['HTTP_REFERER'].split('/')[-1]
    return HttpResponseRedirect('/' + url)