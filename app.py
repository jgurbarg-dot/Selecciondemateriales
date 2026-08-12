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
        "Acero al Carbón (ASTM A516 Gr. 70 / AISI 1040)": ["C", "B", "D", "A", "C", "C", "A", "A"],
        "Acero Inox Austenítico (AISI 304L)": ["A", "D", "D", "A", "C", "B", "A", "A"],
        "Acero Inox Austenítico (AISI 316L)": ["A", "D", "D", "A", "B", "A", "A", "A"],
        "Titanio Grado 2 (ASTM B265)": ["A", "D", "D", "A", "A", "A", "D", "A"],
        "Aleación de Níquel (Hastelloy C-276)": ["A", "A", "B", "A", "A", "A", "A", "A"],
        "Termoplástico (PVC Sch 80)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "Termoplástico (Polipropileno - PP)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "Fluoropolímero (PTFE / Teflon)": ["A", "A", "A", "A", "A", "A", "A", "A"],
        "Elastómero / Sello (FKM / Viton)": ["A", "D", "D", "B", "A", "A", "D", "A"]
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
        if "Termoplástico" in material and temp > 60:
            if calificacion == "A":
                calificacion = "C"
            nota_extra = "⚠️ Precaución: La temperatura supera el límite recomendado para plásticos estándar (~60-70°C)."
        
        if "Acero al Carbón" in material and temp > 400:
            calificacion = "D"
            nota_extra = "❌ El acero al carbón pierde resistencia mecánica a temperaturas > 400°C (fluencia/creep)."
            
        resultados.append({
            "Material (Especificación Técnica)": material,
            "Resistencia Química (A/B/C/D)": calificacion,
            "Observación Heurística": nota_extra
        })
    
    df_res = pd.DataFrame(resultados)
    
    # Función de color corregida para que las letras sean legibles (texto oscuro contrastado)
    def color_ratings(val):
        if val == 'A':
            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif val == 'B':
            return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
        elif val == 'C':
            return 'background-color: #ffeeba; color: #856404; font-weight: bold;'
        else:
            return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'

    st.markdown("### 📋 Matriz de Materiales Candidatos")
    st.dataframe(df_res.style.map(color_ratings, subset=['Resistencia Química (A/B/C/D)']), use_container_width=True)
    
    # Sección de Recomendación Experta y Leyenda
    st.markdown("### 🏆 Guía de Recomendación Directa")
    
    # Filtrar los mejores materiales (categoría A o B tras heurísticas)
    materiales_recomendados = [r["Material (Especificación Técnica)"] for r in resultados if r["Resistencia Química (A/B/C/D)"] in ["A", "B"]]
    
    if materiales_recomendados:
        st.success(f"**Materiales más recomendados para esta aplicación:**\n- " + "\n- ".join([f"**{m}**" for m in materiales_recomendados]))
    else:
        st.warning("⚠️ No hay materiales óptimos en la lista base para estas condiciones extremas. Se requiere una aleación especial o revestimiento (lining).")

    st.info("""
    **Leyenda de Calificación Detallada:**
    * 🟩 **A (Excelente):** Sin efecto químico adverso / Altamente recomendado para diseño a largo plazo.
    * 🟨 **B (Bueno):** Efecto menor o aceptable / Se puede usar con un sobrepesor de corrosión moderado.
    * 🟧 **C (Precaución):** Usar solo bajo condiciones limitadas, periodos cortos o inspección frecuente.
    * 🟥 **D (No recomendado):** Severo ataque corrosivo / Riesgo de falla catastrófica inmediata.
    """)

# --- TAB 2: DISEÑO MECÁNICO ---
with tab2:
    st.subheader("📐 Cálculo de Espesor de Pared (Recipientes a Presión)")
    st.markdown("Basado en el código **ASME BPVC Sección VIII**:")
    
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
    * **Efecto de la Temperatura:** La tasa de corrosión se duplica aproximadamente por cada 10°C de aumento de temperatura.
    * **Corrosión por Paradas (Downtime):** Los equipos fuera de servicio suelen corroerse más rápido por condensación de vapores húmedos o ácidos.
    * **Corrosión-Erosión (FAC):** En fluidos turbulentos o con sólidos en suspensión, las velocidades altas destruyen las capas pasivas de protección.
    * **MIC (Corrosión Microbiológica):** El agua estancada en aceros inoxidables genera colonias bacterianas que perforan el metal en pocos meses.
    * **SCC (Fisuración por Tensión):** Cloruros libres + tensiones de soldadura + T > 60°C provocan fisuración rápida en aceros austeníticos tipo 304/316.
    """)

# --- TAB 4: GUÍA DE GITHUB Y STREAMLIT ---
with tab4:
    st.subheader("🚀 Instrucciones para Actualizar en GitHub")
    st.markdown("""
    1. Ve a tu repositorio en [GitHub](https://github.com).
    2. Edita o reemplaza el contenido de tu archivo **`app.py`** con este nuevo código completo.
    3. Asegúrate de que el archivo **`requirements.txt`** contenga:
       ```text
       streamlit>=1.28.0
       pandas>=2.0.0
       numpy>=1.24.0
       ```
    4. Guarda los cambios (**Commit changes**) y tu app en Streamlit Cloud se actualizará automáticamente solucionando el problema visual.
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desarrollado para Ingeniería de Procesos / Diseño de Equipos | Basado en Heurísticas CPI y Materiales de Construcción.</p>", unsafe_allow_html=True)
