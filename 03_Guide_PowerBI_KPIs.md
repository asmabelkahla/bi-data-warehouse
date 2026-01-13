# Guide Power BI - Analyse GenAI dans les Entreprises

**Réalisé avec ❤️ par: ASMA & MONIA**
**Module:** Data Analytics & Business Intelligence
**5ème année - Ingénierie Informatique**

---

## 📊 Vue d'ensemble du projet

Ce guide vous accompagne dans la création d'un dashboard Power BI professionnel pour analyser l'adoption et l'impact des outils GenAI dans les entreprises à travers le monde.

---

## 1. CONNEXION AUX DONNÉES

### Option A: Import CSV (Recommandé pour débutants)
1. Ouvrir Power BI Desktop
2. **Obtenir des données** → **Texte/CSV**
3. Sélectionner le fichier `donnees_powerbi_genai.csv`
4. Cliquer sur **Transformer les données** pour accéder à Power Query

### Option B: Connexion directe à SQLite (Avancé)
1. **Obtenir des données** → **Base de données** → **SQLite**
2. Sélectionner `datawarehouse_genai.db`
3. Importer les tables: `FAIT_ADOPTION`, `DIM_COMPANY`, `DIM_GEOGRAPHY`, `DIM_INDUSTRY`, `DIM_GENAI_TOOL`

---

## 2. POWER QUERY - TRANSFORMATIONS

### Vérifications dans Power Query:

```powerquery
// S'assurer que les types de colonnes sont corrects
Table.TransformColumnTypes(
    Source,
    {
        {"Adoption_Year", Int64.Type},
        {"Employees_Impacted", Int64.Type},
        {"New_Roles_Created", Int64.Type},
        {"Training_Hours", Int64.Type},
        {"Productivity_Change", type number},
        {"Training_per_Employee", type number},
        {"New_Roles_Rate", type number}
    }
)
```

### Créer une table Calendrier (importante pour l'analyse temporelle):

```powerquery
= List.Dates(
    #date(2020, 1, 1),
    Duration.Days(#date(2025, 12, 31) - #date(2020, 1, 1)) + 1,
    #duration(1, 0, 0, 0)
)
```

---

## 3. MODÈLE DE DONNÉES

### Relations à créer:
- Si vous utilisez plusieurs tables, créez les relations dans la vue **Modèle**
- Toutes les relations doivent être de type **1 à plusieurs** (one-to-many)
- La cardinalité doit pointer des dimensions vers les faits

---

## 4. MESURES DAX - KPIs PRINCIPAUX

Créer une nouvelle table pour organiser vos mesures:
**Page d'accueil** → **Nouvelle table** → Nommer "_Mesures"

### 📈 KPI 1: Nombre Total d'Entreprises

```dax
Total Entreprises =
COUNTROWS('donnees_powerbi_genai')
```

### 📈 KPI 2: Total Employés Impactés

```dax
Total Employés Impactés =
SUM('donnees_powerbi_genai'[Employees_Impacted])
```

Format: Nombre entier avec séparateur de milliers

### 📈 KPI 3: Productivité Moyenne

```dax
Productivité Moyenne (%) =
AVERAGE('donnees_powerbi_genai'[Productivity_Change])
```

Format: Pourcentage avec 2 décimales

### 📈 KPI 4: Total Nouveaux Rôles Créés

```dax
Total Nouveaux Rôles =
SUM('donnees_powerbi_genai'[New_Roles_Created])
```

### 📈 KPI 5: Heures de Formation Totales

```dax
Total Heures Formation =
SUM('donnees_powerbi_genai'[Training_Hours])
```

Format: Nombre entier avec "h" comme suffixe

### 📈 KPI 6: Formation Moyenne par Employé

```dax
Formation Moy par Employé =
AVERAGE('donnees_powerbi_genai'[Training_per_Employee])
```

Format: Nombre décimal (2 chiffres) avec "h" comme suffixe

---

## 5. MESURES DAX AVANCÉES

### 🎯 Taux d'Adoption par Phase

```dax
% Early Adopters =
DIVIDE(
    CALCULATE(
        COUNTROWS('donnees_powerbi_genai'),
        'donnees_powerbi_genai'[Adoption_Phase] = "Early Adopter"
    ),
    COUNTROWS('donnees_powerbi_genai'),
    0
)
```

### 🎯 Impact Productivité Catégorisé

```dax
Entreprises Impact Élevé =
CALCULATE(
    COUNTROWS('donnees_powerbi_genai'),
    OR(
        'donnees_powerbi_genai'[Productivity_Impact] = "Élevé",
        'donnees_powerbi_genai'[Productivity_Impact] = "Très Élevé"
    )
)
```

### 🎯 Taux de Sentiment Positif

```dax
% Sentiment Positif =
DIVIDE(
    CALCULATE(
        COUNTROWS('donnees_powerbi_genai'),
        'donnees_powerbi_genai'[Sentiment_Category] = "Positif"
    ),
    COUNTROWS('donnees_powerbi_genai'),
    0
)
```

### 🎯 ROI Formation (Return on Training Investment)

```dax
ROI Formation =
DIVIDE(
    [Productivité Moyenne (%)],
    [Formation Moy par Employé],
    0
)
```

### 🎯 Taux de Création de Rôles

```dax
Taux Nouveaux Rôles (%) =
AVERAGE('donnees_powerbi_genai'[New_Roles_Rate])
```

### 🎯 Comparaison Année Précédente (YoY)

```dax
Productivité YoY =
VAR ProductiviteAnneeActuelle = [Productivité Moyenne (%)]
VAR ProductiviteAnneePrecedente =
    CALCULATE(
        [Productivité Moyenne (%)],
        DATEADD('Calendrier'[Date], -1, YEAR)
    )
RETURN
    ProductiviteAnneeActuelle - ProductiviteAnneePrecedente
```

### 🎯 Top Outil GenAI

```dax
Outil GenAI le Plus Utilisé =
CALCULATE(
    VALUES('donnees_powerbi_genai'[GenAI_Tool]),
    TOPN(
        1,
        SUMMARIZE(
            'donnees_powerbi_genai',
            'donnees_powerbi_genai'[GenAI_Tool],
            "Compte", COUNTROWS('donnees_powerbi_genai')
        ),
        [Compte],
        DESC
    )
)
```

---

## 6. CONCEPTION DU DASHBOARD

### 📄 Page 1: VUE D'ENSEMBLE (Overview)

**Layout suggéré:**

#### En-tête (Top):
- **Titre**: "Analyse Globale de l'Adoption GenAI"
- **Filtres de page**: Année, Région, Secteur

#### Cartes KPI (Row 1 - 6 cartes):
1. **Total Entreprises** - Carte simple avec icône
2. **Total Employés Impactés** - Format milliers
3. **Productivité Moyenne** - Format pourcentage
4. **Total Nouveaux Rôles** - Nombre entier
5. **% Sentiment Positif** - Jauge circulaire
6. **Formation Moyenne** - Heures par employé

#### Visualisations principales (Rows 2-3):

**Graphique en barres horizontal:**
- Titre: "Top 15 Pays par Nombre d'Entreprises"
- Axe Y: Country
- Axe X: Total Entreprises
- Couleur: Par région

**Graphique en colonnes empilées:**
- Titre: "Adoption par Année et Phase"
- Axe X: Adoption_Year
- Valeurs: Total Entreprises
- Légende: Adoption_Phase
- Couleurs personnalisées: Early (Vert), Mainstream (Bleu), Late (Orange)

**Carte géographique (Map):**
- Localisation: Country
- Taille: Total Employés Impactés
- Couleur: Productivité Moyenne
- Info-bulles: Tous les KPIs

**Graphique en secteurs (Donut):**
- Titre: "Répartition par Type de Secteur"
- Légende: Sector_Type
- Valeurs: Total Entreprises
- Afficher les pourcentages

---

### 📄 Page 2: ANALYSE PAR SECTEUR

**Matrice interactive:**
- Lignes: Sector_Type → Industry_Name
- Valeurs:
  - Total Entreprises
  - Productivité Moyenne
  - Total Employés Impactés
  - Formation Moyenne
- Mise en forme conditionnelle sur Productivité

**Graphique en barres groupées:**
- Titre: "Impact Productivité par Secteur et Taille d'Entreprise"
- Axe X: Sector_Type
- Valeurs: Productivité Moyenne
- Légende: Company_Size

**Nuage de points (Scatter):**
- Titre: "Formation vs Productivité par Industrie"
- Axe X: Formation Moy par Employé
- Axe Y: Productivité Moyenne
- Détails: Industry_Name
- Taille: Total Entreprises
- Couleur: Sector_Type

---

### 📄 Page 3: ANALYSE PAR OUTIL GENAI

**Graphique en barres empilées 100%:**
- Titre: "Parts de Marché des Outils GenAI par Année"
- Axe X: Adoption_Year
- Valeurs: % du total
- Légende: GenAI_Tool

**Table détaillée:**
Colonnes:
- GenAI_Tool
- Tool_Provider
- Nombre d'entreprises
- Productivité Moyenne
- Employés Moyens Impactés
- Taux Sentiment Positif

**Graphique en colonnes groupées:**
- Titre: "Productivité Moyenne par Outil GenAI"
- Axe X: GenAI_Tool
- Valeurs: Productivité Moyenne
- Trier par valeur décroissante

**Graphique en lignes:**
- Titre: "Évolution de l'Utilisation des Outils GenAI"
- Axe X: Adoption_Year
- Valeurs: Total Entreprises
- Légende: GenAI_Tool

---

### 📄 Page 4: IMPACT SUR LES EMPLOYÉS

**Jauge (Gauge):**
- Titre: "Score de Satisfaction Global"
- Valeur: % Sentiment Positif
- Min: 0%, Max: 100%
- Objectif: 80%

**Graphique en barres empilées:**
- Titre: "Sentiment des Employés par Secteur"
- Axe Y: Sector_Type
- Valeurs: Nombre d'entreprises
- Légende: Sentiment_Category
- Couleurs: Positif (Vert), Neutre (Jaune), Négatif (Rouge)

**Graphique en colonnes:**
- Titre: "Nouveaux Rôles Créés par Secteur"
- Axe X: Sector_Type
- Valeurs: Total Nouveaux Rôles

**KPI visuel:**
- Taux de Création de Rôles (%)
- Format: Carte avec tendance

**Nuage de mots (si addon disponible):**
- Basé sur Employee_Sentiment
- Taille selon fréquence des mots

---

### 📄 Page 5: ANALYSE GÉOGRAPHIQUE

**Carte Choroplèthe:**
- Pays colorés selon la productivité moyenne
- Dégradé de couleurs: Rouge (faible) → Vert (élevé)

**Graphique en barres horizontal:**
- Top 10 Pays par Productivité Moyenne
- Tri décroissant

**Table Matrix:**
- Lignes: Region → Country
- Valeurs:
  - Nombre d'entreprises
  - Total Employés
  - Productivité Moyenne
  - Formation Moyenne

**Graphique en entonnoir:**
- Titre: "Répartition des Entreprises par Région"
- Valeurs: Total Entreprises
- Groupe: Region

---

## 7. SLICERS (FILTRES) À AJOUTER

### Filtres globaux (sur toutes les pages):
- **Adoption_Year**: Liste déroulante ou Slider
- **Region**: Liste avec sélection multiple
- **Sector_Type**: Tuiles (Tiles)
- **Company_Size**: Boutons radio

### Filtres spécifiques:
- Page 3: GenAI_Tool (liste)
- Page 4: Sentiment_Category (boutons)
- Page 5: Country (recherche)

---

## 8. MISE EN FORME ET DESIGN

### Palette de couleurs suggérée:
- **Principal**: #0078D4 (Bleu Microsoft)
- **Secondaire**: #50E6FF (Cyan)
- **Accent 1**: #00B294 (Vert)
- **Accent 2**: #FF8C00 (Orange)
- **Négatif**: #E74856 (Rouge)
- **Neutre**: #8A8886 (Gris)

### Thème personnalisé:
1. **Affichage** → **Thèmes** → **Personnaliser le thème actuel**
2. Ajuster les couleurs selon la palette ci-dessus
3. Sauvegarder comme "Thème GenAI Analysis"

### Polices:
- **Titres**: Segoe UI Bold, 16-20pt
- **Sous-titres**: Segoe UI Semibold, 12-14pt
- **Corps**: Segoe UI Regular, 10-11pt

### Icônes et images:
- Ajouter des icônes pour chaque KPI (télécharger depuis flaticon.com)
- Logo de l'entreprise dans l'en-tête
- Icônes des outils GenAI si disponibles

---

## 9. INTERACTIVITÉ AVANCÉE

### Drill-through:
**De la page Overview vers Secteur:**
1. Clic droit sur la page "Analyse par Secteur"
2. Activer "Drill-through"
3. Ajouter "Industry_Name" comme filtre de drill-through

### Boutons de navigation:
1. Créer des boutons pour chaque page
2. **Action** → **Navigation de page**
3. Design: Icônes + Texte

### Info-bulles personnalisées:
1. Créer une page cachée "Tooltip - Entreprise"
2. Afficher: Company_Name, tous les KPIs
3. Utiliser comme info-bulle sur les visualisations principales

### Signets (Bookmarks):
- **Vue Globale**: Tous les filtres réinitialisés
- **Top Performers**: Filtrer Productivité > 25%
- **Early Adopters**: Filtrer Adoption_Phase = "Early Adopter"

---

## 10. QUESTIONS MÉTIER À RÉPONDRE

Votre dashboard doit permettre de répondre à ces questions:

### Stratégiques:
1. Quels pays adoptent le plus rapidement les GenAI?
2. Quels secteurs bénéficient le plus en termes de productivité?
3. Quel outil GenAI est le plus efficace par secteur?

### Opérationnelles:
4. Combien d'heures de formation sont nécessaires par secteur?
5. Quel est le taux de création de nouveaux rôles?
6. Y a-t-il une corrélation entre formation et productivité?

### RH et Change Management:
7. Quel est le sentiment des employés par secteur?
8. Les early adopters ont-ils une meilleure acceptation?
9. Quelle taille d'entreprise réussit le mieux l'adoption?

### Temporelles:
10. L'adoption s'accélère-t-elle au fil des années?
11. La productivité s'améliore-t-elle avec le temps?
12. Quels outils gagnent en popularité?

---

## 11. CHECKLIST AVANT LA PRÉSENTATION

### Données:
- [ ] Toutes les colonnes ont le bon type de données
- [ ] Pas de valeurs nulles dans les visualisations
- [ ] Les relations sont correctes
- [ ] Les mesures DAX fonctionnent sans erreur

### Visualisations:
- [ ] Tous les graphiques ont un titre clair
- [ ] Les axes sont bien étiquetés
- [ ] Les couleurs sont cohérentes
- [ ] Les formats numériques sont appropriés

### Interactivité:
- [ ] Les filtres fonctionnent sur toutes les pages
- [ ] Le cross-filtering est activé
- [ ] Les drill-through fonctionnent
- [ ] Les boutons de navigation sont visibles

### Performance:
- [ ] Le dashboard se charge rapidement
- [ ] Pas de mesures DAX lentes
- [ ] Les visualisations se mettent à jour rapidement

### Présentation:
- [ ] Le storytelling est clair
- [ ] Les insights principaux sont mis en évidence
- [ ] Le design est professionnel
- [ ] Pas de fautes d'orthographe

---

## 12. EXPORT ET PARTAGE

### Publier sur Power BI Service:
1. **Fichier** → **Publier** → **Publier sur Power BI**
2. Sélectionner votre espace de travail
3. Configurer l'actualisation automatique si nécessaire

### Exporter en PDF:
1. **Fichier** → **Exporter** → **Exporter en PDF**
2. Sélectionner toutes les pages
3. Utiliser pour la présentation

### Intégration MERN (bonus):
```javascript
// Exemple d'intégration avec Power BI Embedded
const embedConfig = {
    type: 'report',
    id: 'VOTRE_REPORT_ID',
    embedUrl: 'VOTRE_EMBED_URL',
    accessToken: 'VOTRE_ACCESS_TOKEN',
    settings: {
        filterPaneEnabled: false,
        navContentPaneEnabled: true
    }
};

powerbi.embed(reportContainer, embedConfig);
```

---

## 13. BONUS - FONCTIONNALITÉS AVANCÉES

### 🌟 Q&A (Questions & Réponses):
- Ajouter un visuel Q&A en langage naturel
- Entraîner les synonymes pour votre domaine

### 🌟 Analyse d'influenceurs clés:
- Utiliser le visuel "Influenceurs clés"
- Analyser: "Qu'est-ce qui influence la productivité?"

### 🌟 Prédictions avec Quick Insights:
- Clic droit sur une mesure → "Analyser"
- Identifier les tendances automatiquement

### 🌟 Alertes:
- Configurer des alertes sur Power BI Service
- Exemple: Notifier si productivité < 10%

---

## 14. RESSOURCES COMPLÉMENTAIRES

### Documentation:
- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Guide](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)

### Tutoriels vidéo:
- Guy in a Cube (YouTube)
- Curbal (YouTube)
- SQLBI (Articles avancés)

### Templates:
- Power BI Theme Generator
- Icon8 (Icônes gratuites)
- Flaticon (Icônes et illustrations)

---

## 🎯 OBJECTIF FINAL

Créer un dashboard qui:
1. ✅ Répond aux questions métier du cahier des charges
2. ✅ Utilise au minimum 8-10 visualisations différentes
3. ✅ Contient 10+ mesures DAX pertinentes
4. ✅ Offre une expérience utilisateur fluide et intuitive
5. ✅ Raconte une histoire claire sur l'adoption GenAI
6. ✅ Permet la prise de décision basée sur les données

---

**Bonne création de dashboard! 🚀**

*Pour toute question sur les mesures DAX ou la conception des visualisations, consultez ce guide ou la documentation Power BI officielle.*
