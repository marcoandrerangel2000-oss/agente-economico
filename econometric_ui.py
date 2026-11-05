
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from econometric_tools import ejecutar_modelo_econometrico


def mostrar_econometria():
    st.title("📊 Laboratorio Econométrico")
    st.write(
        "Estima modelos ARIMA, VAR y VECM "
        "utilizando tus propias series de tiempo."
    )

    archivo = st.file_uploader(
        "Sube una base de datos",
        type=["xlsx", "csv"],
        key="archivo_econometrico",
    )

    if archivo is None:
        st.info("Carga un archivo Excel o CSV para comenzar.")
        return

    try:
        if archivo.name.lower().endswith(".csv"):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo)
    except Exception as error:
        st.error(f"No se pudo leer el archivo: {error}")
        return

    st.subheader("Vista previa de los datos")
    st.dataframe(df.head(10), use_container_width=True)

    # Solo columnas numéricas
    numericas = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numericas:
        st.error("No se encontraron columnas numéricas.")
        return

    modelo = st.selectbox(
        "Selecciona el modelo",
        ["ARIMA", "VAR", "VECM"],
    )

    if modelo == "ARIMA":
        variable = st.selectbox(
            "Variable a pronosticar",
            numericas,
        )
        columnas = [variable]
    else:
        columnas = st.multiselect(
            "Variables del modelo",
            numericas,
            default=numericas[:2],
        )

    periodos = st.number_input(
        "Períodos de pronóstico",
        min_value=1,
        max_value=60,
        value=5,
    )

    orden_arima = [1, 1, 1]
    rezagos = 2
    rezagos_diferencias = 1

    if modelo == "ARIMA":
        st.subheader("Parámetros ARIMA")
        c1, c2, c3 = st.columns(3)

        with c1:
            p = st.number_input(
                "p", 0, 5, 1
            )
        with c2:
            d = st.number_input(
                "d", 0, 5, 1
            )
        with c3:
            q = st.number_input(
                "q", 0, 5, 1
            )

        orden_arima = [int(p), int(d), int(q)]

    elif modelo == "VAR":
        rezagos = st.slider(
            "Rezagos VAR", 1, 5, 2
        )

    else:
        rezagos_diferencias = st.slider(
            "Rezagos en diferencias VECM",
            1, 5, 1
        )

    st.caption(
        "Los datos deben estar ordenados cronológicamente, "
        "con observaciones equidistantes y sin valores faltantes. "
        "El horizonte se expresa en períodos de la base."
    )

    if st.button(
        "🚀 Ejecutar modelo",
        type="primary",
        key="ejecutar_econometria",
    ):
        if modelo != "ARIMA" and not 2 <= len(columnas) <= 5:
            st.error("Selecciona entre 2 y 5 variables.")
            return

        try:
            with st.spinner("Estimando modelo..."):
                resultado = ejecutar_modelo_econometrico(
                    modelo=modelo,
                    datos=df[columnas].to_dict(
                        orient="records"
                    ),
                    columnas=columnas,
                    periodos=int(periodos),
                    orden_arima=orden_arima,
                    rezagos=int(rezagos),
                    rezagos_diferencias=int(
                        rezagos_diferencias
                    ),
                )

            st.session_state["ultimo_modelo_econometrico"] = {
                "resultado": resultado,
                "datos": df[columnas].to_dict(
                    orient="records"
                ),
                "columnas": columnas,
                "modelo": modelo,
            }

        except Exception as error:
            st.error(f"No se pudo estimar: {error}")
            return

    guardado = st.session_state.get(
        "ultimo_modelo_econometrico"
    )

    if not guardado:
        return

    resultado = guardado["resultado"]

    st.success(
        f"Modelo {resultado['modelo']} estimado."
    )

    if "aic" in resultado:
        st.metric(
            "AIC",
            f"{resultado['aic']:.3f}"
        )

    if "rango_cointegracion" in resultado:
        st.metric(
            "Rango de cointegración",
            resultado["rango_cointegracion"],
        )

    pronostico = resultado["pronostico"]

    if modelo == "ARIMA":
        tabla = pd.DataFrame({
            columnas[0]: pronostico,
            "Inferior 95%": resultado[
                "intervalo_inferior"
            ],
            "Superior 95%": resultado[
                "intervalo_superior"
            ],
        })
    else:
        tabla = pd.DataFrame(pronostico)

    tabla.index = range(1, len(tabla) + 1)
    tabla.index.name = "Período futuro"

    st.subheader("Pronóstico")
    st.dataframe(tabla, use_container_width=True)

    figura = go.Figure()

    for columna in columnas:
        if columna in tabla.columns:
            figura.add_trace(go.Scatter(
                x=tabla.index,
                y=tabla[columna],
                mode="lines+markers",
                name=columna,
            ))

    figura.update_layout(
        title=f"Pronóstico {modelo}",
        xaxis_title="Período futuro",
        yaxis_title="Valor pronosticado",
    )

    st.plotly_chart(
        figura,
        use_container_width=True,
    )

    st.download_button(
        "📥 Descargar pronóstico CSV",
        data=tabla.to_csv().encode("utf-8"),
        file_name=f"pronostico_{modelo.lower()}.csv",
        mime="text/csv",
    )

    with st.expander("Resultados técnicos"):
        st.json(resultado)
