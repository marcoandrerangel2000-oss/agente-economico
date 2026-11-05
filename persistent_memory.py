
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "memoria.db"


def conectar():
    return sqlite3.connect(DB)


def inicializar():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                rol TEXT NOT NULL,
                contenido TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS recuerdos (
                usuario TEXT NOT NULL,
                clave TEXT NOT NULL,
                valor TEXT NOT NULL,
                PRIMARY KEY (usuario, clave)
            )
        """)


def guardar_mensaje(usuario, rol, contenido):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO mensajes (usuario, rol, contenido)
            VALUES (?, ?, ?)
            """,
            (usuario, rol, contenido)
        )


def obtener_historial(usuario, limite=20):
    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT rol, contenido
            FROM (
                SELECT id, rol, contenido
                FROM mensajes
                WHERE usuario = ?
                ORDER BY id DESC
                LIMIT ?
            )
            ORDER BY id ASC
            """,
            (usuario, limite)
        ).fetchall()

    return [
        {"role": rol, "content": contenido}
        for rol, contenido in filas
    ]


def guardar_recuerdo(usuario, clave, valor):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO recuerdos (usuario, clave, valor)
            VALUES (?, ?, ?)
            ON CONFLICT(usuario, clave)
            DO UPDATE SET valor = excluded.valor
            """,
            (usuario, clave, valor)
        )


def obtener_recuerdos(usuario):
    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT clave, valor
            FROM recuerdos
            WHERE usuario = ?
            ORDER BY clave
            """,
            (usuario,)
        ).fetchall()

    return {
        clave: valor
        for clave, valor in filas
    }


def borrar_recuerdo(usuario, clave):
    with conectar() as conn:
        conn.execute(
            """
            DELETE FROM recuerdos
            WHERE usuario = ? AND clave = ?
            """,
            (usuario, clave)
        )


def borrar_historial(usuario):
    with conectar() as conn:
        conn.execute(
            """
            DELETE FROM mensajes
            WHERE usuario = ?
            """,
            (usuario,)
        )


inicializar()

def obtener_todo_historial(usuario):
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

def buscar_mensajes(usuario, consulta, limite=8):
    palabras = [
        p.lower()
        for p in consulta.split()
        if len(p) >= 4
    ]

    if not palabras:
        return []

    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT contenido
            FROM mensajes
            WHERE usuario = ?
            ORDER BY id DESC
            LIMIT 2000
            """,
            (usuario,)
        ).fetchall()

    resultados = []

    for (contenido,) in filas:
        texto = contenido.lower()

        puntuacion = sum(
            1 for palabra in palabras
            if palabra in texto
        )

        if puntuacion > 0:
            resultados.append(
                (puntuacion, contenido)
            )

    resultados.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        contenido
        for _, contenido in resultados[:limite]
    ]


def contar_mensajes(usuario):
    with conectar() as conn:
        resultado = conn.execute(
            """
            SELECT COUNT(*)
            FROM mensajes
            WHERE usuario = ?
            """,
            (usuario,)
        ).fetchone()

    return resultado[0]
