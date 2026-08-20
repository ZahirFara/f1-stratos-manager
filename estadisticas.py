"""Parte 3 de la ampliacion: medidas de tendencia central con pandas.

Arma un DataFrame con los datos que ya estan cargados en la base y calcula
media, mediana y moda sobre una columna numerica. Tambien arma el parrafo
de interpretacion de esos valores.

Este modulo NO escribe SQL: las filas llegan desde las mismas funciones de
listado que ya usaba el CRUD (repository.listar_circuitos, listar_pilotos y
listar_monoplazas), de manera que las consultas siguen viviendo unicamente
en repository.py y db.py. Tampoco contiene logica de interfaz.
"""
import pandas as pd
import repository as repo


# ------------- objetos del repository -> filas para el DataFrame -------------
def filas_circuitos():
    """Reutiliza el listado del repository y arma una fila por circuito."""
    return [{"nombre_gp": c.nombre_gp,
             "pais": c.pais,
             "longitud_km": c.longitud_km,
             "tipo_pista": c.tipo_pista}
            for c in repo.listar_circuitos()]


def filas_pilotos():
    """Reutiliza el listado del repository y arma una fila por piloto."""
    return [{"nombre": p.nombre,
             "apellido": p.apellido,
             "nacionalidad": p.nacionalidad,
             "edad": p.edad}
            for p in repo.listar_pilotos()]


def filas_monoplazas():
    """Reutiliza el listado del repository y arma una fila por monoplaza."""
    return [{"modelo": m.modelo,
             "motor": m.motor,
             "potencia": m.potencia}
            for m in repo.listar_monoplazas()]


# Configuracion de cada dataset analizable: de donde salen las filas, que
# columna numerica se analiza y sobre que columna de texto se saca la moda.
DATASETS = {
    "Circuitos": {
        "filas": filas_circuitos,
        "columnas": ["nombre_gp", "pais", "longitud_km", "tipo_pista"],
        "columna_numerica": "longitud_km",
        "etiqueta_numerica": "Longitud del circuito",
        "unidad": "km",
        "columna_categorica": "tipo_pista",
        "etiqueta_categorica": "Tipo de pista",
    },
    "Pilotos": {
        "filas": filas_pilotos,
        "columnas": ["nombre", "apellido", "nacionalidad", "edad"],
        "columna_numerica": "edad",
        "etiqueta_numerica": "Edad de los pilotos",
        "unidad": "anios",
        "columna_categorica": "nacionalidad",
        "etiqueta_categorica": "Nacionalidad",
    },
    "Monoplazas": {
        "filas": filas_monoplazas,
        "columnas": ["modelo", "motor", "potencia"],
        "columna_numerica": "potencia",
        "etiqueta_numerica": "Potencia de los monoplazas",
        "unidad": "hp",
        "columna_categorica": "motor",
        "etiqueta_categorica": "Motor",
    },
}


def cargar_dataframe(nombre_dataset):
    """Devuelve un DataFrame de pandas con los datos cargados en la base."""
    config = DATASETS[nombre_dataset]
    return pd.DataFrame(config["filas"](), columns=config["columnas"])


def formatear(valor):
    """Muestra el numero con hasta 3 decimales y sin ceros al final."""
    texto = f"{valor:.3f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def tendencia_central(df, columna):
    """Media, mediana y moda de una columna numerica. None si no hay datos."""
    serie = pd.to_numeric(df[columna], errors="coerce").dropna()
    if serie.empty:
        return None
    modas = serie.mode()                       # puede haber mas de una moda
    frecuencia = int((serie == modas.iloc[0]).sum())
    return {
        "n": int(serie.count()),
        "media": float(serie.mean()),
        "mediana": float(serie.median()),
        "modas": [float(m) for m in modas],
        "frecuencia_moda": frecuencia,
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
    }


def texto_moda(resumen):
    """Devuelve la moda lista para mostrar (puede ser mas de un valor)."""
    if resumen is None or not resumen["modas"]:
        return "-"
    return " / ".join(formatear(m) for m in resumen["modas"])


def moda_categorica(df, columna):
    """Moda de una columna de texto. Devuelve (lista_de_modas, frecuencia)."""
    serie = df[columna].dropna()
    if serie.empty:
        return [], 0
    modas = serie.mode()
    if modas.empty:
        return [], 0
    frecuencia = int((serie == modas.iloc[0]).sum())
    return [str(m) for m in modas], frecuencia


def interpretar(resumen, etiqueta, unidad=""):
    """Arma el parrafo que interpreta media, mediana y moda."""
    if resumen is None:
        return "Todavia no hay datos suficientes para interpretar."

    media = resumen["media"]
    mediana = resumen["mediana"]
    sufijo = f" {unidad}" if unidad else ""
    diferencia = abs(media - mediana)
    relativa = (diferencia / media * 100) if media else 0

    if relativa < 5:
        parte_1 = (
            f"Sobre {resumen['n']} registros, la media de {etiqueta.lower()} es "
            f"{formatear(media)}{sufijo} y la mediana {formatear(mediana)}{sufijo}: "
            "son valores muy parecidos, asi que la distribucion es bastante simetrica "
            "y no hay casos extremos que arrastren el promedio."
        )
    elif media > mediana:
        parte_1 = (
            f"Sobre {resumen['n']} registros, la media de {etiqueta.lower()} "
            f"({formatear(media)}{sufijo}) es mayor que la mediana "
            f"({formatear(mediana)}{sufijo}): unos pocos valores altos "
            f"(el maximo es {formatear(resumen['maximo'])}{sufijo}) tiran del promedio "
            "hacia arriba, mientras que la mitad de los registros queda por debajo de "
            f"{formatear(mediana)}{sufijo}."
        )
    else:
        parte_1 = (
            f"Sobre {resumen['n']} registros, la media de {etiqueta.lower()} "
            f"({formatear(media)}{sufijo}) es menor que la mediana "
            f"({formatear(mediana)}{sufijo}): unos pocos valores bajos "
            f"(el minimo es {formatear(resumen['minimo'])}{sufijo}) empujan el promedio "
            "hacia abajo, por lo que la mitad de los registros supera "
            f"{formatear(mediana)}{sufijo}."
        )

    frecuencia = resumen["frecuencia_moda"]
    if frecuencia <= 1:
        parte_2 = (
            " Ningun valor se repite, asi que la moda no aporta mucho en este conjunto: "
            "los datos estan muy repartidos."
        )
    elif len(resumen["modas"]) == 1:
        parte_2 = (
            f" Hay una moda clara: el valor {formatear(resumen['modas'][0])}{sufijo} "
            f"aparece {frecuencia} veces sobre {resumen['n']} registros."
        )
    else:
        valores = " y ".join(formatear(m) for m in resumen["modas"])
        parte_2 = (
            f" El conjunto es multimodal: los valores {valores}{sufijo} se repiten "
            f"{frecuencia} veces cada uno, asi que no hay un unico valor tipico."
        )
    return parte_1 + parte_2
