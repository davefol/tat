import uuid as uuid_lib

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class HTMLDocument(models.Model):
    html = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    source_url = models.URLField(unique=True)
    uuid = models.UUIDField(
        db_index=True, default=uuid_lib.uuid4, editable=False, unique=True
    )


class HTMLTable(models.Model):
    source_document = models.ForeignKey(
        HTMLDocument,
        on_delete=models.CASCADE,
        related_name="html_tables",
        to_field="uuid",
    )
    xpath = models.CharField(
        max_length=256
    )  # where in the source document the classification task is from
    uuid = models.UUIDField(
        db_index=True, default=uuid_lib.uuid4, editable=False, unique=True
    )

    class Meta:
        unique_together = ("xpath", "source_document")


class ClassificationTaskGroup(models.Model):
    name = models.CharField(max_length=256, unique=True)
    table_class_options = ArrayField(models.CharField(max_length=256))
    uuid = models.UUIDField(
        db_index=True, default=uuid_lib.uuid4, editable=False, unique=True
    )


class ClassificationTask(models.Model):
    name = models.CharField(max_length=256)
    uuid = models.UUIDField(
        db_index=True, default=uuid_lib.uuid4, editable=False, unique=True
    )
    table_class = models.CharField(max_length=256, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True)  # Create your models here.
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    html_table = models.ForeignKey(
        HTMLTable,
        on_delete=models.CASCADE,
        related_name="classification_tasks",
        to_field="uuid",
    )
    group = models.ForeignKey(
        ClassificationTaskGroup,
        on_delete=models.CASCADE,
        related_name="tasks",
        to_field="uuid",
    )

    class Meta:
        unique_together = ("html_table", "group")
