# Generated by Django 3.2.9 on 2021-12-11 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0002_auto_20211201_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classificationtask',
            name='completed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classification_tasks', to=settings.AUTH_USER_MODEL),
        ),
    ]
