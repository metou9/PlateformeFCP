from django.urls import path
from . import views

urlpatterns = [
    path('nouveau/', views.nouveau_sous_projet, name='nouveau_sous_projet'),
    path('liste/', views.liste_sous_projets, name='liste_sous_projets'),
    path('detail/<int:pk>/', views.detail_sous_projet, name='detail_sous_projet'),

     # APIs pour le chargement dynamique (AJAX)
    
    path('api/get-moughataas/', views.get_moughataas, name='get_moughataas'),  # ← tiret, pas underscore
    path('api/get-communes/', views.get_communes, name='get_communes'),        # ← tiret, pas underscore
    
]