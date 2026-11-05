
import warnings
import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.api import VAR, VECM
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import (
    select_coint_rank,
    select_order,
)


def preparar_datos(datos, columnas=None):
    """Valida y prepara series numéricas ordenadas por fecha."""
    df = pd.DataFrame(datos).copy()

    if columnas is not None:
        df = df[columnas]

    if df.empty:
        raise ValueError("No se recibieron datos.")

    if df.isna().any().any():
        raise ValueError(
            "Existen valores faltantes. Limpia la base antes "
            "de estimar el modelo."
        )

    for columna in df.columns:
        df[columna] = pd.to_numeric(
            df[columna], errors="raise"
        )

    if not np.isfinite(df.to_numpy()).all():
        raise ValueError("Los datos contienen valores no finitos.")

    if (df.nunique() <= 1).any():
        raise ValueError(
            "Todas las variables deben presentar variación."
        )

    return df.astype(float)


def prueba_adf(serie):
    """Prueba de Dickey-Fuller aumentada."""
    serie = pd.Series(serie).dropna()

    resultado = adfuller(serie, autolag="AIC")

    return {
        "estadistico": float(resultado[0]),
        "p_valor": float(resultado[1]),
        "rezagos": int(resultado[2]),
        "estacionaria_5pct": bool(resultado[1] < 0.05),
    }


def modelo_arima(datos, columna, orden=(1, 1, 1),
                 periodos=5):
    """Estima ARIMA y genera pronósticos."""
    df = preparar_datos(datos, [columna])

    if len(df) < 20:
        raise ValueError(
            "ARIMA requiere al menos 20 observaciones "
            "en esta implementación."
        )

    if periodos < 1 or periodos > 60:
        raise ValueError(
            "Los períodos deben estar entre 1 y 60."
        )

    if (
        len(orden) != 3
        or any(not isinstance(x, int) or x < 0 for x in orden)
        or max(orden) > 5
    ):
        raise ValueError("Orden ARIMA no permitido.")

    modelo = ARIMA(
        df[columna],
        order=orden,
        enforce_stationarity=True,
        enforce_invertibility=True,
    )

    ajuste = modelo.fit()
    pronostico = ajuste.get_forecast(steps=periodos)
    intervalo = pronostico.conf_int(alpha=0.05)

    return {
        "modelo": "ARIMA",
        "variable": columna,
        "orden": orden,
        "aic": float(ajuste.aic),
        "bic": float(ajuste.bic),
        "adf_niveles": prueba_adf(df[columna]),
        "pronostico": pronostico.predicted_mean.tolist(),
        "intervalo_inferior": intervalo.iloc[:, 0].tolist(),
        "intervalo_superior": intervalo.iloc[:, 1].tolist(),
    }


def modelo_var(datos, columnas, rezagos=2,
               periodos=5):
    """Estima VAR con variables estacionarias."""
    if not 2 <= len(columnas) <= 5:
        raise ValueError("VAR requiere entre 2 y 5 variables.")

    df = preparar_datos(datos, columnas)

    if len(df) < 30:
        raise ValueError(
            "VAR requiere al menos 30 observaciones."
        )

    if not 1 <= rezagos <= 5:
        raise ValueError("Usa entre 1 y 5 rezagos.")

    adf = {
        col: prueba_adf(df[col])
        for col in columnas
    }

    no_estacionarias = [
        col for col, resultado in adf.items()
        if not resultado["estacionaria_5pct"]
    ]

    if no_estacionarias:
        raise ValueError(
            "No se confirmó estacionariedad al 5 % en: "
            + ", ".join(no_estacionarias)
            + ". Evalúa transformaciones o cointegración."
        )

    ajuste = VAR(df).fit(rezagos)

    if not ajuste.is_stable():
        raise ValueError("El VAR estimado no es estable.")

    pronostico = ajuste.forecast(
        df.values[-rezagos:],
        steps=periodos,
    )

    return {
        "modelo": "VAR",
        "variables": columnas,
        "rezagos": rezagos,
        "aic": float(ajuste.aic),
        "bic": float(ajuste.bic),
        "estable": bool(ajuste.is_stable()),
        "adf": adf,
        "pronostico": pd.DataFrame(
            pronostico, columns=columnas
        ).to_dict(orient="list"),
    }


def modelo_vecm(datos, columnas, periodos=5,
                rezagos_diferencias=1):
    """Estima VECM si hay evidencia de cointegración."""
    if not 2 <= len(columnas) <= 5:
        raise ValueError("VECM requiere entre 2 y 5 variables.")

    df = preparar_datos(datos, columnas)

    if len(df) < 40:
        raise ValueError(
            "VECM requiere al menos 40 observaciones."
        )

    if not 1 <= rezagos_diferencias <= 5:
        raise ValueError("Rezagos fuera de rango.")

    rango = select_coint_rank(
        df,
        det_order=0,
        k_ar_diff=rezagos_diferencias,
        method="trace",
        signif=0.05,
    )

    r = int(rango.rank)

    if not 0 < r < len(columnas):
        raise ValueError(
            f"Rango de cointegración estimado: {r}. "
            "No se justifica un VECM cointegrado "
            "con esta especificación."
        )

    ajuste = VECM(
        df,
        k_ar_diff=rezagos_diferencias,
        coint_rank=r,
        deterministic="ci",
    ).fit()

    pronostico = ajuste.predict(steps=periodos)

    return {
        "modelo": "VECM",
        "variables": columnas,
        "rango_cointegracion": r,
        "rezagos_diferencias": rezagos_diferencias,
        "pronostico": pd.DataFrame(
            pronostico, columns=columnas
        ).to_dict(orient="list"),
        "alpha": ajuste.alpha.tolist(),
        "beta": ajuste.beta.tolist(),
    }

