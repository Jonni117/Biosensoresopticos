import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = "2025-04-23 Au NP Biosensores espectro.xlsx"
xls = pd.read_excel(file_path, sheet_name=None)
first_sheet = list(xls.keys())[0]
df_raw = xls[first_sheet].copy()
df = df_raw.apply(pd.to_numeric, errors='coerce')


wavelength_col = None
candidates = []
for col in df.columns:
    s = df[col].dropna()
    if s.shape[0] >= 5 and s.is_monotonic_increasing:
        candidates.append((col, s.shape[0]))
if candidates:
    candidates.sort(key=lambda x: x[1], reverse=True)
    wavelength_col = candidates[0][0]
else:
    numeric_counts = [(col, df[col].dropna().shape[0]) for col in df.columns if df[col].dropna().shape[0] > 0]
    numeric_counts.sort(key=lambda x: x[1], reverse=True)
    wavelength_col = numeric_counts[0][0]

wavelength = df[wavelength_col]
other_cols = [c for c in df.columns if c != wavelength_col and df[c].dropna().shape[0] > 0]


renames = {col: f"Columna {i+1}" for i, col in enumerate(other_cols)}
df = df.rename(columns=renames)
other_cols = [renames[col] for col in other_cols] 


plt.figure(figsize=(9,6))
for col in other_cols:
    mask = wavelength.notna() & df[col].notna()
    if mask.sum() == 0:
        continue
    plt.plot(wavelength[mask], df[col][mask], label=str(col)) 

plt.xlabel("Longitud de onda (nm)")
plt.ylabel("Absorbancia (u.a.)")
plt.title(f"Espectros - hoja: {first_sheet} (λ detectada: '{wavelength_col}')")
plt.legend(title="Espectros")
plt.grid(True)
plt.tight_layout()
plt.savefig("Espectros_superpuestos_columna.png")
plt.show()
print("Espectros_superpuestos_columna.png")
