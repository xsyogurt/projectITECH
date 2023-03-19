from django import forms


class BootStrap:
    bootstrap_exclude_fields = []

    """
    Loop through all the fields in the ModelForm, setting attributes to each field. 
    If there are attributes in the field, keep the original attributes, if there are no attributes, then add them.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():

            if name in self.bootstrap_exclude_fields:
                continue

            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label
                }


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass
