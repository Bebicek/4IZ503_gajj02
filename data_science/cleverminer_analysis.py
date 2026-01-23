"""
===============================================================================
CLEVERMINER ANALÝZA - POLICEJNÍ STŘELBY V USA
===============================================================================
Projekt: 4IZ503 - Dobývání znalostí z databází

Obsah:
- 2x 4ft-Miner (asociační pravidla)
- 2x CF-Miner (analýza histogramů)  
- 2x SD4ft-Miner (subgroup discovery)
===============================================================================
"""

import pandas as pd
import numpy as np
import os
import sys

# Přesměrování výstupu do souboru
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'cleverminer_output.txt')

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
# ČÁST 1: NAČTENÍ A PROFILOVÁNÍ DAT
# =============================================================================
print("="*80)
print("ČÁST 1: NAČTENÍ A PROFILOVÁNÍ DAT")
print("="*80)

# Cesta k datům
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data_after_cleaning')

# Načtení datasetů
df_shootings = pd.read_csv(os.path.join(DATA_DIR, 'shootings_detailed_categorized.csv'))
df_cities = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_categorized.csv'))

print(f"\n{'='*60}")
print("ZÁKLADNÍ STATISTIKY:")
print(f"{'='*60}")
print(f"   - Počet střeleckých incidentů: {len(df_shootings)}")
print(f"   - Počet měst: {len(df_cities)}")
print(f"   - Počet atributů (shootings): {len(df_shootings.columns)}")
print(f"   - Počet atributů (cities): {len(df_cities.columns)}")

# Profilování kategoriálních proměnných
print(f"\n{'='*60}")
print("PROFILOVÁNÍ KATEGORIÁLNÍCH PROMĚNNÝCH:")
print(f"{'='*60}")

categorical_cols = ['armed_category', 'age_group', 'race_category', 'threat_category', 
                   'mental_illness_flag', 'body_camera_flag', 'budget_category', 
                   'population_size', 'shooting_rate_category', 'gender', 'flee']

for col in categorical_cols:
    if col in df_shootings.columns:
        print(f"\n   {col.upper()}:")
        value_counts = df_shootings[col].value_counts()
        for val, count in value_counts.items():
            pct = count / len(df_shootings) * 100
            print(f"      - {val}: {count} ({pct:.1f}%)")

# =============================================================================
# ČÁST 2: PŘÍPRAVA DAT PRO MINING
# =============================================================================
print("\n" + "="*80)
print("ČÁST 2: PŘÍPRAVA DAT PRO MINING")
print("="*80)

# Vytvoření čistého datasetu pro mining
df_mining = df_shootings.copy()

# Nahrazení prázdných hodnot
df_mining['gender'] = df_mining['gender'].fillna('Unknown')
df_mining['flee'] = df_mining['flee'].fillna('Unknown')
df_mining['age_group'] = df_mining['age_group'].fillna('Unknown')
df_mining['race_category'] = df_mining['race_category'].fillna('Other')

# Výběr relevantních sloupců pro mining
mining_columns = [
    'armed_category',      # Typ zbraně
    'age_group',           # Věková skupina
    'race_category',       # Rasová kategorie
    'threat_category',     # Úroveň hrozby
    'mental_illness_flag', # Duševní onemocnění
    'body_camera_flag',    # Tělesná kamera
    'budget_category',     # Kategorie rozpočtu
    'population_size',     # Velikost města
    'shooting_rate_category', # Kategorie míry střelby
    'gender',              # Pohlaví
    'flee'                 # Způsob útěku
]

df_clean = df_mining[mining_columns].copy()

# Konverze na string (vyžadováno CleverMinerem)
for col in df_clean.columns:
    df_clean[col] = df_clean[col].astype(str)

print(f"\nPřipraveno {len(df_clean)} záznamů s {len(df_clean.columns)} atributy pro mining")

# =============================================================================
# ČÁST 3: 4FT-MINER - ASOCIAČNÍ PRAVIDLA
# =============================================================================
print("\n" + "="*80)
print("ČÁST 3: 4FT-MINER - ASOCIAČNÍ PRAVIDLA")
print("="*80)

try:
    from cleverminer import cleverminer
    
    # =========================================================================
    # ÚLOHA 1: Faktory spojené s duševním onemocněním
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 1: Jaké okolnosti vedou k DUŠEVNÍMU ONEMOCNĚNÍ u obětí?")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Najít okolnosti, za kterých je u obětí policejní střelby častěji 
přítomen signál duševního onemocnění (mental_illness_flag = 'Yes').

KVANTIFIKÁTORY:
- Base >= 15 (minimálně 15 případů)
- AAD >= 0.3 (pravděpodobnost vyšší o 30% oproti průměru)
""")
    
    clm1 = cleverminer(
        df=df_clean,
        proc='4ftMiner',
        quantifiers={'Base': 15, 'aad': 0.3},
        ante={
            'attributes': [
                {'name': 'race_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                {'name': 'age_group', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                {'name': 'population_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            ],
            'minlen': 1,
            'maxlen': 2,
            'type': 'con'
        },
        succ={
            'attributes': [
                {'name': 'mental_illness_flag', 'type': 'one', 'value': 'Yes'}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 1:")
    clm1.print_summary()
    clm1.print_rulelist()
    
    # =========================================================================
    # ÚLOHA 2: Faktory spojené s vysokou mírou střelby
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 2: Jaké faktory jsou spojeny s VYSOKOU MÍROU STŘELBY?")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Identifikovat charakteristiky spojené s vysokou mírou 
policejních střelb na 100 000 obyvatel.

KVANTIFIKÁTORY:
- Base >= 20
- AAD >= 0.2
""")
    
    clm2 = cleverminer(
        df=df_clean,
        proc='4ftMiner',
        quantifiers={'Base': 20, 'aad': 0.2},
        ante={
            'attributes': [
                {'name': 'race_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                {'name': 'budget_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                {'name': 'armed_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            ],
            'minlen': 1,
            'maxlen': 2,
            'type': 'con'
        },
        succ={
            'attributes': [
                {'name': 'shooting_rate_category', 'type': 'one', 'value': 'High_Rate'}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 2:")
    clm2.print_summary()
    clm2.print_rulelist()

    # =========================================================================
    # ČÁST 4: CF-MINER - ANALÝZA HISTOGRAMŮ
    # =========================================================================
    print("\n" + "="*80)
    print("ČÁST 4: CF-MINER - ANALÝZA HISTOGRAMŮ")
    print("="*80)
    
    # =========================================================================
    # ÚLOHA 3: Distribuce typu zbraně podle rasy
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 3: Liší se DISTRIBUCE TYPU ZBRANĚ podle rasy?")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Najít podmínky, za kterých se histogram (distribuce) typu zbraně 
liší od celkového průměru.

KVANTIFIKÁTORY:
- S_Down >= 1 (alespoň jeden krok dolů v histogramu)
- Base >= 30
""")
    
    clm3 = cleverminer(
        df=df_clean,
        target='armed_category',
        proc='CFMiner',
        quantifiers={'S_Down': 1, 'Base': 30},
        cond={
            'attributes': [
                {'name': 'race_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 3:")
    clm3.print_summary()
    clm3.print_rulelist()
    
    # =========================================================================
    # ÚLOHA 4: Distribuce věku podle velikosti města
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 4: Liší se VĚKOVÁ STRUKTURA podle velikosti města?")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Zjistit, jak se liší věková struktura obětí v závislosti 
na velikosti města.

KVANTIFIKÁTORY:
- S_Down >= 1
- Base >= 50
""")
    
    clm4 = cleverminer(
        df=df_clean,
        target='age_group',
        proc='CFMiner',
        quantifiers={'S_Down': 1, 'Base': 50},
        cond={
            'attributes': [
                {'name': 'population_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 4:")
    clm4.print_summary()
    clm4.print_rulelist()

    # =========================================================================
    # ČÁST 5: SD4FT-MINER - SUBGROUP DISCOVERY
    # =========================================================================
    print("\n" + "="*80)
    print("ČÁST 5: SD4FT-MINER - SUBGROUP DISCOVERY")
    print("="*80)
    
    # =========================================================================
    # ÚLOHA 5: Rozdíly v použití body kamer
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 5: Rozdíly v POUŽITÍ BODY KAMER mezi velikostmi měst")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Najít situace, kde se pravděpodobnost použití body kamery
výrazně liší mezi různými velikostmi měst.

KVANTIFIKÁTORY:
- Base1 >= 20, Base2 >= 20
- Ratioconf >= 1.1
""")
    
    clm5 = cleverminer(
        df=df_clean,
        proc='SD4ftMiner',
        quantifiers={'Base1': 20, 'Base2': 20, 'Ratioconf': 1.1},
        ante={
            'attributes': [],
            'minlen': 0,
            'maxlen': 0,
            'type': 'con'
        },
        succ={
            'attributes': [
                {'name': 'body_camera_flag', 'type': 'one', 'value': 'Yes'}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        },
        frst={
            'attributes': [
                {'name': 'population_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        },
        scnd={
            'attributes': [
                {'name': 'population_size', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 5:")
    clm5.print_summary()
    clm5.print_rulelist()
    
    # =========================================================================
    # ÚLOHA 6: Neozbrojené oběti podle rasy
    # =========================================================================
    print("\n" + "-"*60)
    print("ÚLOHA 6: Rozdíly v podílu NEOZBROJENÝCH OBĚTÍ podle rasy")
    print("-"*60)
    
    print("""
ZADÁNÍ:
-------
Cíl: Zjistit, zda existují rozdíly v podílu neozbrojených obětí
mezi různými rasovými skupinami.

KVANTIFIKÁTORY:
- Base1 >= 15, Base2 >= 15
- Ratioconf >= 1.1
""")
    
    clm6 = cleverminer(
        df=df_clean,
        proc='SD4ftMiner',
        quantifiers={'Base1': 15, 'Base2': 15, 'Ratioconf': 1.1},
        ante={
            'attributes': [],
            'minlen': 0,
            'maxlen': 0,
            'type': 'con'
        },
        succ={
            'attributes': [
                {'name': 'armed_category', 'type': 'one', 'value': 'Unarmed'}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        },
        frst={
            'attributes': [
                {'name': 'race_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        },
        scnd={
            'attributes': [
                {'name': 'race_category', 'type': 'subset', 'minlen': 1, 'maxlen': 1}
            ],
            'minlen': 1,
            'maxlen': 1,
            'type': 'con'
        }
    )
    
    print("\nVÝSLEDKY ÚLOHY 6:")
    clm6.print_summary()
    clm6.print_rulelist()

except ImportError as e:
    print(f"\nCHYBA: CleverMiner není nainstalován: {e}")
    print("Instalujte pomocí: pip install cleverminer")

# Uzavření výstupního souboru
output_file.close()
sys.stdout = sys.__stdout__
print(f"Výstup uložen do: {OUTPUT_FILE}")

