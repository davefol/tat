from rest_framework import serializers

from ..models import (
    ClassificationTask,
    ClassificationTaskGroup,
    HTMLDocument,
    HTMLTable,
)


class HTMLDocumentSerializer(serializers.HyperlinkedModelSerializer):
    html_tables = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="tasks:html_table-detail",
        lookup_field="uuid",
    )

    class Meta:
        model = HTMLDocument
        fields = ["html", "created_at", "source_url", "uuid", "html_tables"]
        lookup_field = "uuid"


class HTMLTableSerializer(serializers.HyperlinkedModelSerializer):
    source_document = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        queryset=HTMLDocument.objects.all(),
        # view_name="tasks:html_document-detail",
        slug_field="uuid",
    )

    class Meta:
        model = HTMLTable
        fields = ["source_document", "xpath", "uuid"]


class ClassificationTaskSerializer(serializers.HyperlinkedModelSerializer):
    group = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        queryset=ClassificationTaskGroup.objects.all(),
        # view_name="tasks:classification_task_group-detail",
        slug_field="uuid",
    )
    completed_by = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        # queryset=get_user_model().objects.all(),
        slug_field="username",
    )
    html_table = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        queryset=HTMLTable.objects.all(),
        # view_name="tasks:html_table-detail",
        slug_field="uuid",
    )

    class Meta:
        model = ClassificationTask
        fields = [
            "name",
            "html_table",
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
