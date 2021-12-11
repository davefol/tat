from django import forms


class ClassificationTaskAnnotateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        table_class_options = kwargs.pop("table_class_options")
        super().__init__(*args, **kwargs)
        self.fields["table_class"] = forms.ChoiceField(
            choices=[(s, s) for s in table_class_options],
            widget=forms.RadioSelect,
        )


class ClassificationTaskContextForm(forms.Form):
    before = forms.IntegerField(min_value=0, max_value=100)
    after = forms.IntegerField(min_value=0, max_value=100)
