import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Archivos de entrada
files = [
    "raman paracetamolSSM.xlsx",
    "raman paracetamol2SSM.xlsx",
    "raman paracetamol3SSM.xlsx"
]


laser_wavelength_nm = 646.81  
laser_wavelength_cm = laser_wavelength_nm * 1e-7  

def load_data_sheet(path):
    """Carga la hoja 'data' o la primera hoja. Devuelve DataFrame con columnas ['wavelength','intensity']."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")
    xls = pd.ExcelFile(path)
    sheet = 'data' if 'data' in xls.sheet_names else xls.sheet_names[0]
    
    df = pd.read_excel(xls, sheet_name=sheet, header=0)
    if df.shape[1] >= 2 and not np.issubdtype(df.iloc[:,0].dtype, np.number):
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
    
    wl = pd.to_numeric(df.iloc[:,0], errors='coerce')  # nm
    inten = pd.to_numeric(df.iloc[:,1], errors='coerce')
    df_out = pd.DataFrame({'wavelength_nm': wl, 'intensity': inten}).dropna().reset_index(drop=True)
    return df_out

def compute_raman_shift(df, laser_wavelength_cm):
    """Convierte longitud de onda (nm) a Raman shift (cm^-1)."""
    wl_cm = df['wavelength_nm'] * 1e-7  # nm -> cm
    raman_shift = (1/laser_wavelength_cm - 1/wl_cm)  # cm^-1
    df_out = pd.DataFrame({'raman_shift': raman_shift, 'intensity': df['intensity']})
    return df_out

def plot_raman(dfs, labels):
    """Grafica intensidad vs Raman shift para varios espectros."""
    plt.figure(figsize=(10,6))
    for df, label in zip(dfs, labels):
        plt.plot(df['raman_shift'], df['intensity'], label=label)
    plt.xlabel("Raman shift (cm$^{-1}$)")
    plt.ylabel("Intensidad (u.a.)")
    plt.title("Espectros Raman de Paracetamol")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("raman_paracetamol.png", dpi=300)
    plt.show()
    print("Gráfica guardada en: raman_paracetamol.png")

if __name__ == "__main__":
    dfs = []
    labels = []
    for f in files:
        print(f"Cargando {f}...")
        df = load_data_sheet(f)
        df_raman = compute_raman_shift(df, laser_wavelength_cm)
        dfs.append(df_raman)
        labels.append(os.path.splitext(f)[0])
    
    plot_raman(dfs, labels)
    print("Listo.")

