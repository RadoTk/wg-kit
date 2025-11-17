from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django import forms
from .models import Confession, ConfessionTag, ConfessionCategory


class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['text', 'tone', 'category']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Share your confession...'}),
            'tone': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Auto-generate pseudonym for anonymous confessions
        self.instance.pseudo = self._generate_pseudonym()

    def _generate_pseudonym(self):
        import random
        import string
        # Generate a random anonymous name
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        return f"Anonyme_{random_suffix}"


def confession_list(request):
    """
    Display list of confessions based on filters
    """
    confessions = Confession.objects.filter(is_public=True).order_by('-created_at')

    # Apply filters if provided
    tone_filter = request.GET.get('tone')
    if tone_filter:
        confessions = confessions.filter(tone=tone_filter)

    category_filter = request.GET.get('category')
    if category_filter:
        confessions = confessions.filter(category_id=category_filter)

    # Get all tags and categories for filter options
    categories = ConfessionCategory.objects.all()

    context = {
        'confessions': confessions,
        'categories': categories,
        'selected_tone': tone_filter,
        'selected_category': category_filter,
    }
    return render(request, 'confession/confession_list.html', context)


def confession_create(request):
    """
    Handle confession creation
    """
    if request.method == 'POST':
        form = ConfessionForm(request.POST)
        if form.is_valid():
            confession = form.save(commit=False)
            # Set as public by default for confessions
            confession.is_public = True
            confession.save()
            messages.success(request, 'Your confession has been submitted successfully!')
            return redirect('confession_list')
    else:
        form = ConfessionForm()

    return render(request, 'confession/confession_form.html', {'form': form})


def confession_detail(request, pk):
    """
    Display a single confession
    """
    confession = get_object_or_404(Confession, pk=pk)
    return render(request, 'confession/confession_detail.html', {'confession': confession})


@require_http_methods(["POST"])
def confession_anonymous_create(request):
    """
    Handle anonymous confession creation via AJAX
    """
    text = request.POST.get('text', '').strip()
    tone = request.POST.get('tone', 'neutre')
    category_id = request.POST.get('category')

    if not text:
        return JsonResponse({'success': False, 'error': 'Confession text is required'}, status=400)

    try:
        confession = Confession.objects.create(
            text=text,
            tone=tone,
            is_public=True,
            category_id=category_id if category_id else None
        )

        return JsonResponse({
            'success': True,
            'message': 'Confession submitted successfully!',
            'confession_id': confession.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def confession_category_list(request, category_id):
    """
    Display confessions for a specific category
    """
    category = get_object_or_404(ConfessionCategory, id=category_id)
    confessions = Confession.objects.filter(
        category=category,
        is_public=True
    ).order_by('-created_at')

    context = {
        'category': category,
        'confessions': confessions
    }
    return render(request, 'confession/confession_list.html', context)
