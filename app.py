
import streamlit as st

from main import ejecutar_agente, USUARIO
from persistent_memory import (
    obtener_recuerdos,
    guardar_recuerdo,
    borrar_recuerdo,
    borrar_historial,
    conectar
)
from economic_charts import mostrar_graficas


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Economia AI | Workspace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# ESTILOS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stApp"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #F5F7FB;
    color: #17243A;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0B1220;
}

[data-testid="stSidebar"] * {
    color: #E8EEF7;
}

[data-testid="stSidebar"] .stButton button {
    background: #172840;
    border: 1px solid #2B405A;
    color: #FFFFFF;
    border-radius: 12px;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #23415D;
    border-color: #38D9C4;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 8px 10px;
}

h1, h2, h3 {
    color: #14243B;
    letter-spacing: -0.5px;
}

.hero {
    background: linear-gradient(120deg, #0E1D33, #173E57);
    padding: 32px;
    border-radius: 20px;
    color: white;
    margin-bottom: 22px;
}

.hero h1 {
    color: white;
    font-size: 2rem;
    margin: 0 0 8px 0;
}

.hero p {
    color: #C4D5E5;
    font-size: 1rem;
    margin: 0;
}

.eyebrow {
    color: #46E0CB;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.metric-card {
    background: white;
    border: 1px solid #E4EAF2;
    border-radius: 16px;
    padding: 20px;
    min-height: 115px;
    box-shadow: 0 3px 12px rgba(15, 35, 60, 0.03);
}

.metric-card .label {
    color: #6A7C91;
    font-size: 0.85rem;
}

.metric-card .value {
    color: #14243B;
    font-size: 1.7rem;
    font-weight: 800;
    margin-top: 10px;
}

[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E5EAF1;
    border-radius: 15px;
    padding: 14px;
    margin-bottom: 12px;
}

[data-testid="stChatInput"] {
    border-radius: 15px;
}

.stButton button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: #0F8F91;
    border: none;
    border-radius: 10px;
}

.stButton button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    background: #087779;
}

div[data-testid="stForm"] {
    background: white;
    border: 1px solid #E5EAF1;
    border-radius: 16px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# BASE DE DATOS
# ==========================================

def cargar_historial(usuario):
    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT rol, contenido
            FROM mensajes
            WHERE usuario = ?
            ORDER BY id ASC
            """,
            (usuario,)
        ).fetchall()

    return [
        {"role": rol, "content": contenido}
        for rol, contenido in filas
    ]


def contar_mensajes(usuario):
    with conectar() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM mensajes WHERE usuario = ?",
            (usuario,)
        ).fetchone()[0]


if "mensajes" not in st.session_state:
    st.session_state.mensajes = cargar_historial(USUARIO)


# ==========================================
# COMPONENTES VISUALES
# ==========================================

def hero(etiqueta, titulo, descripcion):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{etiqueta}</div>
            <h1>{titulo}</h1>
            <p>{descripcion}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def tarjeta(titulo, valor):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{titulo}</div>
            <div class="value">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## ◈ ECONOMIA AI")
    st.caption("INTELLIGENCE WORKSPACE")
    st.divider()

    pagina = st.radio(
        "ESPACIO DE TRABAJO",
        [
            "💬 Chat económico",
            "📈 Gráficas económicas",
            "🧠 Memoria permanente"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.caption("ADMINISTRACIÓN")

    if st.button(
        "🔄 Actualizar historial",
        use_container_width=True
    ):
        st.session_state.mensajes = cargar_historial(USUARIO)
        st.rerun()

    if st.button(
        "🗑️ Borrar conversaciones",
        use_container_width=True
    ):
        borrar_historial(USUARIO)
        st.session_state.mensajes = []
        st.rerun()

    st.divider()
    st.caption("● Sistema conectado")
    st.caption("Groq · SQLite · Streamlit")


# ==========================================
# GRÁFICAS
# ==========================================

if pagina == "📈 Gráficas económicas":

    hero(
        "DATA ANALYTICS",
        "Análisis económico",
        "Visualiza indicadores y tendencias económicas."
    )

    mostrar_graficas()
    st.stop()


# ==========================================
# MEMORIA
# ==========================================

if pagina == "🧠 Memoria permanente":

    hero(
        "INTELLIGENT MEMORY",
        "Centro de memoria",
        "Administra los conocimientos guardados por tu agente."
    )

    recuerdos = obtener_recuerdos(USUARIO)

    col1, col2 = st.columns(2)

    with col1:
        tarjeta("Recuerdos almacenados", len(recuerdos))

    with col2:
        tarjeta("Mensajes registrados", contar_mensajes(USUARIO))

    st.write("")
    st.subheader("Conocimientos guardados")

    if recuerdos:

        for clave, valor in recuerdos.items():

            with st.container(border=True):
                col_info, col_boton = st.columns([5, 1])

                with col_info:
                    st.markdown(f"**{clave}**")
                    st.write(valor)

                with col_boton:
                    if st.button(
                        "Eliminar",
                        key=f"delete_{clave}"
                    ):
                        borrar_recuerdo(USUARIO, clave)
                        st.rerun()
    else:
        st.info("Todavía no hay recuerdos guardados.")

    st.write("")
    st.subheader("Agregar un recuerdo")

    with st.form("nuevo_recuerdo"):

        clave = st.text_input(
            "Nombre del recuerdo",
            placeholder="proyecto_actual"
        )

        valor = st.text_area(
            "Información",
            placeholder="Estoy analizando el PIB de Guatemala."
        )

        if st.form_submit_button(
            "Guardar recuerdo",
            type="primary"
        ):
            if clave.strip() and valor.strip():
                guardar_recuerdo(
                    USUARIO,
                    clave.strip(),
                    valor.strip()
                )
                st.rerun()
            else:
                st.warning("Completa ambos campos.")

    st.stop()


# ==========================================
# CHAT
# ==========================================

hero(
    "AI ECONOMIC ASSISTANT",
    "Tu espacio de análisis económico",
    "Consulta indicadores, desarrolla proyectos y conversa con tu agente inteligente."
)

total_mensajes = contar_mensajes(USUARIO)
total_recuerdos = len(obtener_recuerdos(USUARIO))

c1, c2, c3 = st.columns(3)

with c1:
    tarjeta("Mensajes guardados", total_mensajes)

with c2:
    tarjeta("Recuerdos activos", total_recuerdos)

with c3:
    tarjeta("Motor de IA", "Groq")

st.write("")
st.subheader("Conversación")

if not st.session_state.mensajes:
    st.info(
        "¡Bienvenido! Puedes comenzar preguntando sobre "
        "el PIB, inflación, desempleo o tus proyectos."
    )

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])


pregunta = st.chat_input(
    "Pregunta sobre economía, datos o proyectos..."
)

if pregunta:

    st.session_state.mensajes.append({
        "role": "user",
        "content": pregunta
    })

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):

        with st.spinner("Analizando información..."):

            try:
                respuesta = ejecutar_agente(
                    pregunta,
                    usuario=USUARIO
                )

                st.markdown(respuesta)

                st.session_state.mensajes.append({
                    "role": "assistant",
                    "content": respuesta
                })

            except Exception as error:
                st.error(
                    f"Error: {type(error).__name__}: {error}"
                )
