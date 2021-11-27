import time
from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    ClassificationTaskAnnotateForm,
    ClassificationTaskGroupAddTaskForm,
    ClassificationTaskGroupCreateForm,
)
from .models import ClassificationTask, ClassificationTaskGroup


@dataclass
class TaskType:
    name: str
    url: str


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.type == "ADMIN"  # type: ignore


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "tasks/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_types"] = [
            TaskType("Classification", "classification"),
        ]
        return context


class ClassificationTaskGroupListView(LoginRequiredMixin, ListView):
    model = ClassificationTaskGroup

    def get_queryset(self):
        if self.request.user.type == "ADMIN":  # type: ignore
            return ClassificationTaskGroup.objects.all()
        else:
            return ClassificationTaskGroup.objects.prefetch_related(
                Prefetch(
                    "classificationtask_set",
                    queryset=ClassificationTask.objects.filter(
                        Q(completed_by=self.request.user) | Q(completed=False)
                    ),
                )
            )


class ClassificationTaskGroupCreateView(
    AdminRequiredMixin, SuccessMessageMixin, FormView
):
    form_class = ClassificationTaskGroupCreateForm
    template_name = "tasks/classificationtaskgroup_form.html"
    success_url = reverse_lazy("tasks:classification_tasks")
    sucess_message = "Classification task group successfully created"

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            task_group = ClassificationTaskGroup(
                name=form.cleaned_data["name"],
                table_class_options=form.cleaned_data["table_class_options"],
            )
            task_group.save()
            files = request.FILES.getlist("html_tables")
            timestamp = int(time.time())
            for i, f in enumerate(files):
                name = f"{timestamp}:{i:05d}"
                table_html = f.read()
                ClassificationTask(
                    name=name, table_html=table_html, group=task_group
                ).save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ClassificationTaskGroupAddTasksView(
    AdminRequiredMixin, SuccessMessageMixin, FormView
):
    form_class = ClassificationTaskGroupAddTaskForm
    template_name = "tasks/classificationtaskgroup_add_tasks.html"
    success_url = reverse_lazy("tasks:classification_tasks")
    success_message = "Classification tasks successfully added to group"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_group = get_object_or_404(ClassificationTaskGroup, pk=self.kwargs["pk"])
        context["task_group"] = task_group
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            task_group = get_object_or_404(
                ClassificationTaskGroup, pk=self.kwargs["pk"]
            )
            timestamp = int(time.time())
            files = request.FILES.getlist("html_tables")
            for i, f in enumerate(files):
                name = f"{timestamp}:{i:05d}"
                table_html = f.read()
                ClassificationTask(
                    name=name, table_html=table_html.decode("utf-8"), group=task_group
                ).save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ClassificationTaskDeleteView(AdminRequiredMixin, DeleteView):
    model = ClassificationTask
    success_url = reverse_lazy("tasks:classification_tasks")


class ClassificationTaskGroupDeleteView(DeleteView):
    model = ClassificationTaskGroup
    success_url = reverse_lazy("tasks:classification_tasks")


class ClassificationTaskGroupEditView(UpdateView):
    model = ClassificationTaskGroup
    success_url = reverse_lazy("tasks:classification_tasks")
    fields = ["name", "table_class_options"]
    template_name_suffix = "_edit"


class ClassificationTaskAnnotateFormView(
    LoginRequiredMixin, SuccessMessageMixin, FormView
):
    form_class = ClassificationTaskAnnotateForm
    template_name = "tasks/classificationtask_annotate.html"
    success_url = reverse_lazy("tasks:classification_tasks")
    success_message = "Task Complete: Table successfully classified"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        classification_task = get_object_or_404(
            ClassificationTask, pk=self.kwargs["pk"]
        )
        kwargs["table_class_options"] = classification_task.group.table_class_options
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        classification_task = get_object_or_404(
            ClassificationTask, pk=self.kwargs["pk"]
        )
        context["table_html"] = classification_task.table_html
        return context

    def form_valid(self, form):
        classification_task = get_object_or_404(
            ClassificationTask, pk=self.kwargs["pk"]
        )
        classification_task.table_class = form.cleaned_data["table_class"]
        classification_task.completed = True
        classification_task.completed_by = self.request.user
        classification_task.completed_at = datetime.now()
        classification_task.save()
        return super().form_valid(form)
