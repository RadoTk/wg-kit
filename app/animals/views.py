from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from .forms import AnimalForm
from .models import Animal
from django.http import HttpResponseForbidden



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from .forms import AnimalForm
from .models import Animal

@method_decorator(login_required, name='dispatch')
class AnimalCreateView(View):
    template_name = 'animals/animal_form.html'

    def get(self, request):
        form = AnimalForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AnimalForm(request.POST, request.FILES)  # important ici
        if form.is_valid():
            animal = form.save(commit=False)
            animal.owner = request.user
            animal.save()
            form.save_m2m()  # si besoin (pas dans ton cas mais bon)
            return redirect('animals:animal_detail', pk=animal.pk)
        return render(request, self.template_name, {'form': form})


@login_required
def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    # Security: only owner or staff can view sensitive medical info
    can_view_sensitive = (animal.owner == request.user) or request.user.is_staff
    return render(request, 'animals/animal_detail.html', {'animal': animal, 'can_view_sensitive': can_view_sensitive})

@method_decorator(login_required, name='dispatch')
class AnimalUpdateView(View):
    # Exemple basique
    def get(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        if animal.owner != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Vous n'avez pas la permission.")
        form = AnimalForm(instance=animal)
        return render(request, 'animals/animal_form.html', {'form': form})

    def post(self, request, pk):
        animal = get_object_or_404(Animal, pk=pk)
        if animal.owner != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Vous n'avez pas la permission.")
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('animals:animal_detail', pk=animal.pk)
        return render(request, 'animals/animal_form.html', {'form': form})
