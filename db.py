"""Capa de acceso a la base de datos: conexión y creación del schema."""
import sqlite3

DB_PATH = "stratos.db"


def get_connection():
    """Devuelve una conexión con claves foráneas activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS pilotos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT    NOT NULL,
            apellido     TEXT    NOT NULL,
            nacionalidad TEXT    NOT NULL,
            edad         INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS monoplazas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo    TEXT    NOT NULL,
            motor     TEXT    NOT NULL,
            potencia  INTEGER NOT NULL,
            id_piloto INTEGER NOT NULL,
            FOREIGN KEY (id_piloto) REFERENCES pilotos(id)
        );

        CREATE TABLE IF NOT EXISTS circuitos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_gp   TEXT    NOT NULL,
            pais        TEXT    NOT NULL,
            longitud_km REAL    NOT NULL,
            tipo_pista  TEXT    NOT NULL
        );
    """)
    conn.commit()
    conn.close()
