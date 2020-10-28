from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit


class ImportSchoolsCSVForm(forms.Form):
    csv_file = forms.FileField()
    force = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Field('csv_file'),
            Field('force'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button'),
            ),
        )
