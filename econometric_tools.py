
import json

from econometric_models import (
    modelo_arima,
    modelo_var,
    modelo_vecm,
)


def ejecutar_modelo_econometrico(
    modelo,
    datos,
    columnas,
    periodos=5,
    orden_arima=None,
    rezagos=2,
    rezagos_diferencias=1,
):
    """Ejecuta un modelo validado y devuelve resultados JSON."""

    modelo = modelo.upper().strip()

    if modelo not in ("ARIMA", "VAR", "VECM"):
        raise ValueError("Modelo no permitido.")

    if not isinstance(datos, list) or not datos:
        raise ValueError("No hay observaciones disponibles.")

    if not isinstance(columnas, list) or not columnas:
        raise ValueError("Selecciona las variables.")

    if not isinstance(periodos, int) or not 1 <= periodos <= 60:
        raise ValueError("Horizonte de pronóstico no válido.")

    if modelo == "ARIMA":
        if len(columnas) != 1:
            raise ValueError("ARIMA requiere una variable.")

        orden = tuple(
            orden_arima if orden_arima is not None
            else [1, 1, 1]
        )

        resultado = modelo_arima(
            datos=datos,
            columna=columnas[0],
            orden=orden,
            periodos=periodos,
        )

    elif modelo == "VAR":
        resultado = modelo_var(
            datos=datos,
            columnas=columnas,
            rezagos=rezagos,
            periodos=periodos,
        )

    else:
        resultado = modelo_vecm(
            datos=datos,
            columnas=columnas,
            periodos=periodos,
            rezagos_diferencias=rezagos_diferencias,
        )

    return resultado


def ejecutar_modelo_json(argumentos, datos_autorizados):
    """Punto de entrada seguro para llamadas de Groq."""

    if not isinstance(argumentos, dict):
        raise ValueError("Argumentos incorrectos.")

    if datos_autorizados is None:
        raise ValueError(
            "Primero carga una base de datos en Streamlit."
        )

    resultado = ejecutar_modelo_econometrico(
        modelo=argumentos["modelo"],
        datos=datos_autorizados,
        columnas=argumentos["columnas"],
        periodos=argumentos.get("periodos", 5),
        orden_arima=argumentos.get("orden_arima"),
        rezagos=argumentos.get("rezagos", 2),
        rezagos_diferencias=argumentos.get(
            "rezagos_diferencias", 1
        ),
    )

    return json.dumps(
        resultado,
        ensure_ascii=False,
        allow_nan=False,
    )

