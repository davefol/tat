from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class ClassificationTaskGroup(models.Model):
    name = models.CharField(max_length=256)
    table_class_options = ArrayField(models.CharField(max_length=256))


class ClassificationTask(models.Model):
    name = models.CharField(max_length=256)
    table_html = models.TextField()
    table_class = models.CharField(max_length=256, blank=True)
    completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True)  # Create your models here.
    group = models.ForeignKey(ClassificationTaskGroup, on_delete=models.CASCADE)
