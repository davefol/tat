import io
import itertools
import re
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime

import lxml.html
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ClassificationTaskAnnotateForm, ClassificationTaskContextForm
from .models import ClassificationTask, ClassificationTaskGroup, HTMLDocument, HTMLTable


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
                    "tasks",
                    queryset=ClassificationTask.objects.filter(
                        Q(completed_by=self.request.user) | Q(completed=False)
                    ),
                )
            )


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


class HTMLTableContextView(DetailView):
    model = HTMLTable
    template_name = "tasks/html_table_context.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        num_el_before = self.request.GET.get("before") or 5
        num_el_after = self.request.GET.get("after") or 0
        num_el_before = int(num_el_before)
        num_el_after = int(num_el_after)

        # Get entire html and select the table element
        raw_html = self.object.source_document.html
        root = lxml.html.fromstring(raw_html.encode())
        table_el = root.xpath(self.object.xpath)[0]

        # build up an html fragment from the table
        # and the surrounding elements
        html_fragment = b""
        for el in itertools.islice(
            table_el.itersiblings(preceding=True), num_el_before
        ):
            el.set("class", "faded")
            html_fragment = lxml.html.tostring(el) + html_fragment

        html_fragment += lxml.html.tostring(table_el)

        for el in itertools.islice(
            table_el.itersiblings(preceding=False), num_el_after
        ):
            el.set("class", "faded")
            html_fragment += lxml.html.tostring(el)

        context["html_fragment"] = html_fragment.decode()
        return context


def nearest_el_with_siblings(el):
    if any(filter(el_text, el.itersiblings(preceding=False))) or any(
        filter(el_text, el.itersiblings(preceding=True))
    ):
        return el
    return nearest_el_with_siblings(el.getparent())


def el_non_ix_child(el):
    if el.getparent().tag in ["nonnumeric", "continuation"]:
        return el_non_ix_child(el.getparent())
    return el


def el_text(el):
    try:
        return any("".join(el.itertext()).strip())
    except ValueError:
        return False


def el_unset_height_inline_style(el):
    try:
        style = el.attrib["style"]
        style = re.sub(r"(height:[^;]*;)", lambda x: "/*" + x.group(1) + "*/", style)
        el.attrib["style"] = style
    except KeyError:
        pass
    return el


class ClassificationTaskAnnotateFormView(
    LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, FormView
):
    form_class = ClassificationTaskAnnotateForm
    template_name = "tasks/classificationtask_annotate.html"
    success_message = "Task Complete: Table successfully classified"

    def test_func(self):
        self.object = get_object_or_404(ClassificationTask, pk=self.kwargs["pk"])
        return (
            self.request.user.type == "ADMIN"
            or self.request.user == self.object.completed_by  # type: ignore
            or not self.object.completed_by
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        classification_task = get_object_or_404(
            ClassificationTask, pk=self.kwargs["pk"]
        )
        kwargs["table_class_options"] = classification_task.group.table_class_options
        kwargs["initial"] = {"table_class": classification_task.table_class}
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        num_el_before = (
            self.request.GET.get("before")
            or self.request.user.html_table_context_before
        )
        num_el_after = (
            self.request.GET.get("after") or self.request.user.html_table_context_after
        )
        num_el_before = int(num_el_before)
        num_el_after = int(num_el_after)
        self.request.user.html_table_context_before = num_el_before
        self.request.user.html_table_context_after = num_el_after
        self.request.user.save()

        self.object = get_object_or_404(ClassificationTask, pk=self.kwargs["pk"])

        # Get entire html and select the table element
        raw_html = self.object.html_table.source_document.html
        root = lxml.html.fromstring(raw_html.encode())
        table_el = root.xpath(self.object.html_table.xpath)[0]
        # table_el = nearest_el_with_siblings(table_el)
        table_el = nearest_el_with_siblings(table_el)
        table_el.attrib["id"] = "classification_target"

        # build up an html fragment from the table
        # and the surrounding elements
        html_fragment = b""
        for el in itertools.islice(
            table_el.itersiblings(preceding=True), num_el_before
        ):
            try:
                el.set("class", "faded")
                if el.tag == "table":
                    el = el_unset_height_inline_style(el)
            except TypeError:
                pass
            html_fragment = lxml.html.tostring(el, pretty_print=True) + html_fragment

        table_el.set("class", "box")
        table_el = el_unset_height_inline_style(table_el)
        html_fragment += lxml.html.tostring(table_el, pretty_print=True)

        for el in itertools.islice(
            table_el.itersiblings(preceding=False), num_el_after
        ):
            try:
                el.set("class", "faded")
                if el.tag == "table":
                    el = el_unset_height_inline_style(el)
            except TypeError:
                pass
            html_fragment += lxml.html.tostring(el, pretty_print=True)

        context["self_url"] = reverse_lazy(
            "tasks:classification_task_annotate", kwargs={"pk": self.object.id}
        )
        context["context_form"] = ClassificationTaskContextForm(
            initial={"before": num_el_before, "after": num_el_after}
        )
        context["html_fragment"] = html_fragment.decode()
        context["name"] = self.object.name
        context["html_source"] = self.object.html_table.source_document.source_url
        context["xpath"] = self.object.html_table.xpath
        context["table_class"] = self.object.table_class
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

    def get_success_url(self):
        next_task = ClassificationTask.objects.filter(completed=False).first()
        if next_task is None:
            return reverse("tasks:classifcation_tasks")
        else:
            return reverse(
                "tasks:classification_task_annotate", kwargs={"pk": next_task.id}
            )


def download_all_data(request):
    if request.user.is_authenticated and request.user.type == "ADMIN":
        models = [
            ("html_documents", HTMLDocument),
            ("html_tables", HTMLTable),
            ("classification_task_groups", ClassificationTaskGroup),
            ("classification_tasks", ClassificationTask),
        ]
        buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(buffer, "w")
        for collection_name, model_class in models:
            data = serializers.serialize("json", model_class.objects.all())
            zip_file.writestr(f"{collection_name}.json", data)
        zip_file.close()
        response = HttpResponse(buffer.getvalue())
        response["Content-Type"] = "application/x-zip-compressed"
        response[
            "Content-Disposition"
        ] = f"inline; filename=data_{int(time.time())}.zip"
        return response
    else:
        raise PermissionDenied


def classification_group_download(request, pk):
    if request.user.is_authenticated and request.user.type == "ADMIN":
        classification_task_group = get_object_or_404(ClassificationTaskGroup, pk=pk)
        classification_tasks = classification_task_group.tasks
        html_tables = set()
        for classification_task in classification_tasks.all():
            html_tables.add(classification_task.html_table)
        html_documents = set()
        for html_table in html_tables:
            html_documents.add(html_table.source_document)
        buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(buffer, "w")
        data = serializers.serialize("jsonl", [classification_task_group])
        zip_file.writestr("classification_task_group.json", data)
        data = serializers.serialize("jsonl", classification_tasks.all())
        zip_file.writestr("classification_tasks.json", data)
        data = serializers.serialize("jsonl", html_tables)
        zip_file.writestr("html_tables.json", data)
        data = serializers.serialize("jsonl", html_documents)
        zip_file.writestr("html_documents.json", data)
        zip_file.close()
        response = HttpResponse(buffer.getvalue())
        response["Content-Type"] = "application/x-zip-compressed"
        response[
            "Content-Disposition"
        ] = f"inline; filename={slugify(classification_task_group.name)}_{int(time.time())}.zip"
        return response
    else:
        raise PermissionDenied
