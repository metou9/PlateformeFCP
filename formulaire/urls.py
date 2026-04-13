from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # AUTHENTIFICATION
    # ============================================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============================================
    # ACCUEIL (protégé)
    # ============================================
    path('', views.accueil, name='accueil'),
    # Suppression d'un sous-projet
    path('supprimer/<int:pk>/', views.supprimer_sous_projet, name='supprimer_sous_projet'),
    
    # ============================================
    # FORMULAIRES PRINCIPAUX (protégés)
    # ============================================
    # Étape 1: Informations générales du sous-projet
    path('nouveau/', views.nouveau_sous_projet, name='nouveau_sous_projet'),
    path('save-sous-projet/', views.save_sous_projet, name='save_sous_projet'),
    
    # Étape 2: Financement - Infrastructures
    path('financement-infrastructure/', views.financement_infrastructure, name='financement_infrastructure'),
    path('save-infrastructure/', views.save_infrastructure, name='save_infrastructure'),
    
    # Étape 3: Financement - Équipements
    path('financement-equipement/', views.financement_equipement, name='financement_equipement'),
    path('save-equipement/', views.save_equipement, name='save_equipement'),
    
    # Étape 4: Financement - Intrants
    path('financement-intrant/', views.financement_intrant, name='financement_intrant'),
    path('save-intrant/', views.save_intrant, name='save_intrant'),
    
    # Étape 5: Financement - Fonctionnement
    path('financement-fonctionnement/', views.financement_fonctionnement, name='financement_fonctionnement'),
    path('save-fonctionnement/', views.save_fonctionnement, name='save_fonctionnement'),
    
    # Étape 6: Financement - Services
    path('financement-services/', views.financement_services, name='financement_services'),
    path('save-service/', views.save_service, name='save_service'),
    
    # Étape 7: Réalisations et Passifs
    path('realisation-passif/', views.realisation_passif, name='realisation_passif'),
    path('save-realisation-passif/', views.save_realisation_passif, name='save_realisation_passif'),
    
    # Liste et détail des sous-projets
    path('liste/', views.liste_sous_projets, name='liste_sous_projets'),
    path('detail/<int:pk>/', views.detail_sous_projet, name='detail_sous_projet'),
    
    # ============================================
    # API NON PROTÉGÉES (pour chargement dynamique)
    # ============================================
    path('api/get-moughataas/', views.get_moughataas, name='get_moughataas'),
    path('api/get-communes/', views.get_communes, name='get_communes'),
    path('api/get-paysages/', views.get_paysages, name='get_paysages'),
    path('api/get-villages/', views.get_villages, name='get_villages'),
    path('preselection-automatique/', views.preselection_automatique, name='preselection_automatique'),
]