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
api_router.register(
    r"html_documents", api_views.HTMLDocumentViewSet, basename="html_document"
)
api_router.register(r"html_tables", api_views.HTMLTableViewSet, basename="html_table")

app_name = "tasks"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "classification/",
        views.ClassificationTaskGroupListView.as_view(),
        name="classification_tasks",
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
        r"classification/annotate/(?P<pk>\d+)/$",
        views.ClassificationTaskAnnotateFormView.as_view(),
        name="classification_task_annotate",
    ),
    path(
        r"html_table_context/<int:pk>/",
        views.HTMLTableContextView.as_view(),
        name="html_table_context",
    ),
    path("api/", include(api_router.urls)),
    path(
        "api/html_document_retrieve_source_url/<path:source_url>",
        api_views.HTMLDocumentRetrieveSourceUrl.as_view(),
        name="html_document_retrieve_source_url",
    ),
    path(
        "api/classification_task_group_retrieve_name/<str:name>",
        api_views.ClassificatonTaskGroupRetrieveName.as_view(),
        name="classification_task_group_retrieve_name",
    ),
    path(
        "api/html_table_retrieve_source_url_xpath/",
        api_views.html_table_retrieve_source_url_xpath,
        name="html_table_retrieve_source_url_xpath",
    ),
    path(
        "download_all_data",
        views.download_all_data,
        name="download_all_data",
    ),
    path(
        "classification_group_download/<int:pk>",
        views.classification_group_download,
        name="classification_group_download",
    ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("auth-token/", obtain_auth_token),
]
