"""Parte 2 de la ampliacion: importacion de los datasets propios (CSV) con pandas.

Lee los archivos de la carpeta datos/ con pandas.read_csv() y da de alta cada
fila recorriendo el DataFrame con un for y llamando a las mismas funciones de
alta del repository que ya usa el CRUD (crear_circuito / crear_piloto).
No contiene SQL ni logica de interfaz.
"""
import os
import pandas as pd
import repository as repo

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
CSV_CIRCUITOS = os.path.join(CARPETA_DATOS, "circuitos.csv")
CSV_PILOTOS = os.path.join(CARPETA_DATOS, "pilotos.csv")


def leer_csv(ruta):
    """Devuelve el DataFrame del CSV indicado (dataset armado en la Parte 1)."""
    return pd.read_csv(ruta)


def importar_circuitos(ruta=CSV_CIRCUITOS):
    """Da de alta cada fila del CSV de circuitos.

    Devuelve (insertados, omitidos). Se omiten los GP que ya estan en la base
    para poder ejecutar la importacion mas de una vez sin duplicar registros.
    """
    df = leer_csv(ruta)
    existentes = {c.nombre_gp.strip().lower() for c in repo.listar_circuitos()}
    insertados = 0
    omitidos = 0
    for _, fila in df.iterrows():          # bucle simple: un alta por fila
        nombre_gp = str(fila["nombre_gp"]).strip()
        if nombre_gp.lower() in existentes:
            omitidos += 1
            continue
        repo.crear_circuito(nombre_gp,
                            str(fila["pais"]).strip(),
                            float(fila["longitud_km"]),
                            str(fila["tipo_pista"]).strip())
        existentes.add(nombre_gp.lower())
        insertados += 1
    return insertados, omitidos


def importar_pilotos(ruta=CSV_PILOTOS):
    """Da de alta cada fila del CSV de pilotos.

    Devuelve (insertados, omitidos). La clave para no duplicar es nombre + apellido.
    """
    df = leer_csv(ruta)
    existentes = {(p.nombre.strip().lower(), p.apellido.strip().lower())
                  for p in repo.listar_pilotos()}
    insertados = 0
    omitidos = 0
    for _, fila in df.iterrows():          # bucle simple: un alta por fila
        nombre = str(fila["nombre"]).strip()
        apellido = str(fila["apellido"]).strip()
        if (nombre.lower(), apellido.lower()) in existentes:
            omitidos += 1
            continue
        repo.crear_piloto(nombre,
                          apellido,
                          str(fila["nacionalidad"]).strip(),
                          int(fila["edad"]))
        existentes.add((nombre.lower(), apellido.lower()))
        insertados += 1
    return insertados, omitidos


# Datasets disponibles para la vista de importacion (etiqueta -> ruta y funcion).
DATASETS_CSV = {
    "Circuitos": {"ruta": CSV_CIRCUITOS, "importar": importar_circuitos},
    "Pilotos": {"ruta": CSV_PILOTOS, "importar": importar_pilotos},
}
