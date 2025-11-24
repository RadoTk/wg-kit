from django import forms
from wagtail.images.models import Image
from .models import Animal
from django.core.exceptions import ValidationError


class AnimalForm(forms.ModelForm):
    new_photo = forms.ImageField(required=False, label="Photo de l'animal")

    class Meta:
        model = Animal
        fields = [
            'name', 'breed', 'category', 'age_years', 'weight_kg', 'sex',
            'vet_name', 'allergies', 'medical_conditions',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': 150}),
            'breed': forms.TextInput(attrs={'maxlength': 150}),
            'vet_name': forms.TextInput(attrs={'maxlength': 150}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, commit=True):
        animal = super().save(commit=False)
        new_photo_file = self.cleaned_data.get('new_photo')
        if new_photo_file:
            wagtail_image = Image.objects.create(
                title=animal.name + " photo",
                file=new_photo_file,
            )
            animal.photo = wagtail_image
        if commit:
            animal.save()
        return animal
    
    def clean_new_photo(self):
        photo = self.cleaned_data.get('new_photo')

        if photo:
            # Limite taille fichier (ex: 5MB)
            max_size_mb = 5
            if photo.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"Image trop grande (max {max_size_mb}MB).")

            # Limite type mime (jpg, png, gif)
            valid_mime_types = ['image/jpeg', 'image/png', 'image/gif']
            if photo.content_type not in valid_mime_types:
                raise ValidationError("Format non supporté. Utilisez JPG, PNG ou GIF.")
        
        return photo
