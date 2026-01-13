# -*- coding: utf-8 -*-
"""
Projet BI - Mini-projet Data Analytics & Business Intelligence
ETL et Data Warehouse pour l'Adoption GenAI dans les Entreprises
Modèle en Étoile (Star Schema)

Réalisé avec ❤️ par: ASMA & MONIA
Module: Data Analytics & Business Intelligence
5ème année - Ingénierie Informatique
"""

import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print(" PROJET BI - ETL ET DATA WAREHOUSE GENAI ".center(80, "="))
print("="*80)

# ==================================================================================
# ÉTAPE 1: EXTRACTION DES DONNÉES
# ==================================================================================
print("\n[ÉTAPE 1] EXTRACTION DES DONNÉES")
print("-" * 80)

# Charger les données nettoyées
df = pd.read_csv('donnees_genai_nettoyees.csv')
print(f"✓ Données chargées: {df.shape[0]:,} lignes, {df.shape[1]} colonnes")

# Sauvegarde des données brutes
df_original = df.copy()

# ==================================================================================
# ÉTAPE 2: CONCEPTION DU MODÈLE EN ÉTOILE
# ==================================================================================
print("\n[ÉTAPE 2] CONCEPTION DU MODÈLE EN ÉTOILE")
print("-" * 80)

print("""
ARCHITECTURE DU DATA WAREHOUSE - MODÈLE EN ÉTOILE

                    ┌─────────────────┐
                    │  DIM_COMPANY    │
                    ├─────────────────┤
                    │ Company_ID (PK) │
                    │ Company_Name    │
                    │ Company_Size    │
                    └────────┬────────┘
                             │
                             │
    ┌─────────────────┐      │      ┌──────────────────┐
    │  DIM_GEOGRAPHY  │      │      │   DIM_INDUSTRY   │
    ├─────────────────┤      │      ├──────────────────┤
    │ Geography_ID(PK)│      │      │ Industry_ID (PK) │
    │ Country         │      │      │ Industry_Name    │
    │ Region          │      │      │ Sector_Type      │
    └────────┬────────┘      │      └────────┬─────────┘
             │               │               │
             │               │               │
             └───────────────┼───────────────┘
                             │
                   ┌─────────▼──────────┐
                   │  FAIT_ADOPTION     │
                   ├────────────────────┤
                   │ Adoption_ID (PK)   │
                   │ Company_ID (FK)    │
                   │ Geography_ID (FK)  │
                   │ Industry_ID (FK)   │
                   │ GenAI_Tool_ID (FK) │
                   │ Adoption_Year      │
                   │ Employees_Impacted │
                   │ New_Roles_Created  │
                   │ Training_Hours     │
                   │ Productivity_Chg   │
                   │ Training_per_Emp   │
                   │ New_Roles_Rate     │
                   │ Sentiment_Category │
                   └─────────┬──────────┘
                             │
                    ┌────────▼─────────┐
                    │ DIM_GENAI_TOOL   │
                    ├──────────────────┤
                    │ GenAI_Tool_ID(PK)│
                    │ Tool_Name        │
                    │ Tool_Category    │
                    └──────────────────┘

✓ Modèle en étoile avec:
  - 1 Table de faits: FAIT_ADOPTION
  - 4 Tables de dimensions: DIM_COMPANY, DIM_GEOGRAPHY, DIM_INDUSTRY, DIM_GENAI_TOOL
""")

# ==================================================================================
# ÉTAPE 3: CRÉATION DU DATA WAREHOUSE (SQLite)
# ==================================================================================
print("\n[ÉTAPE 3] CRÉATION DU DATA WAREHOUSE")
print("-" * 80)

# Connexion à la base de données SQLite
db_path = 'datawarehouse_genai.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print(f"✓ Connexion à la base de données établie: {db_path}")

# 3.1 Table de dimension: DIM_COMPANY
print("\n3.1 Création de DIM_COMPANY:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_COMPANY (
    Company_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Company_Name TEXT NOT NULL,
    Company_Size TEXT,
    Employees_Impacted_Category TEXT
)
''')
conn.commit()
print("  ✓ Table DIM_COMPANY créée")

# 3.2 Table de dimension: DIM_GEOGRAPHY
print("\n3.2 Création de DIM_GEOGRAPHY:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_GEOGRAPHY (
    Geography_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Country TEXT NOT NULL,
    Region TEXT
)
''')
conn.commit()
print("  ✓ Table DIM_GEOGRAPHY créée")

# 3.3 Table de dimension: DIM_INDUSTRY
print("\n3.3 Création de DIM_INDUSTRY:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_INDUSTRY (
    Industry_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Industry_Name TEXT NOT NULL UNIQUE,
    Sector_Type TEXT
)
''')
conn.commit()
print("  ✓ Table DIM_INDUSTRY créée")

# 3.4 Table de dimension: DIM_GENAI_TOOL
print("\n3.4 Création de DIM_GENAI_TOOL:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS DIM_GENAI_TOOL (
    GenAI_Tool_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Tool_Name TEXT NOT NULL UNIQUE,
    Tool_Category TEXT,
    Tool_Provider TEXT
)
''')
conn.commit()
print("  ✓ Table DIM_GENAI_TOOL créée")

# 3.5 Table de faits: FAIT_ADOPTION
print("\n3.5 Création de FAIT_ADOPTION:")
cursor.execute('''
CREATE TABLE IF NOT EXISTS FAIT_ADOPTION (
    Adoption_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Company_ID INTEGER,
    Geography_ID INTEGER,
    Industry_ID INTEGER,
    GenAI_Tool_ID INTEGER,
    Adoption_Year INTEGER,
    Adoption_Phase TEXT,
    Employees_Impacted INTEGER,
    New_Roles_Created INTEGER,
    Training_Hours INTEGER,
    Productivity_Change REAL,
    Productivity_Impact TEXT,
    Training_per_Employee REAL,
    New_Roles_Rate REAL,
    Sentiment_Category TEXT,
    Employee_Sentiment TEXT,
    FOREIGN KEY (Company_ID) REFERENCES DIM_COMPANY(Company_ID),
    FOREIGN KEY (Geography_ID) REFERENCES DIM_GEOGRAPHY(Geography_ID),
    FOREIGN KEY (Industry_ID) REFERENCES DIM_INDUSTRY(Industry_ID),
    FOREIGN KEY (GenAI_Tool_ID) REFERENCES DIM_GENAI_TOOL(GenAI_Tool_ID)
)
''')
conn.commit()
print("  ✓ Table FAIT_ADOPTION créée")

# ==================================================================================
# ÉTAPE 4: PRÉPARATION DES DIMENSIONS (TRANSFORMATION)
# ==================================================================================
print("\n[ÉTAPE 4] PRÉPARATION DES DIMENSIONS")
print("-" * 80)

# 4.1 Mapping des régions géographiques
def get_region(country):
    """Mapper les pays vers des régions géographiques"""
    regions = {
        'USA': 'Amérique du Nord',
        'Canada': 'Amérique du Nord',
        'Brazil': 'Amérique du Sud',
        'UK': 'Europe',
        'Germany': 'Europe',
        'France': 'Europe',
        'Switzerland': 'Europe',
        'South Africa': 'Afrique',
        'UAE': 'Moyen-Orient',
        'India': 'Asie',
        'Singapore': 'Asie',
        'Japan': 'Asie',
        'South Korea': 'Asie',
        'Australia': 'Océanie'
    }
    return regions.get(country, 'Autre')

df['Region'] = df['Country'].apply(get_region)

# 4.2 Catégorisation des secteurs
def get_sector_type(industry):
    """Mapper les industries vers des types de secteurs"""
    sectors = {
        'Technology': 'Tech & Digital',
        'Healthcare': 'Services Essentiels',
        'Finance': 'Finance & Assurance',
        'Retail': 'Commerce & Distribution',
        'Manufacturing': 'Production & Industrie',
        'Education': 'Services Publics',
        'Transportation': 'Transport & Logistique',
        'Telecom': 'Tech & Digital',
        'Hospitality': 'Services & Loisirs',
        'Entertainment': 'Services & Loisirs',
        'Legal Services': 'Services Professionnels',
        'Advertising': 'Services Professionnels',
        'Utilities': 'Services Essentiels',
        'Defense': 'Défense & Sécurité'
    }
    return sectors.get(industry, 'Autre')

df['Sector_Type'] = df['Industry'].apply(get_sector_type)

# 4.3 Catégorisation des outils GenAI
def get_tool_category(tool):
    """Catégoriser les outils GenAI"""
    if tool in ['ChatGPT', 'GPT-4']:
        return 'LLM - OpenAI'
    elif tool == 'Claude':
        return 'LLM - Anthropic'
    elif tool == 'Gemini':
        return 'LLM - Google'
    elif tool == 'LLaMA':
        return 'LLM - Meta'
    elif tool == 'Mixtral':
        return 'LLM - Mistral'
    elif tool == 'Groq':
        return 'Infrastructure AI'
    else:
        return 'Autre'

def get_tool_provider(tool):
    """Identifier le fournisseur de l'outil"""
    providers = {
        'ChatGPT': 'OpenAI',
        'Claude': 'Anthropic',
        'Gemini': 'Google',
        'LLaMA': 'Meta',
        'Mixtral': 'Mistral AI',
        'Groq': 'Groq Inc'
    }
    return providers.get(tool, 'Inconnu')

df['Tool_Category'] = df['GenAI Tool'].apply(get_tool_category)
df['Tool_Provider'] = df['GenAI Tool'].apply(get_tool_provider)

print("✓ Enrichissement des données terminé")
print(f"  - Régions géographiques: {df['Region'].nunique()}")
print(f"  - Types de secteurs: {df['Sector_Type'].nunique()}")
print(f"  - Catégories d'outils: {df['Tool_Category'].nunique()}")

# ==================================================================================
# ÉTAPE 5: CHARGEMENT DES DIMENSIONS (LOADING)
# ==================================================================================
print("\n[ÉTAPE 5] CHARGEMENT DES DIMENSIONS")
print("-" * 80)

# 5.1 Chargement DIM_GEOGRAPHY
print("\n5.1 Chargement de DIM_GEOGRAPHY:")
geography_dim = df[['Country', 'Region']].drop_duplicates().reset_index(drop=True)
geography_mapping = {}

for idx, row in geography_dim.iterrows():
    cursor.execute('''
    INSERT INTO DIM_GEOGRAPHY (Country, Region)
    VALUES (?, ?)
    ''', (row['Country'], row['Region']))
    geography_id = cursor.lastrowid
    geography_mapping[row['Country']] = geography_id

conn.commit()
print(f"  ✓ {len(geography_dim)} pays chargés")

# 5.2 Chargement DIM_INDUSTRY
print("\n5.2 Chargement de DIM_INDUSTRY:")
industry_dim = df[['Industry', 'Sector_Type']].drop_duplicates().reset_index(drop=True)
industry_mapping = {}

for idx, row in industry_dim.iterrows():
    cursor.execute('''
    INSERT INTO DIM_INDUSTRY (Industry_Name, Sector_Type)
    VALUES (?, ?)
    ''', (row['Industry'], row['Sector_Type']))
    industry_id = cursor.lastrowid
    industry_mapping[row['Industry']] = industry_id

conn.commit()
print(f"  ✓ {len(industry_dim)} industries chargées")

# 5.3 Chargement DIM_GENAI_TOOL
print("\n5.3 Chargement de DIM_GENAI_TOOL:")
tool_dim = df[['GenAI Tool', 'Tool_Category', 'Tool_Provider']].drop_duplicates().reset_index(drop=True)
tool_mapping = {}

for idx, row in tool_dim.iterrows():
    cursor.execute('''
    INSERT INTO DIM_GENAI_TOOL (Tool_Name, Tool_Category, Tool_Provider)
    VALUES (?, ?, ?)
    ''', (row['GenAI Tool'], row['Tool_Category'], row['Tool_Provider']))
    tool_id = cursor.lastrowid
    tool_mapping[row['GenAI Tool']] = tool_id

conn.commit()
print(f"  ✓ {len(tool_dim)} outils GenAI chargés")

# ==================================================================================
# ÉTAPE 6: CHARGEMENT DE LA TABLE DE FAITS
# ==================================================================================
print("\n[ÉTAPE 6] CHARGEMENT DE LA TABLE DE FAITS")
print("-" * 80)

loaded_count = 0
error_count = 0

for idx, row in df.iterrows():
    try:
        # Insérer dans DIM_COMPANY
        cursor.execute('''
        INSERT INTO DIM_COMPANY (Company_Name, Company_Size, Employees_Impacted_Category)
        VALUES (?, ?, ?)
        ''', (row['Company Name'], row['Company_Size'], row['Company_Size']))
        company_id = cursor.lastrowid

        # Récupérer les IDs des dimensions
        geography_id = geography_mapping.get(row['Country'])
        industry_id = industry_mapping.get(row['Industry'])
        tool_id = tool_mapping.get(row['GenAI Tool'])

        # Insérer dans FAIT_ADOPTION
        cursor.execute('''
        INSERT INTO FAIT_ADOPTION (
            Company_ID, Geography_ID, Industry_ID, GenAI_Tool_ID,
            Adoption_Year, Adoption_Phase,
            Employees_Impacted, New_Roles_Created, Training_Hours,
            Productivity_Change, Productivity_Impact,
            Training_per_Employee, New_Roles_Rate,
            Sentiment_Category, Employee_Sentiment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_id, geography_id, industry_id, tool_id,
            int(row['Adoption Year']), row['Adoption_Phase'],
            int(row['Number of Employees Impacted']), int(row['New Roles Created']),
            int(row['Training Hours Provided']),
            float(row['Productivity Change (%)']), row['Productivity_Impact'],
            float(row['Training_per_Employee']), float(row['New_Roles_Rate']),
            row['Sentiment_Category'], row['Employee Sentiment']
        ))

        loaded_count += 1
        if loaded_count % 10000 == 0:
            conn.commit()
            print(f"  ✓ {loaded_count:,} enregistrements chargés...")

    except Exception as e:
        error_count += 1
        if error_count <= 5:  # Afficher seulement les 5 premières erreurs
            print(f"  ✗ Erreur ligne {idx}: {e}")
        continue

conn.commit()
print(f"\n✓ Chargement terminé: {loaded_count:,} enregistrements insérés")
if error_count > 0:
    print(f"⚠️  {error_count} erreurs rencontrées")

# ==================================================================================
# ÉTAPE 7: VALIDATION ET STATISTIQUES DU DATA WAREHOUSE
# ==================================================================================
print("\n[ÉTAPE 7] VALIDATION ET STATISTIQUES DU DATA WAREHOUSE")
print("-" * 80)

# Compter les enregistrements dans chaque table
tables = ['DIM_COMPANY', 'DIM_GEOGRAPHY', 'DIM_INDUSTRY', 'DIM_GENAI_TOOL', 'FAIT_ADOPTION']
print("\nNombre d'enregistrements par table:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  ✓ {table}: {count:,} enregistrements")

# Statistiques clés
print("\n" + "="*80)
print("STATISTIQUES CLÉS DU DATA WAREHOUSE")
print("="*80)

# Par géographie
print("\n📊 TOP 10 PAYS PAR NOMBRE D'ADOPTIONS:")
cursor.execute("""
SELECT g.Country, COUNT(*) as Nombre_Adoptions
FROM FAIT_ADOPTION f
JOIN DIM_GEOGRAPHY g ON f.Geography_ID = g.Geography_ID
GROUP BY g.Country
ORDER BY Nombre_Adoptions DESC
LIMIT 10
""")
for row in cursor.fetchall():
    print(f"  • {row[0]}: {row[1]:,} entreprises")

# Par industrie
print("\n📊 RÉPARTITION PAR SECTEUR:")
cursor.execute("""
SELECT i.Sector_Type, COUNT(*) as Nombre
FROM FAIT_ADOPTION f
JOIN DIM_INDUSTRY i ON f.Industry_ID = i.Industry_ID
GROUP BY i.Sector_Type
ORDER BY Nombre DESC
""")
for row in cursor.fetchall():
    print(f"  • {row[0]}: {row[1]:,} entreprises")

# Par outil GenAI
print("\n📊 POPULARITÉ DES OUTILS GENAI:")
cursor.execute("""
SELECT t.Tool_Name, t.Tool_Provider, COUNT(*) as Nombre_Utilisations
FROM FAIT_ADOPTION f
JOIN DIM_GENAI_TOOL t ON f.GenAI_Tool_ID = t.GenAI_Tool_ID
GROUP BY t.Tool_Name, t.Tool_Provider
ORDER BY Nombre_Utilisations DESC
""")
for row in cursor.fetchall():
    print(f"  • {row[0]} ({row[1]}): {row[2]:,} entreprises")

# Par année
print("\n📊 ÉVOLUTION DE L'ADOPTION PAR ANNÉE:")
cursor.execute("""
SELECT Adoption_Year, COUNT(*) as Nombre,
       ROUND(AVG(Productivity_Change), 2) as Productivite_Moyenne
FROM FAIT_ADOPTION
GROUP BY Adoption_Year
ORDER BY Adoption_Year
""")
for row in cursor.fetchall():
    print(f"  • {row[0]}: {row[1]:,} entreprises (Productivité moyenne: +{row[2]}%)")

# Statistiques globales
print("\n📊 STATISTIQUES GLOBALES:")
cursor.execute("""
SELECT
    COUNT(*) as Total_Entreprises,
    SUM(Employees_Impacted) as Total_Employes,
    AVG(Employees_Impacted) as Moy_Employes,
    SUM(New_Roles_Created) as Total_Nouveaux_Roles,
    AVG(New_Roles_Created) as Moy_Nouveaux_Roles,
    AVG(Productivity_Change) as Moy_Productivite,
    AVG(Training_per_Employee) as Moy_Formation_Par_Employe
FROM FAIT_ADOPTION
""")
stats = cursor.fetchone()
print(f"  • Total entreprises: {stats[0]:,}")
print(f"  • Total employés impactés: {stats[1]:,}")
print(f"  • Moyenne employés par entreprise: {stats[2]:,.0f}")
print(f"  • Total nouveaux rôles créés: {stats[3]:,}")
print(f"  • Moyenne nouveaux rôles par entreprise: {stats[4]:.1f}")
print(f"  • Productivité moyenne: +{stats[5]:.2f}%")
print(f"  • Formation moyenne par employé: {stats[6]:.2f}h")

# Sentiment des employés
print("\n📊 SENTIMENT DES EMPLOYÉS:")
cursor.execute("""
SELECT Sentiment_Category, COUNT(*) as Nombre,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM FAIT_ADOPTION), 1) as Pourcentage
FROM FAIT_ADOPTION
GROUP BY Sentiment_Category
ORDER BY Nombre DESC
""")
for row in cursor.fetchall():
    print(f"  • {row[0]}: {row[1]:,} entreprises ({row[2]}%)")

# ==================================================================================
# ÉTAPE 8: EXPORT POUR POWER BI
# ==================================================================================
print("\n[ÉTAPE 8] EXPORT POUR POWER BI")
print("-" * 80)

# Créer une vue complète pour Power BI
query = """
SELECT
    f.Adoption_ID,
    c.Company_Name,
    c.Company_Size,
    g.Country,
    g.Region,
    i.Industry_Name,
    i.Sector_Type,
    t.Tool_Name as GenAI_Tool,
    t.Tool_Category,
    t.Tool_Provider,
    f.Adoption_Year,
    f.Adoption_Phase,
    f.Employees_Impacted,
    f.New_Roles_Created,
    f.Training_Hours,
    f.Productivity_Change,
    f.Productivity_Impact,
    f.Training_per_Employee,
    f.New_Roles_Rate,
    f.Sentiment_Category,
    f.Employee_Sentiment
FROM FAIT_ADOPTION f
LEFT JOIN DIM_COMPANY c ON f.Company_ID = c.Company_ID
LEFT JOIN DIM_GEOGRAPHY g ON f.Geography_ID = g.Geography_ID
LEFT JOIN DIM_INDUSTRY i ON f.Industry_ID = i.Industry_ID
LEFT JOIN DIM_GENAI_TOOL t ON f.GenAI_Tool_ID = t.GenAI_Tool_ID
"""

df_powerbi = pd.read_sql_query(query, conn)
output_file = 'donnees_powerbi_genai.csv'
df_powerbi.to_csv(output_file, index=False, encoding='utf-8')
print(f"✓ Dataset pour Power BI exporté: {output_file} ({len(df_powerbi):,} lignes)")

# Créer aussi des tables agrégées pour faciliter l'analyse
print("\n✓ Création de tables agrégées:")

# Agrégation par pays
cursor.execute("""
CREATE VIEW IF NOT EXISTS VUE_PAYS AS
SELECT
    g.Country,
    g.Region,
    COUNT(*) as Nombre_Entreprises,
    SUM(f.Employees_Impacted) as Total_Employes,
    AVG(f.Productivity_Change) as Productivite_Moyenne,
    SUM(f.New_Roles_Created) as Total_Nouveaux_Roles
FROM FAIT_ADOPTION f
JOIN DIM_GEOGRAPHY g ON f.Geography_ID = g.Geography_ID
GROUP BY g.Country, g.Region
""")
print("  • VUE_PAYS créée")

# Agrégation par industrie
cursor.execute("""
CREATE VIEW IF NOT EXISTS VUE_INDUSTRIE AS
SELECT
    i.Industry_Name,
    i.Sector_Type,
    COUNT(*) as Nombre_Entreprises,
    AVG(f.Productivity_Change) as Productivite_Moyenne,
    AVG(f.Training_per_Employee) as Formation_Moyenne
FROM FAIT_ADOPTION f
JOIN DIM_INDUSTRY i ON f.Industry_ID = i.Industry_ID
GROUP BY i.Industry_Name, i.Sector_Type
""")
print("  • VUE_INDUSTRIE créée")

# Agrégation par outil
cursor.execute("""
CREATE VIEW IF NOT EXISTS VUE_GENAI_TOOL AS
SELECT
    t.Tool_Name,
    t.Tool_Provider,
    COUNT(*) as Nombre_Utilisations,
    AVG(f.Productivity_Change) as Productivite_Moyenne,
    AVG(f.Employees_Impacted) as Employes_Moyens
FROM FAIT_ADOPTION f
JOIN DIM_GENAI_TOOL t ON f.GenAI_Tool_ID = t.GenAI_Tool_ID
GROUP BY t.Tool_Name, t.Tool_Provider
""")
print("  • VUE_GENAI_TOOL créée")

conn.commit()

# ==================================================================================
# ÉTAPE 9: CRÉATION DE GRAPHIQUES D'ANALYSE
# ==================================================================================
print("\n[ÉTAPE 9] CRÉATION DE GRAPHIQUES D'ANALYSE")
print("-" * 80)

# Graphique 1: Top pays
df_pays = pd.read_sql_query("SELECT * FROM VUE_PAYS ORDER BY Nombre_Entreprises DESC LIMIT 15", conn)
fig, ax = plt.subplots(figsize=(12, 6))
ax.barh(df_pays['Country'], df_pays['Nombre_Entreprises'], color='steelblue')
ax.set_xlabel('Nombre d\'entreprises')
ax.set_title('Top 15 Pays - Adoption GenAI', fontsize=14, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('08_dw_top_pays.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 08_dw_top_pays.png")
plt.close()

# Graphique 2: Par secteur
df_secteur = pd.read_sql_query("""
SELECT Sector_Type, SUM(Nombre_Entreprises) as Total
FROM VUE_INDUSTRIE
GROUP BY Sector_Type
ORDER BY Total DESC
""", conn)
fig, ax = plt.subplots(figsize=(10, 10))
colors = plt.cm.Set3(range(len(df_secteur)))
ax.pie(df_secteur['Total'], labels=df_secteur['Sector_Type'], autopct='%1.1f%%',
       colors=colors, startangle=90)
ax.set_title('Répartition par Type de Secteur', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('09_dw_secteurs.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: 09_dw_secteurs.png")
plt.close()

# Fermer la connexion
conn.close()

print("\n" + "="*80)
print(" ETL ET DATA WAREHOUSE TERMINÉS AVEC SUCCÈS ".center(80, "="))
print("="*80)
print(f"""
Fichiers générés:
  • {db_path} (Data Warehouse SQLite)
  • {output_file} (Dataset pour Power BI)
  • 08_dw_top_pays.png (Analyse pays)
  • 09_dw_secteurs.png (Analyse secteurs)

Structure du Data Warehouse:
  ✓ 1 Table de faits: FAIT_ADOPTION
  ✓ 4 Tables de dimensions: COMPANY, GEOGRAPHY, INDUSTRY, GENAI_TOOL
  ✓ 3 Vues agrégées: VUE_PAYS, VUE_INDUSTRIE, VUE_GENAI_TOOL

Prochaines étapes:
  1. Importer {output_file} dans Power BI Desktop
  2. Ou connecter directement à {db_path} via ODBC/SQLite
  3. Créer les mesures DAX et KPIs
  4. Concevoir le dashboard interactif avec:
     - KPI: Taux d'adoption par région
     - KPI: Impact productivité moyen
     - KPI: Satisfaction employés
     - Visualisations par pays, secteur, outil GenAI
     - Analyse temporelle de l'adoption
""")
print("="*80)
