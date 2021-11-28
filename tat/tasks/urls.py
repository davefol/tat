from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from .api import views as api_views

api_router = routers.DefaultRouter()
api_router.register(
    r"classification_tasks",
    api_views.ClassificationTaskViewSet,
    basename="classification_task",
)
api_router.register(
    r"classification_task_groups",
    api_views.ClassificationTaskGroupViewSet,
    basename="classification_task_group",
)

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
    path("api/", include(api_router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth-token/", obtain_auth_token),
]
