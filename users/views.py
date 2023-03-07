from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views


class LogoutAndRedirect(auth_views.LogoutView):
    """Logout and redirect to the homepage."""

    def get_next_page(self):
        messages.success(self.request, 'You have been logged out.')
        return '/login'


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! Now you can login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})
