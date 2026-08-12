import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Selección de Materiales - Ing. Química",
    page_icon="🧪",
    layout="wide"
)

# Estilo visual limpio y profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 Asistente Inteligente para la Selección de Materiales de Construcción")
st.markdown("""
*Herramienta basada en heurísticas de ingeniería química (Art. James J. Briem / CPI) y normativas ASME / API para equipos de procesos, recipientes a presión y gasoductos.*
""")

# ==========================================
# BASE DE DATOS DE COMPATIBILIDAD Y MATERIALES
# ==========================================
@st.cache_data
def load_compatibility_data():
    data = {
        "Sustancia": [
            "Ácido Acético (80%)", "Ácido Sulfúrico (93-98%)", "Ácido Clorhídrico (37%)", 
            "Hidróxido de Sodio (50%)", "Agua de Mar / Salmuera", "Agua (Limpia / Calderas)", 
            "Acetona", "Clasificación General Hidrocarburos / Gas Natural"
        ],
        "Acero al Carbón": ["C", "B", "D", "A", "C", "C", "A", "A"],
        "Acero Inox 304": ["A", "D", "D", "A", "C", "B", "A", "A"],
        "Acero Inox 316": ["A", "D", "D", "A", "B", "A", "A", "A"],
        "Titanio": ["A", "D", "D", "A", "A", "A", "D", "A"],
        "Hastelloy C": ["A", "A", "B", "A", "A", "A", "A", "A"],
        "PVC (Type 1)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "Polipropileno (PP)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "PTFE (Teflon)": ["A", "A", "A", "A", "A", "A", "A", "A"],
        "Viton": ["A", "D", "D", "B", "A", "A", "D", "A"]
    }
    return pd.DataFrame(data)

df_comp = load_compatibility_data()

# ==========================================
# BARRA LATERAL - ENTRADA DE DATOS DEL USUARIO
# ==========================================
st.sidebar.header("⚙️ Parámetros de Operación")

tipo_equipo = st.sidebar.selectbox(
    "Tipo de Equipo / Instalación",
    [
        "Recipiente a Presión (ASME Sec. VIII)", 
        "Tanque de Almacenamiento Atmosférico (API 650)", 
        "Gasoducto / Línea de Conducción", 
        "Intercambiador de Calor", 
        "Bomba / Agitador (Operación Dinámica)", 
        "Otro Equipo de Proceso"
    ]
)

sustancia = st.sidebar.selectbox(
    "Sustancia / Medio de Contacto Principal",
    df_comp["Sustancia"].tolist()
)

temp = st.sidebar.slider("Temperatura de Diseño (°C)", -20, 400, 25)
presion = st.sidebar.number_input("Presión de Diseño (bar)", min_value=0.0, value=10.0, step=1.0)

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    fluido_limpio = st.radio("¿Fluido Limpio?", ["Sí", "No (Abrasivo/Socio)"])
with col_s2:
    es_corrosivo = st.radio("¿Ambiente Corrosivo?", ["No", "Sí"])

# ==========================================
# PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Selección de Materiales", 
    "📐 Diseño Mecánico (Espesor)", 
    "💡 Heurísticas & Alertas CPI", 
    "🚀 Guía GitHub & Streamlit"
])

# --- TAB 1: SELECCIÓN Y COMPATIBILIDAD ---
with tab1:
    st.subheader(f"Evaluación para: {tipo_equipo}")
    st.markdown(f"**Sustancia analizada:** `{sustancia}` | **Temperatura:** `{temp} °C` | **Presión:** `{presion} bar`")
    
    # Filtrar fila de la sustancia
    fila_sustancia = df_comp[df_comp["Sustancia"] == sustancia].iloc[0]
    
    resultados = []
    for material in df_comp.columns[1:]:
        calificacion = fila_sustancia[material]
        
        # Lógica heurística de ajuste por temperatura y condiciones
        nota_extra = "Condiciones normales de operación."
        
        # Restricciones térmicas heurísticas de plásticos / aceros
        if material in ["PVC (Type 1)", "Polipropileno (PP)"] and temp > 60:
            if calificacion == "A":
                calificacion = "C"
            nota_extra = "⚠️ Precaución: La temperatura supera el límite recomendado para plásticos estándar (~60-70°C)."
        
        if material == "Acero al Carbón" and temp > 400:
            calificacion = "D"
            nota_extra = "❌ El acero al carbón pierde resistencia mecánica a temperaturas > 400°C (fluencia/creep)."
            
        resultados.append({
            "Material": material,
            "Resistencia Química (A/B/C/D)": calificacion,
            "Observación Heurística": nota_extra
        })
    
    df_res = pd.DataFrame(resultados)
    
    # Función para dar color a la tabla
    def color_ratings(val):
        color = 'background-color: #d4edda' if val == 'A' else ('background-color: #fff3cd' if val == 'B' else ('background-color: #ffeeba' if val == 'C' else 'background-color: #f8d7da'))
        return color

    st.markdown("### 📋 Matriz de Materiales Candidatos")
    st.dataframe(df_res.style.applymap(color_ratings, subset=['Resistencia Química (A/B/C/D)']), use_container_width=True)
    
    st.info("""
    **Leyenda de Calificación:**
    * **A:** Excelente (Sin efecto / Muy recomendado)
    * **B:** Bueno (Efecto menor / Aceptable)
    * **C:** Precaución (Usar bajo condiciones limitadas o con sobrepesor de corrosión)
    * **D:** No recomendado (Severo efecto corrosivo)
    """)

# --- TAB 2: DISEÑO MECÁNICO ---
with tab2:
    st.subheader("📐 Cálculo de Espesor de Pared (Recipientes a Presión)")
    st.markdown("Basado en el código **ASME BPVC Sección VIII** (visto en teoría de diseño de equipos):")
    
    # Fórmula LaTeX
    st.latex(r"t = \frac{P \cdot R}{S \cdot E - 0.6 \cdot P} + CA")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        P_calc = st.number_input("Presión de diseño, $P$ (bar)", value=presion)
        R_calc = st.number_input("Radio interior del recipiente, $R$ (mm)", value=500.0)
        CA_calc = st.number_input("Sobrepesor de corrosión, $CA$ (mm)", value=3.0)
    with col_c2:
        S_calc = st.number_input("Máximo esfuerzo admisible del material, $S$ (bar)", value=1300.0)
        E_calc = st.slider("Eficiencia de soldadura, $E$ (0.7 - 1.0)", 0.7, 1.0, 0.85)
        
    if st.button("🧮 Calcular Espesor Mínimo"):
        if (S_calc * E_calc - 0.6 * P_calc) <= 0:
            st.error("Error: El denominador es menor o igual a cero. Revise los valores de esfuerzo y presión.")
        else:
            t_res = (P_calc * R_calc) / (S_calc * E_calc - 0.6 * P_calc) + CA_calc
            st.success(f"### Espesor de pared calculado ($t$): **{t_res:.2f} mm**")
            st.markdown(f"- **Espesor neto sin corrosión:** `{t_res - CA_calc:.2f} mm`")
            st.markdown(f"- **Sobrepesor por corrosión ($CA$):** `{CA_calc} mm`")

# --- TAB 3: HEURÍSTICAS Y CHECKLIST ---
with tab3:
    st.subheader("💡 Heurísticas Clave para Ingeniería de Procesos (Briem / Marriaga)")
    
    st.markdown("""
    * **Efecto de la Temperatura:** Como regla general heurística, la tasa de corrosión **se duplica por cada 10°C** de aumento de temperatura hasta el punto de ebullición. Cuidado con las temperaturas de superficie en chaquetas de vapor.
    * **Corrosión por Paradas (Downtime Corrosion):** Los equipos fuera de servicio sufren a menudo más corrosión que operando en caliente (por condensación de gases ácidos como $SO_2$ o acumulación de humedad).
    * **Velocidad y Corrosión-Eserosión (FAC):** En fluidos sucios o de alta velocidad, las capas protectoras de óxido pueden desprenderse. Para tuberías y gasoductos, mantenga velocidades de diseño seguras para evitar cavitación y desgaste de soldaduras.
    * **Corrosión Influenciada Microbiológicamente (MIC):** ¡Atención crítica! Si se deja agua hidrostática estancada en sistemas de acero inoxidable durante meses, las bacterias pueden perforar el material en poco tiempo mediante estructuras en "cueva".
    * **fisuración por tensión (SCC):** Los cloruros en concentraciones de pocas ppm, combinados con tensiones residuales de soldadura y temperatura > 60°C, generan fisuración catastrófica en aceros inoxidables austeníticos (304/316).
    """)

# --- TAB 4: GUÍA DE GITHUB Y STREAMLIT ---
with tab4:
    st.subheader("🚀 Instrucciones para Subir a GitHub y Desplegar en la Nube")
    st.markdown("""
    Sigue estos pasos sencillos para llevar tu aplicación a la web de forma gratuita:

    ### Paso 1: Crear los archivos en tu repositorio de GitHub
    Crea un repositorio nuevo en [GitHub](https://github.com) y sube los siguientes dos archivos:
    
    1. **`app.py`** (El código que escribimos arriba).
    2. **`requirements.txt`** (Las librerías necesarias).

    Contenido exacto para el archivo **`requirements.txt`**:
    ```text
    streamlit>=1.28.0
    pandas>=2.0.0
    numpy>=1.24.0
    ```

    ### Paso 2: Desplegar en Streamlit Community Cloud
    1. Ve a [share.streamlit.io](https://share.streamlit.io/).
    2. Inicia sesión con tu cuenta de GitHub.
    3. Haz clic en **"New app"**.
    4. Selecciona tu repositorio, la rama (`main` o `master`) y el archivo principal (`app.py`).
    5. Haz clic en **"Deploy!"** y en unos segundos tendrás tu aplicación lista para compartir mediante un enlace web.
    """)

# Pie de página institucional
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desarrollado para Ingeniería de Procesos / Diseño de Equipos | Basado en Heurísticas CPI y Materiales de Construcción.</p>", unsafe_allow_html=True)
