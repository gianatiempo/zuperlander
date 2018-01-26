# *-* coding:utf-8 *-*
import json

from django import forms
from django.core.validators import MaxValueValidator

from landinator.forms import widgets as custom_widgets

max_value_validator = MaxValueValidator(0)


class CheckOtherField(forms.fields.MultiValueField):
    widget = custom_widgets.CheckOtherWidget

    def __init__(self, *args, **kwargs):
        list_fields = [forms.fields.BooleanField(required=False),
                       forms.fields.CharField()]
        super(CheckOtherField, self).__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return json.dumps(values)

