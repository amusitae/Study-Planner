from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import RegisterForm, TaskFilterForm, TaskForm
from .models import Task
from .services import get_dashboard_stats, overdue_tasks


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()  # password is hashed by Django
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"stats": get_dashboard_stats(request.user)})


class OwnerTaskMixin(LoginRequiredMixin):
    """Every query is limited to the logged-in user's tasks (data isolation).
    Someone else's task id therefore returns 404, never the data."""

    model = Task

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskListView(OwnerTaskMixin, ListView):
    template_name = "task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        qs = super().get_queryset()
        self.filter_form = TaskFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data["q"]:
                qs = qs.filter(title__icontains=data["q"])
            if data["status"]:
                qs = qs.filter(status=data["status"])
            if data["priority"]:
                qs = qs.filter(priority=data["priority"])
            if data["overdue"]:
                qs = overdue_tasks(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class TaskCreateView(OwnerTaskMixin, CreateView):
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Task added.")
        return super().form_valid(form)


class TaskUpdateView(OwnerTaskMixin, UpdateView):
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task updated.")
        return super().form_valid(form)


class TaskDeleteView(OwnerTaskMixin, DeleteView):
    template_name = "task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task deleted.")
        return super().form_valid(form)


@login_required
@require_POST
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    task.status = Task.Status.COMPLETED
    task.save()
    messages.success(request, "Task marked as completed.")
    return redirect(request.POST.get("next") or "task_list")
