from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from app.users.models import Address
from app.orders.models import Country

from django import forms
from app.users.models import Address

from django import forms
from django.contrib.auth.models import User
from app.users.models import UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField(required=False)
    birth_date = forms.DateField(required=False)

    address_line1 = forms.CharField()
    postal_code = forms.CharField()
    city = forms.CharField()
    country = forms.ModelChoiceField(queryset=Country.objects.all())

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=True)

        profile = user.profile
        profile.phone_number = self.cleaned_data["phone_number"]
        profile.birth_date = self.cleaned_data["birth_date"]
        profile.save()

        # Adresse principale
        address = Address.objects.create(
            user=user,
            address_type="shipping",
            full_name=f"{user.first_name} {user.last_name}",
            address_line1=self.cleaned_data["address_line1"],
            postal_code=self.cleaned_data["postal_code"],
            city=self.cleaned_data["city"],
            country=self.cleaned_data["country"],
            is_default=True,
        )

        profile.default_shipping_address = address
        profile.save()

        return user





class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "address_type",
            "full_name",
            "address_line1",
            "address_line2",
            "postal_code",
            "city",
            "country",
            "phone_number",
            "is_default",
        ]



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "birth_date", "gender"]
