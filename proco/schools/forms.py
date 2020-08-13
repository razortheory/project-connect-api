from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit

from proco.locations.models import Country


class ImportSchoolsCSVForm(forms.Form):
    country = forms.ModelChoiceField(Country.objects.all())
    csv_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Field('country'),
            Field('csv_file'),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button'),
            ),
        )
