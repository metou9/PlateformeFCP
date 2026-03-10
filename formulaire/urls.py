from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Accueil (protégé)
    path('', views.accueil, name='accueil'),
    
    # Formulaires (protégés)
    path('nouveau/', views.nouveau_sous_projet, name='nouveau_sous_projet'),
    path('liste/', views.liste_sous_projets, name='liste_sous_projets'),
    path('detail/<int:pk>/', views.detail_sous_projet, name='detail_sous_projet'),
    
    # APIs (publiques)
    path('api/get-moughataas/', views.get_moughataas, name='get_moughataas'),
    path('api/get-communes/', views.get_communes, name='get_communes'),
]