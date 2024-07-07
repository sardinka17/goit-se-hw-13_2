from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy

from users.forms import SignUpForm


class SignUpView(View):
    template_name = 'users/signup.html'
    form_class = SignUpForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f'Registration successfully')

            return redirect(to='quotes:index')

        return render(request, self.template_name, {'form': form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    success_message = 'An email with instructions to reset your password has been sent to %(email)s.'
    subject_template_name = 'users/password_reset_subject.txt'
