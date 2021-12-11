import urllib.parse

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import (
    ClassificationTask,
    ClassificationTaskGroup,
    HTMLDocument,
    HTMLTable,
)
from .serializers import (
    ClassificationTaskGroupSerializer,
    ClassificationTaskSerializer,
    HTMLDocumentSerializer,
    HTMLTableSerializer,
)


class HTMLDocumentViewSet(viewsets.ModelViewSet):
    queryset = HTMLDocument.objects.all()
    serializer_class = HTMLDocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "uuid"


class HTMLDocumentRetrieveSourceUrl(generics.RetrieveAPIView):
    queryset = HTMLDocument.objects.all()
    serializer_class = HTMLDocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # lookup_url_kwarg = "source_url"
    lookup_field = "source_url"

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {
            self.lookup_field: urllib.parse.unquote(self.kwargs[lookup_url_kwarg])
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class HTMLTableViewSet(viewsets.ModelViewSet):
    queryset = HTMLTable.objects.all()
    serializer_class = HTMLTableSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "uuid"


@api_view(["GET"])
def html_table_retrieve_source_url_xpath(request):
    data = {
        "source_document": request.data.get("source_document"),
        "xpath": request.data.get("xpath"),
    }
    for k, v in data.items():
        if v is None:
            return Response(
                {"Must not be null": [k]}, status=status.HTTP_400_BAD_REQUEST
            )

    try:
        html_table = HTMLTable.objects.get(**data)
    except HTMLTable.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = HTMLTableSerializer(html_table, many=False)
        return Response(serializer.data)


class ClassificationTaskViewSet(viewsets.ModelViewSet):
    queryset = ClassificationTask.objects.all()
    serializer_class = ClassificationTaskSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "uuid"


class ClassificationTaskGroupViewSet(viewsets.ModelViewSet):
    queryset = ClassificationTaskGroup.objects.all()
    serializer_class = ClassificationTaskGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "uuid"


class ClassificatonTaskGroupRetrieveName(generics.RetrieveAPIView):
    queryset = ClassificationTaskGroup.objects.all()
    serializer_class = ClassificationTaskGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "name"

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {
            self.lookup_field: urllib.parse.unquote_plus(self.kwargs[lookup_url_kwarg])
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
