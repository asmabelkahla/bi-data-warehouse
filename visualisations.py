# -*- coding: utf-8 -*-
"""
Visualisations et analyses pour le projet BI
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Charger les données
conn = sqlite3.connect('/home/claude/datawarehouse_medical.db')
df_clean = pd.read_csv('/home/claude/donnees_nettoyees_powerbi.csv')

print("="*80)
print(" ANALYSES ET VISUALISATIONS ".center(80, "="))
print("="*80)

# ==================================================================================
# ANALYSE 1: Distribution par catégorie d'âge
# ==================================================================================
print("\n[ANALYSE 1] Distribution par catégorie d'âge")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribution des patients
age_dist = df_clean['Categorie_Age'].value_counts().sort_index()
axes[0].bar(range(len(age_dist)), age_dist.values, color='steelblue')
axes[0].set_xticks(range(len(age_dist)))
axes[0].set_xticklabels(age_dist.index, rotation=45)
axes[0].set_title('Distribution des patients par catégorie d\'âge')
axes[0].set_ylabel('Nombre de patients')
axes[0].grid(axis='y', alpha=0.3)

# Douleur initiale par âge
age_pain = df_clean.groupby('Categorie_Age')['EN0'].mean().sort_index()
axes[1].bar(range(len(age_pain)), age_pain.values, color='coral')
axes[1].set_xticks(range(len(age_pain)))
axes[1].set_xticklabels(age_pain.index, rotation=45)
axes[1].set_title('Douleur initiale moyenne par catégorie d\'âge')
axes[1].set_ylabel('Score EN0 moyen')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/viz_1_age_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_1_age_distribution.png")
plt.close()

# ==================================================================================
# ANALYSE 2: Évolution de la douleur dans le temps
# ==================================================================================
print("\n[ANALYSE 2] Évolution de la douleur dans le temps")
fig, ax = plt.subplots(figsize=(12, 6))

pain_cols = ['EN0', 'EN_15min', 'EN_30min', 'EN_45min', 'EN_60min', 'EN_90min']
time_points = [0, 15, 30, 45, 60, 90]

# Moyenne et écart-type
mean_pain = df_clean[pain_cols].mean()
std_pain = df_clean[pain_cols].std()

ax.plot(time_points, mean_pain, marker='o', linewidth=2, markersize=8, 
        color='darkblue', label='Douleur moyenne')
ax.fill_between(time_points, 
                mean_pain - std_pain, 
                mean_pain + std_pain, 
                alpha=0.3, color='lightblue', label='±1 écart-type')

ax.set_xlabel('Temps (minutes)', fontsize=12)
ax.set_ylabel('Score de douleur (EN)', fontsize=12)
ax.set_title('Évolution de la douleur au cours du temps', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig('/home/claude/viz_2_pain_evolution.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_2_pain_evolution.png")
plt.close()

# ==================================================================================
# ANALYSE 3: Comparaison des traitements
# ==================================================================================
print("\n[ANALYSE 3] Efficacité des traitements")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

treatments = ['AINS', 'Paracétamol', 'Titration_morphinique']
treatment_labels = ['AINS', 'Paracétamol', 'Morphine']

for idx, (treatment, label) in enumerate(zip(treatments, treatment_labels)):
    if treatment in df_clean.columns:
        variation_by_treatment = df_clean.groupby(treatment)['Variation_douleur'].mean()
        
        axes[idx].bar(['Non traité', 'Traité'], 
                     [variation_by_treatment.get(0, 0), variation_by_treatment.get(1, 0)],
                     color=['lightcoral', 'lightgreen'])
        axes[idx].set_title(f'Effet de {label} sur la douleur')
        axes[idx].set_ylabel('Variation moyenne de la douleur')
        axes[idx].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        axes[idx].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/viz_3_treatment_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_3_treatment_comparison.png")
plt.close()

# ==================================================================================
# ANALYSE 4: Distribution des comorbidités
# ==================================================================================
print("\n[ANALYSE 4] Analyse des comorbidités")
fig, ax = plt.subplots(figsize=(10, 6))

comorbidity_cols = ['Diabète', 'HTA', 'Dyslipidémie', 'FA', 'Insuffisance_rénale', 
                     'BPCO', 'Asthme', 'UGD']
available_cols = [col for col in comorbidity_cols if col in df_clean.columns]

comorbidity_counts = df_clean[available_cols].sum().sort_values(ascending=True)

ax.barh(range(len(comorbidity_counts)), comorbidity_counts.values, color='teal')
ax.set_yticks(range(len(comorbidity_counts)))
ax.set_yticklabels(comorbidity_counts.index)
ax.set_xlabel('Nombre de patients', fontsize=12)
ax.set_title('Prévalence des comorbidités', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/viz_4_comorbidities.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_4_comorbidities.png")
plt.close()

# ==================================================================================
# ANALYSE 5: Matrice de corrélation des scores de douleur
# ==================================================================================
print("\n[ANALYSE 5] Corrélations entre scores de douleur")
fig, ax = plt.subplots(figsize=(10, 8))

pain_correlation = df_clean[pain_cols].corr()

sns.heatmap(pain_correlation, annot=True, fmt='.2f', cmap='coolwarm', 
            center=0.8, vmin=0, vmax=1, square=True, ax=ax,
            cbar_kws={'label': 'Coefficient de corrélation'})
ax.set_title('Corrélations entre les scores de douleur', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/claude/viz_5_pain_correlation.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_5_pain_correlation.png")
plt.close()

# ==================================================================================
# ANALYSE 6: Résultats cliniques
# ==================================================================================
print("\n[ANALYSE 6] Résultats cliniques")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Amélioration de la douleur
amelioration_counts = df_clean['Amelioration_douleur'].value_counts()
axes[0, 0].pie(amelioration_counts, labels=['Amélioration modérée', 'Amélioration significative'],
               autopct='%1.1f%%', colors=['lightyellow', 'lightgreen'])
axes[0, 0].set_title('Amélioration de la douleur (>2 points)')

# Évolution
if 'Evolution_amélioration' in df_clean.columns:
    evolution_counts = df_clean['Evolution_amélioration'].value_counts()
    axes[0, 1].bar(['Non amélioré', 'Amélioré'], 
                   [evolution_counts.get(0, 0), evolution_counts.get(1, 0)],
                   color=['salmon', 'lightgreen'])
    axes[0, 1].set_title('Évolution globale')
    axes[0, 1].set_ylabel('Nombre de patients')
    axes[0, 1].grid(axis='y', alpha=0.3)

# Retour à domicile vs Hospitalisation
outcomes = ['Retour_à_domicile', 'Hospitalisation']
outcome_data = []
outcome_labels = []
for outcome in outcomes:
    if outcome in df_clean.columns:
        count = df_clean[outcome].sum()
        outcome_data.append(count)
        outcome_labels.append(outcome.replace('_', ' '))

if outcome_data:
    axes[1, 0].bar(outcome_labels, outcome_data, color=['green', 'orange'])
    axes[1, 0].set_title('Issue de la consultation')
    axes[1, 0].set_ylabel('Nombre de patients')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(axis='y', alpha=0.3)

# Type de colique néphrétique
cn_types = ['CN_simple', 'CN_compliquée']
cn_data = []
cn_labels = []
for cn_type in cn_types:
    if cn_type in df_clean.columns:
        count = df_clean[cn_type].sum()
        cn_data.append(count)
        cn_labels.append(cn_type.replace('_', ' '))

if cn_data:
    axes[1, 1].bar(cn_labels, cn_data, color=['skyblue', 'crimson'])
    axes[1, 1].set_title('Types de colique néphrétique')
    axes[1, 1].set_ylabel('Nombre de cas')
    axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/viz_6_clinical_outcomes.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: viz_6_clinical_outcomes.png")
plt.close()

# ==================================================================================
# STATISTIQUES RÉCAPITULATIVES
# ==================================================================================
print("\n" + "="*80)
print(" STATISTIQUES RÉCAPITULATIVES ".center(80, "="))
print("="*80)

stats_summary = f"""
DÉMOGRAPHIE:
  • Nombre total de patients: {len(df_clean)}
  • Âge moyen: {df_clean['Age'].mean():.1f} ans (±{df_clean['Age'].std():.1f})
  • Âge min/max: {df_clean['Age'].min():.0f} - {df_clean['Age'].max():.0f} ans

DOULEUR:
  • Score initial (EN0): {df_clean['EN0'].mean():.2f} (±{df_clean['EN0'].std():.2f})
  • Score final (EN_90min): {df_clean['EN_90min'].mean():.2f} (±{df_clean['EN_90min'].std():.2f})
  • Variation moyenne: {df_clean['Variation_douleur'].mean():.2f}
  • Amélioration significative: {(df_clean['Amelioration_douleur']==1).sum()} patients ({(df_clean['Amelioration_douleur']==1).sum()/len(df_clean)*100:.1f}%)

TRAITEMENTS:
  • AINS: {df_clean['AINS'].sum()} patients ({df_clean['AINS'].sum()/len(df_clean)*100:.1f}%)
  • Paracétamol: {df_clean['Paracétamol'].sum()} patients ({df_clean['Paracétamol'].sum()/len(df_clean)*100:.1f}%)
  • Morphine: {df_clean['Titration_morphinique'].sum()} patients ({df_clean['Titration_morphinique'].sum()/len(df_clean)*100:.1f}%)

COMORBIDITÉS:
  • Score moyen: {df_clean['Score_comorbidite'].mean():.2f}
  • Patients avec comorbidités: {(df_clean['Score_comorbidite']>0).sum()} ({(df_clean['Score_comorbidite']>0).sum()/len(df_clean)*100:.1f}%)
"""

print(stats_summary)

# Sauvegarder les statistiques
with open('/home/claude/statistiques_resumees.txt', 'w', encoding='utf-8') as f:
    f.write(stats_summary)
print("\n✓ Statistiques sauvegardées: statistiques_resumees.txt")

conn.close()

print("\n" + "="*80)
print(" ANALYSES ET VISUALISATIONS TERMINÉES ".center(80, "="))
print("="*80)
print(f"""
Fichiers générés:
  • viz_1_age_distribution.png
  • viz_2_pain_evolution.png
  • viz_3_treatment_comparison.png
  • viz_4_comorbidities.png
  • viz_5_pain_correlation.png
  • viz_6_clinical_outcomes.png
  • statistiques_resumees.txt
""")
