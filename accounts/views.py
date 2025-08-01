from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetDoneView as DjangoPasswordResetDoneView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
    LogoutView as DjangoLogoutView,
)
from .forms import (
    CustomUserCreationForm,
    LoginForm,
    PasswordResetForm,
    SetPasswordForm,
)
from .utils import calculate_profile_completeness


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


class LoginView(DjangoLoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(1209600)
        return response


class LogoutView(DjangoLogoutView):
    http_method_names = ['get', 'post']


class PasswordResetView(DjangoPasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'accounts/password_reset.html'
    extra_context = {'stage': 'done'}


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'accounts/password_reset.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stage'] = 'confirm'
        return context


class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = 'accounts/password_reset.html'
    extra_context = {'stage': 'complete'}
    success_url = reverse_lazy('accounts:dashboard')


@login_required
def dashboard_view(request):
    user = request.user
    meter = calculate_profile_completeness(user)
    tips = []
    if not user.first_name:
        tips.append("Add your first name")
    if not user.last_name:
        tips.append("Add your last name")
    if not user.email:
        tips.append("Verify your email address")
    if not user.bio:
        tips.append("Write a short bio about yourself")
    if not user.avatar:
        tips.append("Upload a profile picture")
    context = {
        'user': user,
        'meter': meter,
        'tips': tips,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
@require_POST
def update_profile_view(request):
    user = request.user
    user.first_name = request.POST.get('first_name', '').strip()
    user.last_name = request.POST.get('last_name', '').strip()
    user.bio = request.POST.get('bio', '').strip()
    avatar = request.FILES.get('avatar')
    if avatar:
        user.avatar = avatar
    user.save()
    return JsonResponse({
        "status": "success",
        "first_name": user.first_name,
        "username": user.username,
        "avatar_url": user.avatar.url if user.avatar else "",
    })


@login_required
@require_POST
def delete_account_view(request):
    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('accounts:login')
