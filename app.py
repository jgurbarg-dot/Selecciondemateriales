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
*Herramienta basada en heurísticas de ingeniería química (Art. James J. Briem / CPI) y normativas ASME / API para equipos de procesos y recipientes a presión.*
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
        "Acero al Carbón (ASTM A516 Gr. 70)": ["C", "B", "D", "A", "C", "C", "A", "A"],
        "Acero Inox Austenítico (AISI 304L)": ["A", "D", "D", "A", "C", "B", "A", "A"],
        "Acero Inox Austenítico (AISI 316L)": ["A", "D", "D", "A", "B", "A", "A", "A"],
        "Titanio Grado 2 (ASTM B265)": ["A", "D", "D", "A", "A", "A", "D", "A"],
        "Aleación de Níquel (Hastelloy C-276)": ["A", "A", "B", "A", "A", "A", "A", "A"],
        "Termoplástico (PVC Sch 80)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "Termoplástico (Polipropileno - PP)": ["A", "C", "A", "A", "A", "A", "D", "D"],
        "Fluoropolímero (Revestimiento PTFE)": ["A", "A", "A", "A", "A", "A", "A", "A"],
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
        "Recipiente a Presión / Caldera (ASME Sec. VIII)", 
        "Tanque de Almacenamiento Atmosférico (API 650)", 
        "Gasoducto / Línea de Conducción", 
        "Intercambiador de Calor", 
        "Bomba / Agitador (Operación Dinámica)"
    ]
)

sustancia = st.sidebar.selectbox(
    "Sustancia / Medio de Contacto Principal",
    df_comp["Sustancia"].tolist()
)

temp = st.sidebar.slider("Temperatura de Diseño (°C)", -20, 500, 94)
presion = st.sidebar.number_input("Presión de Diseño (bar)", min_value=0.0, value=4.0, step=1.0)

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
    
    fila_sustancia = df_comp[df_comp["Sustancia"] == sustancia].iloc[0]
    
    resultados = []
    for material in df_comp.columns[1:]:
        calificacion = fila_sustancia[material]
        nota_extra = "Condiciones normales de operación."
        
        # Lógica heurística de ajuste por temperatura y condiciones
        if "Termoplástico" in material and temp > 60:
            if calificacion == "A":
                calificacion = "C"
            nota_extra = "⚠️ Precaución: Supera el límite de temperatura para plásticos (~60°C)."
        
        if "Acero al Carbón" in material and temp > 400:
            calificacion = "D"
            nota_extra = "❌ El acero al carbón pierde resistencia a temperaturas > 400°C (fluencia)."
            
        resultados.append({
            "Material (Especificación Técnica)": material,
            "Resistencia Química (A/B/C/D)": calificacion,
            "Observación Heurística": nota_extra
        })
    
    df_res = pd.DataFrame(resultados)
    
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
    
    # --- LÓGICA INTELIGENTE DE RECOMENDACIÓN ESTRUCTURAL ---
    st.markdown("### 🏆 Recomendación Experta para el Diseño del Equipo")
    
    if "Recipiente a Presión" in tipo_equipo or "Caldera" in tipo_equipo:
        if "Agua (Limpia / Calderas)" in sustancia:
            st.success("""
            **🎯 Material Estructural Principal Recomendado:**
            * **Acero al Carbón ASTM A516 Grado 70** (Para la carcasa, virolas y domos de la caldera).
            
            **💡 Justificación de Ingeniería:**
            Aunque el agua pura de forma aislada daría una calificación neutra/precaución en tablas estáticas puras, **en una caldera real el agua de alimentación está tratada químicamente** (desaireada y con control de pH/secuestrantes de oxígeno). Por lo tanto, el **ASTM A516 Gr. 70** es la norma obligatoria y más económica de la industria para soportar la presión (ej. 4 bar), aplicándole un sobrepesor por corrosión (*Corrosion Allowance*) de 1.5 a 3 mm. 
            *Los plásticos, elastómeros (Viton) o teflón **no sirven** como estructura principal a presión.*
            """)
        else:
            st.info("Para este recipiente a presión con la sustancia seleccionada, evalúe aceros inoxidables o aceros al carbón con revestimiento interno adecuado.")
    else:
        # Para otros equipos generales, muestra los mejores en resistencia química
        materiales_buenos = [r["Material (Especificación Técnica)"] for r in resultados if r["Resistencia Química (A/B/C/D)"] in ["A", "B"] and not "Elastómero" in r["Material (Especificación Técnica)"] and not "Termoplástico" in r["Material (Especificación Técnica)"]]
        if materiales_buenos:
            st.success(f"**Materiales recomendados para el proceso:**\n- " + "\n- ".join([f"**{m}**" for m in materiales_buenos]))

    st.info("""
    **Leyenda de Calificación Detallada:**
    * 🟩 **A (Excelente):** Alta inercia química / Excelente opción base.
    * 🟨 **B (Bueno):** Aceptable con consideraciones de espesor o tratamiento.
    * 🟧 **C (Precaución):** Requiere condiciones limitadas o tratamiento químico estricto.
    * 🟥 **D (No recomendado):** Ataque corrosivo severo o pérdida de propiedades mecánicas.
    """)

# --- TAB 2: DISEÑO MECÁNICO ---
with tab2:
    st.subheader("📐 Cálculo de Espesor de Pared (Recipientes a Presión / Calderas)")
    st.markdown("Basado en el código **ASME BPVC Sección VIII**:")
    
    st.latex(r"t = \frac{P \cdot R}{S \cdot E - 0.6 \cdot P} + CA")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        P_calc = st.number_input("Presión de diseño, $P$ (bar)", value=presion)
        R_calc = st.number_input("Radio interior del recipiente, $R$ (mm)", value=500.0)
        CA_calc = st.number_input("Sobrepesor de corrosión, $CA$ (mm)", value=3.0)
    with col_c2:
        S_calc = st.number_input("Esfuerzo admisible del material ASTM A516 Gr. 70, $S$ (bar)", value=1300.0)
        E_calc = st.slider("Eficiencia de soldadura, $E$ (0.7 - 1.0)", 0.7, 1.0, 0.85)
        
    if st.button("🧮 Calcular Espesor Mínimo"):
        if (S_calc * E_calc - 0.6 * P_calc) <= 0:
            st.error("Error: El denominador es menor o igual a cero. Revise los valores de esfuerzo y presión.")
        else:
            t_res = (P_calc * R_calc) / (S_calc * E_calc - 0.6 * P_calc) + CA_calc
            st.success(f"### Espesor de pared calculado ($t$): **{t_res:.2f} mm**")
            st.markdown(f"- **Espesor neto estructural sin corrosión:** `{t_res - CA_calc:.2f} mm`")
            st.markdown(f"- **Sobrepesor por corrosión añadido ($CA$):** `{CA_calc} mm`")

# --- TAB 3: HEURÍSTICAS Y CHECKLIST ---
with tab3:
    st.subheader("💡 Heurísticas Clave para Ingeniería de Procesos (Briem / Marriaga)")
    st.markdown("""
    * **Efecto de la Temperatura:** La tasa de corrosión se duplica por cada 10°C de aumento de temperatura.
    * **Tratamiento de Agua en Calderas:** El acero al carbón requiere obligatoriamente control de oxígeno disuelto y pH para evitar picaduras (*pitting*).
    * **Corrosión por Paradas:** Los equipos fuera de servicio sufren mayor corrosión por condensación húmeda.
    """)

# --- TAB 4: GUÍA DE GITHUB Y STREAMLIT ---
with tab4:
    st.subheader("🚀 Instrucciones para Actualizar en GitHub")
    st.markdown("""
    1. Reemplaza el código en tu archivo **`app.py`** en GitHub con este código actualizado.
    2. Guarda los cambios y tu aplicación reflejará inmediatamente las recomendaciones correctas orientadas a recipientes a presión y calderas.
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desarrollado para Ingeniería de Procesos / Diseño de Equipos | Basado en Heurísticas CPI y Materiales de Construcción.</p>", unsafe_allow_html=True)
