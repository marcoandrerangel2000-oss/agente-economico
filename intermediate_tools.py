
import requests

def consultar_pib(pais="GTM"):
    url = (
        f"https://api.worldbank.org/v2/country/{pais}"
        "/indicator/NY.GDP.MKTP.CD"
    )

    try:
        respuesta = requests.get(
            url,
            params={"format": "json", "per_page": 10},
            timeout=15
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

        if not isinstance(datos, list) or len(datos) < 2:
            return "No se pudo obtener información del PIB."

        registros = datos[1] or []

        for registro in registros:
            if registro.get("value") is not None:
                return (
                    f"PIB de {pais} en {registro['date']}: "
                    f"USD {registro['value']:,.2f}"
                )

        return "No hay datos disponibles."

    except (requests.RequestException, ValueError, TypeError, KeyError) as error:
        return f"Error al consultar el PIB: {error}"
