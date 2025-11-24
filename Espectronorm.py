
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


file_particles = r"espectro nanoparticulasSSM.xlsx"
file_background = r"espectro luz de fondoSSM.xlsx"

def load_data_sheet(path):
    xls = pd.ExcelFile(path)
    sheet = 'data' if 'data' in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=sheet, header=None)
    if df.shape[1] < 2:
        raise ValueError(f"La hoja '{sheet}' no tiene suficientes columnas en {path}.")
    wl = pd.to_numeric(df.iloc[:,0], errors='coerce')
    inten = pd.to_numeric(df.iloc[:,1], errors='coerce')
    return pd.DataFrame({'wavelength': wl, 'intensity': inten}).dropna()

def normalize(series):
    arr = np.array(series, dtype=float)
    m = np.nanmax(np.abs(arr))
    return arr / m if (m and not np.isnan(m)) else arr

if __name__ == "__main__":
    df_p = load_data_sheet(file_particles)
    df_b = load_data_sheet(file_background)

    df_p['int_norm'] = normalize(df_p['intensity'])
    df_b['int_norm'] = normalize(df_b['intensity'])

    wl_min = min(df_p['wavelength'].min(), df_b['wavelength'].min())
    wl_max = max(df_p['wavelength'].max(), df_b['wavelength'].max())
    wl_grid = np.linspace(wl_min, wl_max, 2000)

    p_interp = np.interp(wl_grid, df_p['wavelength'], df_p['int_norm'], left=np.nan, right=np.nan)
    b_interp = np.interp(wl_grid, df_b['wavelength'], df_b['int_norm'], left=np.nan, right=np.nan)

    plt.figure(figsize=(10,6))
    plt.plot(wl_grid, b_interp, label='Luz de fondo (normalizada)')
    plt.plot(wl_grid, p_interp, label='Luz transmitida a través de AuNPs (normalizada)')
    plt.xlabel('Longitud de onda (nm)')
    plt.ylabel('Intensidad normalizada (a.u.)')
    plt.title('Superposición de espectros (normalizados vs. valor máximo)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    out_png = "spectra_overlay.png"
    plt.savefig(out_png, dpi=300)
    plt.show()
    print("Figura guardada en:", out_png)
