"""
rebalance_trends.py
Shifts Market Trends distribution so that "Stable" is dominant (~55%).

Before: Declining=417 (34.75%), Stable=405 (33.75%), Rising=378 (31.5%)
After:  Stable≈660 (55%),  Declining≈300 (25%), Rising≈240 (20%)

Strategy:
  - Keep a backup of the original CSV.
  - Use random sampling (with seed for reproducibility) to flip rows:
      * Pick 255 random Declining rows → convert to Stable
      * Pick 138 random Rising rows   → convert to Stable
  That gives Stable = 405 + 255 + 138 = 798... too many.
  
  More precise calculation:
    Target Stable = 660, current = 405 → need +255 more
    Shrink Declining from 417 → 300 (take 117 from Declining)
    Shrink Rising   from 378 → 240 (take 138 from Rising)
    117 + 138 = 255 ✓  →  Stable = 405 + 255 = 660 (55%)
"""

import pandas as pd
import shutil
import os

DATA_FILE = 'tamilnadu_house_data.csv'
BACKUP_FILE = 'tamilnadu_house_data_original_backup.csv'

# 1. Back up original
if not os.path.exists(BACKUP_FILE):
    shutil.copy(DATA_FILE, BACKUP_FILE)
    print(f"✅ Backup saved as: {BACKUP_FILE}")
else:
    print(f"ℹ️  Backup already exists at: {BACKUP_FILE}")

# 2. Load data
df = pd.read_csv(DATA_FILE)
print("\n--- Before ---")
print(df['Market Trends'].value_counts())
print(f"Total rows: {len(df)}")

# 3. Randomly pick rows to flip (with fixed seed for reproducibility)
SEED = 99

# From Declining → Stable: pick 117 Declining rows
declining_idx = df[df['Market Trends'] == 'Declining'].index.tolist()
rising_idx    = df[df['Market Trends'] == 'Rising'].index.tolist()

import random
random.seed(SEED)

n_from_declining = 117
n_from_rising    = 138

flip_declining = random.sample(declining_idx, n_from_declining)
flip_rising    = random.sample(rising_idx,    n_from_rising)

df.loc[flip_declining, 'Market Trends'] = 'Stable'
df.loc[flip_rising,    'Market Trends'] = 'Stable'

# 4. Verify
print("\n--- After ---")
counts = df['Market Trends'].value_counts()
print(counts)
total = len(df)
for trend, count in counts.items():
    print(f"  {trend}: {count} ({count/total*100:.1f}%)")

# 5. Save
df.to_csv(DATA_FILE, index=False)
print(f"\n✅ Updated dataset saved to: {DATA_FILE}")
print("   Now restart app.py for the Flask backend to retrain with the new distribution.")
