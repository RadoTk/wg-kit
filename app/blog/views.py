from django.shortcuts import render
from .models import BlogPage, BlogPageDetail

def blog_page_full_detail(request, slug):
    # Récupère l'article de blog en utilisant son slug
    blog_page = BlogPage.objects.live().filter(slug=slug).first()

    if blog_page:
        # Si l'article existe, passe-le au template
        return render(request, 'blog/blog_page_detail.html', {'blog_page': blog_page})

    # Si l'article n'existe pas, renvoie une erreur ou redirection
    return render(request, '404.html')
