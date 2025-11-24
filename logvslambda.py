import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


file_particles = "espectro nanoparticulasSSM.xlsx"
file_background = "espectro luz de fondoSSM.xlsx"


output_excel = "absorbancia_resultados.xlsx"
output_png = "absorbancia_vs_lambda.png"
use_ln = True        
replace_nonpositive = True  
epsilon = 1e-12      
n_points = 2000      

def load_data_sheet(path):
    """Carga la hoja 'data' del xlsx o la primera hoja. Devuelve DataFrame con columnas ['wavelength','intensity']."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")
    xls = pd.ExcelFile(path)
    sheet = 'data' if 'data' in xls.sheet_names else xls.sheet_names[0]
    
    df = pd.read_excel(xls, sheet_name=sheet, header=0)
   
    if df.shape[1] >= 2 and not np.issubdtype(df.iloc[:,0].dtype, np.number):
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
    
    wl = pd.to_numeric(df.iloc[:,0], errors='coerce')
    inten = pd.to_numeric(df.iloc[:,1], errors='coerce')
    df_out = pd.DataFrame({'wavelength': wl, 'intensity': inten}).dropna().reset_index(drop=True)
    return df_out

def compute_absorbance(df_I0, df_I, use_ln=False, replace_nonpositive=True, epsilon=1e-12, n_points=2000):
    """Interpola ambos espectros a una malla común y calcula A = log(I0/I) (base10 por defecto)."""
    wl_min = max(df_I0['wavelength'].min(), df_I['wavelength'].min())
    wl_max = min(df_I0['wavelength'].max(), df_I['wavelength'].max())
    if wl_min >= wl_max:
        raise ValueError("Los rangos de longitud de onda de I0 e I no se solapan correctamente.")
    wl_grid = np.linspace(wl_min, wl_max, n_points)

    I0_interp = np.interp(wl_grid, df_I0['wavelength'], df_I0['intensity'], left=np.nan, right=np.nan)
    I_interp  = np.interp(wl_grid, df_I['wavelength'],   df_I['intensity'],  left=np.nan, right=np.nan)

    
    if replace_nonpositive:
        I0_safe = np.where(I0_interp <= 0, epsilon, I0_interp)
        I_safe  = np.where(I_interp  <= 0, epsilon, I_interp)
    else:
        # dejar valores no físicos como NaN para que el usuario los trate
        I0_safe = np.where(I0_interp <= 0, np.nan, I0_interp)
        I_safe  = np.where(I_interp  <= 0, np.nan, I_interp)

    
    ratio = I0_safe / I_safe
    with np.errstate(divide='ignore', invalid='ignore'):
        if use_ln:
            A = np.log(ratio)         # ln(I0/I)
        else:
            A = np.log10(ratio)       # log10(I0/I) -> absorbancia

    out_df = pd.DataFrame({
        'wavelength': wl_grid,
        'I0': I0_interp,
        'I': I_interp,
        'I0_safe': I0_safe,
        'I_safe': I_safe,
        'absorbance': A
    })
    return out_df

def plot_absorbance(out_df, output_png, use_ln=False):
    """Grafica absorbancia vs longitud de onda y guarda la figura."""
    plt.figure(figsize=(10,6))
    label = "ln(I0/I)" if use_ln else "log10(I0/I) (absorbancia)"
    plt.plot(out_df['wavelength'], out_df['absorbance'], label=label)
    plt.xlabel("Longitud de onda nm")
    plt.ylabel(label)
    plt.title(f"{label} vs. longitud de onda")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.show()
    print("Gráfica guardada en:", output_png)

if __name__ == "__main__":
    
    print("Cargando archivos...")
    df_p = load_data_sheet(file_particles)   # I (muestra)
    df_b = load_data_sheet(file_background)  # I0 (blanco / fondo)

    
    print(f"Lecturas: partículas={len(df_p)} filas, fondo={len(df_b)} filas")

    
    results = compute_absorbance(df_b, df_p, use_ln=use_ln,
                                 replace_nonpositive=replace_nonpositive,
                                 epsilon=epsilon,
                                 n_points=n_points)

    
    print("Guardando resultados a Excel...")
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        results.to_excel(writer, sheet_name='absorbancia', index=False)
        df_b.to_excel(writer, sheet_name='I0_background', index=False)
        df_p.to_excel(writer, sheet_name='I_particles', index=False)
    print("Excel guardado en:", output_excel)

    
    plot_absorbance(results, output_png, use_ln=use_ln)

    print("Listo.")
