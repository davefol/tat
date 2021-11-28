from rest_framework import permissions, viewsets

from ..models import ClassificationTask, ClassificationTaskGroup
from .serializers import ClassificationTaskGroupSerializer, ClassificationTaskSerializer


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
