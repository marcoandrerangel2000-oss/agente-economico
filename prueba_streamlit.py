
import streamlit as st

st.set_page_config(
    page_title="Agente Económico IA",
    page_icon="📊",
    layout="wide"
)

st.title("🤖 AGENTE ECONÓMICO IA")
st.write("Prueba de conexión entre Streamlit y Groq.")

try:
    from main import ejecutar_agente

    st.success("Conexión con main.py establecida correctamente.")

    pregunta = st.text_input(
        "Escribe una pregunta económica:",
        placeholder="¿Cuál es el PIB de Guatemala?"
    )

    if st.button("Consultar"):
        if pregunta.strip():
            with st.spinner("El agente está analizando tu pregunta..."):
                respuesta = ejecutar_agente(pregunta)

            st.subheader("Respuesta del agente")
            st.write(respuesta)
        else:
            st.warning("Primero escribe una pregunta.")

except Exception as error:
    st.error(f"Error detectado: {type(error).__name__}: {error}")
