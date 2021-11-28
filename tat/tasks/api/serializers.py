from rest_framework import serializers

from ..models import ClassificationTask, ClassificationTaskGroup


class ClassificationTaskSerializer(serializers.HyperlinkedModelSerializer):
    group = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="tasks:classification_task_group-detail",
        lookup_field="uuid",
    )
    completed_by = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name="user:detail"
    )

    class Meta:
        model = ClassificationTask
        fields = [
            "name",
            "table_html",
            "table_class",
            "completed",
            "completed_by",
            "created_at",
            "updated_at",
            "group",
            "uuid",
        ]
        lookup_field = "uuid"


class ClassificationTaskGroupSerializer(serializers.HyperlinkedModelSerializer):
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="tasks:classification_task-detail",
        lookup_field="uuid",
    )

    class Meta:
        model = ClassificationTaskGroup
        fields = [
            "name",
            "table_class_options",
            "uuid",
            "tasks",
        ]
        lookup_field = "uuid"
