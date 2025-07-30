from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (CustomUserCreationForm, LoginForm, 
                    PasswordResetForm, SetPasswordForm)
from django.contrib.auth.views import (LoginView, PasswordResetView, 
                                       PasswordResetDoneView, PasswordResetConfirmView, 
                                       PasswordResetCompleteView, LogoutView as DjangoLogoutView)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('accounts:login')  # We'll define this URL shortly
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        # Default login
        response = super().form_valid(form)

        # Check "Remember Me"
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)  # Session expires on browser close
        else:
            self.request.session.set_expiry(1209600)  # 2 weeks

        return response

class LogoutView(DjangoLogoutView):
    http_method_names = ['get', 'post']


class PasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset.html'
    extra_context = {'stage': 'done'}

class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stage'] = 'confirm'
        return context

class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset.html'
    extra_context = {'stage': 'complete'}


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {
        'user': request.user
    })

