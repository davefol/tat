from django import forms
from django.contrib.postgres.forms import SimpleArrayField


class ClassificationTaskGroupCreateForm(forms.Form):
    name = forms.CharField(max_length=256)
    table_class_options = SimpleArrayField(forms.CharField(max_length=256))
    html_tables = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


class ClassificationTaskGroupAddTaskForm(forms.Form):
    html_tables = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


class ClassificationTaskAnnotateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        table_class_options = kwargs.pop("table_class_options")
        super().__init__(*args, **kwargs)
        self.fields["table_class"] = forms.ChoiceField(
            choices=[(s, s) for s in table_class_options],
            widget=forms.RadioSelect,
        )
