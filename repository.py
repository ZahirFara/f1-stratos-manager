"""Capa de datos (repository): CRUD + transformacion de filas a objetos.
No contiene logica de interfaz."""
import sqlite3
from db import get_connection
from models import Piloto, Monoplaza, Circuito


# ----------------------------- PILOTOS -----------------------------
def crear_piloto(nombre, apellido, nacionalidad, edad):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pilotos (nombre, apellido, nacionalidad, edad) VALUES (?, ?, ?, ?)",
        (nombre, apellido, nacionalidad, edad))
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def listar_pilotos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, apellido, nacionalidad, edad FROM pilotos")
    filas = cur.fetchall()
    conn.close()
    pilotos = []
    for f in filas:                      # bucle: filas -> objetos
        pilotos.append(Piloto(f[0], f[1], f[2], f[3], f[4]))
    return pilotos


def obtener_piloto(id_piloto):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, apellido, nacionalidad, edad FROM pilotos WHERE id = ?",
        (id_piloto,))
    f = cur.fetchone()
    conn.close()
    if f is None:
        return None
    return Piloto(f[0], f[1], f[2], f[3], f[4])


def actualizar_piloto(id_piloto, nombre, apellido, nacionalidad, edad):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE pilotos SET nombre = ?, apellido = ?, nacionalidad = ?, edad = ? WHERE id = ?",
        (nombre, apellido, nacionalidad, edad, id_piloto))
    conn.commit()
    conn.close()


def eliminar_piloto(id_piloto):
    """Devuelve True si se borro; False si tiene un monoplaza asignado (FK)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM pilotos WHERE id = ?", (id_piloto,))
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    finally:
        conn.close()
    return ok


def filtrar_pilotos_por_nacionalidad(nacionalidad):
    return [p for p in listar_pilotos() if p.nacionalidad == nacionalidad]


def nacionalidades_unicas():
    return sorted({p.nacionalidad for p in listar_pilotos()})


# --------------------------- MONOPLAZAS ----------------------------
def crear_monoplaza(modelo, motor, potencia, id_piloto):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO monoplazas (modelo, motor, potencia, id_piloto) VALUES (?, ?, ?, ?)",
        (modelo, motor, potencia, id_piloto))
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def listar_monoplazas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.modelo, m.motor, m.potencia, m.id_piloto, p.nombre, p.apellido
        FROM monoplazas m
        INNER JOIN pilotos p ON m.id_piloto = p.id
    """)
    filas = cur.fetchall()
    conn.close()
    monoplazas = []
    for f in filas:
        monoplazas.append(Monoplaza(f[0], f[1], f[2], f[3], f[4],
                                    piloto_nombre=f[5], piloto_apellido=f[6]))
    return monoplazas


def obtener_monoplaza(id_monoplaza):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, modelo, motor, potencia, id_piloto FROM monoplazas WHERE id = ?",
        (id_monoplaza,))
    f = cur.fetchone()
    conn.close()
    if f is None:
        return None
    return Monoplaza(f[0], f[1], f[2], f[3], f[4])


def actualizar_monoplaza(id_monoplaza, modelo, motor, potencia, id_piloto):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE monoplazas SET modelo = ?, motor = ?, potencia = ?, id_piloto = ? WHERE id = ?",
        (modelo, motor, potencia, id_piloto, id_monoplaza))
    conn.commit()
    conn.close()


def eliminar_monoplaza(id_monoplaza):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM monoplazas WHERE id = ?", (id_monoplaza,))
    conn.commit()
    conn.close()


# ---------------------------- CIRCUITOS ----------------------------
def crear_circuito(nombre_gp, pais, longitud_km, tipo_pista):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO circuitos (nombre_gp, pais, longitud_km, tipo_pista) VALUES (?, ?, ?, ?)",
        (nombre_gp, pais, longitud_km, tipo_pista))
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return nuevo_id


def listar_circuitos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre_gp, pais, longitud_km, tipo_pista FROM circuitos")
    filas = cur.fetchall()
    conn.close()
    circuitos = []
    for f in filas:
        circuitos.append(Circuito(f[0], f[1], f[2], f[3], f[4]))
    return circuitos


def obtener_circuito(id_circuito):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre_gp, pais, longitud_km, tipo_pista FROM circuitos WHERE id = ?",
        (id_circuito,))
    f = cur.fetchone()
    conn.close()
    if f is None:
        return None
    return Circuito(f[0], f[1], f[2], f[3], f[4])


def actualizar_circuito(id_circuito, nombre_gp, pais, longitud_km, tipo_pista):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE circuitos SET nombre_gp = ?, pais = ?, longitud_km = ?, tipo_pista = ? WHERE id = ?",
        (nombre_gp, pais, longitud_km, tipo_pista, id_circuito))
    conn.commit()
    conn.close()


def eliminar_circuito(id_circuito):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM circuitos WHERE id = ?", (id_circuito,))
    conn.commit()
    conn.close()


def filtrar_circuitos_por_tipo(tipo_pista):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre_gp, pais, longitud_km FROM circuitos WHERE tipo_pista = ?",
        (tipo_pista,))
    filas = cur.fetchall()
    conn.close()
    circuitos = []
    for f in filas:
        circuitos.append(Circuito(f[0], f[1], f[2], f[3], tipo_pista))
    return circuitos


def tipos_pista_unicos():
    return sorted({c.tipo_pista for c in listar_circuitos()})


# -------------------------- DATOS DE EJEMPLO -----------------------
def seed():
    """Carga datos demo solo si las tablas estan vacias."""
    if listar_pilotos():
        return
    p1 = crear_piloto("Max", "Verstappen", "Paises Bajos", 28)
    p2 = crear_piloto("Franco", "Colapinto", "Argentina", 22)
    p3 = crear_piloto("Lewis", "Hamilton", "Reino Unido", 41)
    crear_monoplaza("RB22", "Honda RBPT", 900, p1)
    crear_monoplaza("AMR26", "Mercedes", 870, p2)
    crear_monoplaza("SF26", "Ferrari", 880, p3)
    crear_circuito("GP Monaco", "Monaco", 3.337, "Urbano")
    crear_circuito("GP Italia", "Italia", 5.793, "Velocidad")
    crear_circuito("GP Argentina", "Argentina", 4.259, "Mixto")
