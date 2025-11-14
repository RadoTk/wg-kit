from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog_index, name='blog_index'),  # Page d'index
    path('blog/<slug:slug>/', views.blog_page_detail, name='blog_page_detail'),  # Page de résumé
    path('blog/<slug:slug>/detail/', views.blog_page_full_detail, name='blog_page_full_detail'),  # Page de détail complète
]
