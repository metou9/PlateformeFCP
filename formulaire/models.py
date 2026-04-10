from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password


# ============================================
# 1. MODÈLES DE RÉFÉRENCE (Tables déjà existantes)
# ============================================

class Wilaya(models.Model):
    """Table des wilayas (régions)"""
    code = models.CharField(max_length=10, unique=True, verbose_name="Code de la wilaya")
    nom = models.CharField(max_length=100, verbose_name="Nom de la wilaya")
    
    class Meta:
        verbose_name = "Wilaya"
        verbose_name_plural = "Wilayas"
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class Moughataa(models.Model):
    """Table des moughataas (départements)"""
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name='moughataas', verbose_name="Wilaya")
    code = models.CharField(max_length=10, verbose_name="Code de la moughataa")
    nom = models.CharField(max_length=100, verbose_name="Nom de la moughataa")
    
    class Meta:
        verbose_name = "Moughataa"
        verbose_name_plural = "Moughataas"
    
    def __str__(self):
        return f"{self.nom} ({self.wilaya.nom})"


class Commune(models.Model):
    """Table des communes"""
    moughataa = models.ForeignKey(Moughataa, on_delete=models.CASCADE, related_name='communes', verbose_name="Moughataa")
    code = models.CharField(max_length=10, verbose_name="Code de la commune")
    nom = models.CharField(max_length=100, verbose_name="Nom de la commune")
    
    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
    
    def __str__(self):
        return self.nom


class Paysage(models.Model):
    """Table des paysages/zones"""
    nom = models.CharField(max_length=200, verbose_name="Nom du paysage")
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='paysages', verbose_name="Commune")
    
    class Meta:
        verbose_name = "Paysage"
        verbose_name_plural = "Paysages"
    
    def __str__(self):
        return self.nom


class Village(models.Model):
    """Table des villages"""
    paysage = models.ForeignKey(Paysage, on_delete=models.CASCADE, related_name='villages', null=True, blank=True, verbose_name="Paysage")
    nom = models.CharField(max_length=100, verbose_name="Nom du village")
    
    class Meta:
        unique_together = ('paysage', 'nom')
        verbose_name = "Village"
        verbose_name_plural = "Villages"
    
    def __str__(self):
        return self.nom


# ============================================
# 2. TABLE PRINCIPALE : SOUS-PROJET
# ============================================

class SousProjet(models.Model):
    """Table principale des sous-projets"""
    
    # Choix pour les champs avec valeurs prédéfinies
    GUICHET_CHOICES = [
        ('AGR', 'AGR'),
        ('ACI', 'ACI'),
    ]
    
    TYPE_PROJET_CHOICES = [
        ('AG', 'AG'),
        ('EL', 'EL'),
        ('ENV', 'ENV'),
        ('SER', 'SER'),
    ]
    
    OUI_NON_CHOICES = [
        ('oui', 'Oui'),
        ('non', 'Non'),
    ]
    
    # 1. Informations générales
    date_saisie = models.DateTimeField(auto_now_add=True, verbose_name="Date de saisie")
    date_formulaire = models.DateField(verbose_name="Date du formulaire")
    intitule_sous_projet = models.CharField(max_length=500, verbose_name="Intitulé du sous-projet")
    guichet = models.CharField(max_length=3, choices=GUICHET_CHOICES, verbose_name="Guichet")
    type_projet = models.CharField(max_length=3, choices=TYPE_PROJET_CHOICES, verbose_name="Type de projet")
    chaine_approvisionnement = models.CharField(max_length=500, blank=True, null=True, verbose_name="Chaîne d'approvisionnement")
    marches_vises = models.TextField(help_text="Marchés visés / clients identifiés", blank=True, null=True, verbose_name="Marchés visés")
    segment_ca = models.CharField(max_length=500, blank=True, null=True, verbose_name="Segment de la CA")
    
    # 2. Identification du demandeur
    nom_statut_juridique = models.CharField(max_length=500, verbose_name="Nom et statut juridique")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    personne_contact_nom = models.CharField(max_length=200, verbose_name="Personne contact (nom)")
    personne_contact_fonction = models.CharField(max_length=200,blank=True, null=True, verbose_name="Personne contact (fonction)")
    telephone = models.CharField(max_length=50, verbose_name="Téléphone")
    fax = models.CharField(max_length=50, blank=True, null=True, verbose_name="Fax")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Question femmes/jeunes
    presente_par_femmes_jeunes = models.CharField(
        max_length=3, 
        choices=OUI_NON_CHOICES,
        blank=True, 
        null=True,
        verbose_name="Présenté par des femmes ou jeunes (-35 ans)"
    )
    
    # 3. Description
    objectif_sous_projet = models.TextField(verbose_name="Objectif du sous-projet")
    principales_activites = models.TextField(
        help_text="Liste des principales activités avec objectifs quantitatifs",
        blank=True, 
        null=True,
        verbose_name="Principales activités"
    )
    
    # Localisation
    wilaya = models.ForeignKey(Wilaya, on_delete=models.PROTECT, verbose_name="Wilaya")
    moughataa = models.ForeignKey(Moughataa, on_delete=models.PROTECT, verbose_name="Moughataa")
    commune = models.ForeignKey(Commune, on_delete=models.PROTECT, verbose_name="Commune")
    paysage = models.ForeignKey(Paysage, on_delete=models.SET_NULL, null=True, blank=True, related_name='sous_projets', verbose_name="Paysage")
    village = models.CharField(max_length=200, help_text="Nom du village ou quartier", verbose_name="Village")
    
    # 5. Renseignement sur le promoteur
    annee_debut_activites = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        blank=True, 
        null=True,
        verbose_name="Année de début des activités"
    )
    historique_promoteur = models.TextField(blank=True, null=True, verbose_name="Brève historique")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Sous-projet"
        verbose_name_plural = "Sous-projets"
    
    def __str__(self):
        return f"{self.intitule_sous_projet} - {self.date_formulaire}"


# ============================================
# 3. TABLES DE FINANCEMENT
# ============================================

class Infrastructure(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='infrastructures')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    prix_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False, blank=True, null=True)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant_total avant sauvegarde"""
        # Calcul : Quantité × Prix unitaire
        if self.quantite and self.prix_unit:
            self.montant_total = self.quantite * self.prix_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Infra - {self.sous_projet.id} - {self.description[:30]}"


class Equipement(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='equipements')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    prix_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False, blank=True, null=True)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant_total avant sauvegarde"""
        if self.quantite and self.prix_unit:
            self.montant_total = self.quantite * self.prix_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Équip - {self.sous_projet.id} - {self.description[:30]}"


class Intrant(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='intrants')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    prix_unit = models.DecimalField(max_digits=15, decimal_places=2)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False, blank=True, null=True)
    subvention_padisam = models.DecimalField(max_digits=15, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant_total avant sauvegarde"""
        if self.quantite and self.prix_unit:
            self.montant_total = self.quantite * self.prix_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Intrant - {self.sous_projet.id} - {self.description[:30]}"


class Fonctionnement(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='fonctionnements')
    description = models.CharField(blank=True, null=True, max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    prix_unit = models.DecimalField(max_digits=15, blank=True, null=True, decimal_places=2)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False, blank=True, null=True)
    contribution_promoteur = models.DecimalField(max_digits=15, blank=True, null=True,decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, blank=True, null=True, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant_total avant sauvegarde"""
        if self.quantite and self.prix_unit:
            self.montant_total = self.quantite * self.prix_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Fonct - {self.sous_projet.id} - {self.description[:30]}"


class Service(models.Model):
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='services')
    description = models.CharField(max_length=500)
    quantite = models.IntegerField(validators=[MinValueValidator(0)])
    prix_unit = models.DecimalField(max_digits=15, decimal_places=2)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, editable=False, blank=True, null=True)
    subvention_padisam = models.DecimalField(max_digits=15, blank=True, null=True, decimal_places=2)
    contribution_promoteur = models.DecimalField(max_digits=15,blank=True, null=True, decimal_places=2)
    autre_financement = models.DecimalField(max_digits=15, blank=True, null=True, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        """Calcul automatique du montant_total avant sauvegarde"""
        if self.quantite and self.prix_unit:
            self.montant_total = self.quantite * self.prix_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Service - {self.sous_projet.id} - {self.description[:30]}"

# ============================================
# 4. TABLE DES RÉALISATIONS PASSÉES
# ============================================

class Activite(models.Model):
    """
    Table des activités principales du sous-projet
    Chaque activité peut avoir plusieurs réalisations
    """
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='activites')
    nom_activite = models.CharField(max_length=500, blank=True, null=True, verbose_name="Nom de l'activité")
    realisations = models.TextField(verbose_name="Objectifs quantitatifs", blank=True, null=True)
    
    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
        ordering = ['id']
    
    def __str__(self):
        return self.nom_activite[:50]

class RealisationPassee(models.Model):
    """Table des réalisations passées"""
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='realisations', verbose_name="Sous-projet")
    annee = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)], verbose_name="Année")
    produit = models.CharField(max_length=500, verbose_name="Produit")
    volume = models.DecimalField(max_digits=15, decimal_places=2, help_text="Volume en tonnes/kg selon produit", verbose_name="Volume")
    ventes_usd = models.DecimalField(max_digits=15, decimal_places=2, help_text="Ventes en USD", verbose_name="Ventes USD")
    
    class Meta:
        ordering = ['annee']
        verbose_name = "Réalisation passée"
        verbose_name_plural = "Réalisations passées"
    
    def __str__(self):
        return f"Réalisation {self.annee} - {self.produit[:30]}"


# ============================================
# 5. TABLE DES PASSIFS (EMPRUNTS)
# ============================================

class PassifEmprunt(models.Model):
    """Table des passifs/emprunts"""
    sous_projet = models.ForeignKey(SousProjet, on_delete=models.CASCADE, related_name='emprunts', verbose_name="Sous-projet")
    annee = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)], verbose_name="Année")
    institution_financiere = models.CharField(max_length=200, verbose_name="Institution financière")
    montant_emprunte = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant emprunté")
    montant_rembourse = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant remboursé")
    
    class Meta:
        ordering = ['annee']
        verbose_name = "Passif/Emprunt"
        verbose_name_plural = "Passifs/Emprunts"
    
    def __str__(self):
        return f"Emprunt {self.annee} - {self.institution_financiere[:20]}"


# ============================================
# 6. TABLE UTILISATEUR
# ============================================

class Utilisateur(models.Model):
    """Table des utilisateurs"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('agent', 'Agent de saisie'),
        ('superviseur', 'Superviseur'),
        ('consultant', 'Consultant'),
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    username = models.CharField(max_length=50, unique=True, verbose_name="Nom d'utilisateur")
    password = models.CharField(max_length=128, verbose_name="Mot de passe")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent', verbose_name="Rôle")
    wilaya = models.ForeignKey(
        Wilaya,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Wilaya d'affectation", 
        default=0
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    dernier_login = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    def set_password(self, raw_password):
        """Hash le mot de passe"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Vérifie le mot de passe"""
        return check_password(raw_password, self.password)

    def clean(self):
        if self.role == 'agent' and not self.wilaya:
            raise ValidationError({'wilaya': "La wilaya est obligatoire pour un agent de saisie."})
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.username})"