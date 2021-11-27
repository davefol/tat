from django.urls import path, re_path

from . import views

app_name = "tasks"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "classification/",
        views.ClassificationTaskGroupListView.as_view(),
        name="classification_tasks",
    ),
    path(
        "classification/create/",
        views.ClassificationTaskGroupCreateView.as_view(),
        name="classification_create",
    ),
    re_path(
        r"classification/edit_task_group/(?P<pk>\d+)/$",
        views.ClassificationTaskGroupEditView.as_view(),
        name="classification_group_edit",
    ),
    re_path(
        r"classification/delete_task_group/(?P<pk>\d+)/$",
        views.ClassificationTaskGroupDeleteView.as_view(),
        name="classification_group_delete",
    ),
    re_path(
        r"classification/delete_task/(?P<pk>\d+)/$",
        views.ClassificationTaskDeleteView.as_view(),
        name="classification_task_delete",
    ),
    re_path(
        r"classification/add_tasks/(?P<pk>\d+)/$",
        views.ClassificationTaskGroupAddTasksView.as_view(),
        name="classification_group_add_tasks",
    ),
    re_path(
        r"classification/annotate/(?P<pk>\d+)/$",
        views.ClassificationTaskAnnotateFormView.as_view(),
        name="classification_task_annotate",
    ),
]
