"""
===============================================================================
MACHINE LEARNING ANALÝZA - POLICEJNÍ STŘELBY V USA
===============================================================================
Projekt: 4IZ503 - Dobývání znalostí z databází

Obsah:
- Kontingenční tabulky a Chi-square testy
- Random Forest s Feature Importance
===============================================================================
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
import os
import sys

warnings.filterwarnings('ignore')

# Přesměrování výstupu do souboru
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'ml_analysis_output.txt')

class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
    def flush(self):
        for f in self.files:
            f.flush()

output_file = open(OUTPUT_FILE, 'w', encoding='utf-8')
sys.stdout = Tee(sys.__stdout__, output_file)

# =============================================================================
# ČÁST 1: NAČTENÍ DAT
# =============================================================================
print("="*80)
print("MACHINE LEARNING ANALÝZA - POLICEJNÍ STŘELBY V USA")
print("="*80)

DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data_after_cleaning')

df_shootings = pd.read_csv(os.path.join(DATA_DIR, 'shootings_detailed_categorized.csv'))

print(f"\nNačteno {len(df_shootings)} záznamů")

# Příprava dat
df_clean = df_shootings.copy()
df_clean['gender'] = df_clean['gender'].fillna('Unknown')
df_clean['flee'] = df_clean['flee'].fillna('Unknown')
df_clean['age_group'] = df_clean['age_group'].fillna('Unknown')
df_clean['race_category'] = df_clean['race_category'].fillna('Other')

for col in df_clean.columns:
    df_clean[col] = df_clean[col].astype(str)

# =============================================================================
# ČÁST 2: KONTINGENČNÍ TABULKY A CHI-SQUARE TESTY
# =============================================================================
print("\n" + "="*80)
print("ČÁST 2: KONTINGENČNÍ TABULKY A CHI-SQUARE TESTY")
print("="*80)

def analyze_contingency(df, var1, var2, title):
    """Analýza kontingenční tabulky s chi-square testem."""
    print(f"\n{'-'*60}")
    print(f"{title}")
    print(f"{'-'*60}")
    
    contingency = pd.crosstab(df[var1], df[var2])
    print(f"\nKONTINGENČNÍ TABULKA ({var1} vs {var2}):")
    print(contingency)
    
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    print(f"\nCHI-SQUARE TEST:")
    print(f"   Chi2 statistika: {chi2:.4f}")
    print(f"   p-hodnota: {p_value:.6f}")
    print(f"   Stupně volnosti: {dof}")
    
    if p_value < 0.05:
        print(f"   --> STATISTICKY VÝZNAMNÝ VZTAH (p < 0.05)")
    else:
        print(f"   --> Není statisticky významný")
    
    # Cramerovo V
    n = contingency.sum().sum()
    min_dim = min(contingency.shape[0] - 1, contingency.shape[1] - 1)
    cramer_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
    print(f"   Cramerovo V (síla vztahu): {cramer_v:.4f}")
    
    return contingency, cramer_v

# Analýzy vztahů
ct1, cv1 = analyze_contingency(df_clean, 'race_category', 'armed_category', 
                                "VZTAH 1: Rasa oběti vs Typ zbraně")

ct2, cv2 = analyze_contingency(df_clean, 'age_group', 'mental_illness_flag',
                                "VZTAH 2: Věková skupina vs Duševní onemocnění")

ct3, cv3 = analyze_contingency(df_clean, 'population_size', 'shooting_rate_category',
                                "VZTAH 3: Velikost města vs Míra střelby")

ct4, cv4 = analyze_contingency(df_clean, 'budget_category', 'body_camera_flag',
                                "VZTAH 4: Rozpočet policie vs Použití body kamery")

ct5, cv5 = analyze_contingency(df_clean, 'race_category', 'shooting_rate_category',
                                "VZTAH 5: Rasa oběti vs Míra střelby")

# =============================================================================
# ČÁST 3: RANDOM FOREST - PREDIKTIVNÍ MODEL
# =============================================================================
print("\n" + "="*80)
print("ČÁST 3: RANDOM FOREST - PREDIKTIVNÍ MODEL")
print("="*80)

# Příprava dat pro ML
df_ml = df_clean.copy()
label_encoders = {}

for col in df_ml.columns:
    le = LabelEncoder()
    df_ml[col] = le.fit_transform(df_ml[col].astype(str))
    label_encoders[col] = le

print("\n" + "-"*60)
print("Model: Predikce vysoké míry střelby")
print("-"*60)

y_rate = (df_clean['shooting_rate_category'] == 'High_Rate').astype(int)
cols_to_drop = ['shooting_rate_category', 'id', 'name', 'date', 
                'city_clean', 'state_clean', 'city_state',
                'race', 'armed', 'threat_level', 'manner_of_death',
                'signs_of_mental_illness', 'body_camera']
cols_to_drop = [c for c in cols_to_drop if c in df_ml.columns]
X_rate = df_ml.drop(cols_to_drop, axis=1)

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_rate, y_rate, test_size=0.3, random_state=42
)

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    min_samples_split=30,
    random_state=42
)
rf_model.fit(X_train_r, y_train_r)

print(f"\nVÝSLEDKY RANDOM FOREST:")
print(f"   Přesnost na trénovacích datech: {rf_model.score(X_train_r, y_train_r):.3f}")
print(f"   Přesnost na testovacích datech: {rf_model.score(X_test_r, y_test_r):.3f}")

print(f"\nFEATURE IMPORTANCE:")
rf_importance = pd.DataFrame({
    'Feature': X_rate.columns,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

for _, row in rf_importance.iterrows():
    bar = "█" * int(row['Importance'] * 30)
    print(f"   {row['Feature']:25s} {bar} {row['Importance']:.4f}")

# Uzavření výstupního souboru
output_file.close()
sys.stdout = sys.__stdout__
print(f"Výstup uložen do: {OUTPUT_FILE}")

