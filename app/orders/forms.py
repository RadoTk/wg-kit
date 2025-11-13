from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "shopper_first_name",
            "shopper_name",       
            "shopper_email",
            "shopper_address",     
            "shopper_postal_code",
            "shopper_country",
        ]
        labels = {
            "shopper_first_name": "First name",
            "shopper_name": "Name",
            "shopper_email": "E-mail",
            "shopper_address": "Address",
            "shopper_postal_code": "Postal code",
            "shopper_country": "Country",
        }
        widgets = {
            "shopper_first_name": forms.TextInput(attrs={"placeholder": "Enter first name"}),
            "shopper_name": forms.TextInput(attrs={"placeholder": "Enter last name"}),
            "shopper_email": forms.EmailInput(attrs={"placeholder": "Enter email"}),
            "shopper_address": forms.TextInput(attrs={"placeholder": "Street address"}),
            "shopper_postal_code": forms.TextInput(attrs={"placeholder": "Postal code"}),
            "shopper_country": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget

            # Appliquer les classes Bootstrap
            if isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"

            # Ajouter "is-invalid" si le champ a des erreurs
            if self.errors.get(name):
                css_class += " is-invalid"

            # Ajouter la classe au widget
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css_class}".strip()
