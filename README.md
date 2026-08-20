# F1 Stratos Manager — ORT Racing Team

Sistema de gestión de una escudería de Fórmula 1 (temporada 2026): pilotos, monoplazas y calendario de circuitos, con persistencia en SQLite, interfaz en Streamlit y un módulo de análisis estadístico con Pandas. Dejamos un archivo de Instrucciones para leer antes de ejecutarlo.

**Materia:** Estadística y Datos con Python — 5.º Año

## Integrantes

- **Ignacio Britos** — [@IgnacioBritoss](https://github.com/IgnacioBritoss)
- **Lucas Park**
- **Guido Jacofsky**
- **Zahir Fara** — [@ZahirFara](https://github.com/ZahirFara)

---

## Cómo ejecutar el proyecto

**Requisito:** tener Python 3.10 o superior instalado.

### 1. Instalar las librerías

Parado en la carpeta del proyecto, abrí una terminal y ejecutá:

```bash
pip install -r requirements.txt
```

### 2. Iniciar la aplicación

```bash
python -m streamlit run app.py
```

Se abre sola en el navegador, en **http://localhost:8501**

> **Si aparece el error `streamlit no se reconoce como nombre de un cmdlet`**, es porque la carpeta de scripts de Python no está en el PATH de Windows. Usá siempre la forma `python -m streamlit run app.py` como figura arriba y el problema se evita.

Para cerrar la aplicación: **Ctrl+C** en la terminal.

### 3. Cargar los datos

La base de datos (`stratos.db`) se crea vacía la primera vez que abrís la app, así que hay que cargarle los datos:

1. En el menú lateral, entrá a **Estadísticas**.
2. En la pestaña **Importar CSV**, con *Circuitos* seleccionado, apretá **Importar circuitos a la base** → se dan de alta 22 circuitos.
3. Cambiá el desplegable a *Pilotos* y apretá **Importar pilotos a la base** → se dan de alta 18 pilotos.

Listo. Ya podés navegar por **Pilotos**, **Monoplazas**, **Calendario** y **Estadísticas**.

---

## Cómo está organizado el proyecto

**Todo el SQL vive en `repository.py` y `db.py`.** Ningún otro archivo escribe consultas: ni `app.py`, ni `importador.py`, ni `estadisticas.py`. Los tres pasan siempre por la capa de datos.

| Archivo | Qué hace |
|---|---|
| `db.py` | Conexión a SQLite y creación de las tablas (con claves foráneas activadas). |
| `models.py` | Clases POO: `Piloto`, `Monoplaza`, `Circuito`. |
| `repository.py` | Capa de datos: CRUD completo. Convierte filas → objetos con bucles. |
| `importador.py` | Lee los CSV con `pandas.read_csv()` y da de alta cada fila usando `repository`. |
| `estadisticas.py` | Calcula media, mediana y moda con Pandas, sobre los datos que devuelve `repository`. |
| `app.py` | Interfaz Streamlit: navegación, filtros, formularios y validaciones. |
| `datos/` | Los datasets propios en CSV. |

### Métodos de instancia (POO)

- **Piloto**: `nombre_completo()`, `categoria()` → Junior / Senior / Veterano según la edad.
- **Monoplaza**: `es_alta_potencia()`, `piloto_asignado()`.
- **Circuito**: `es_largo()`, `clasificacion_longitud()` → Largo / Corto.

### Validaciones

Campos obligatorios no vacíos, edad entre 16 y 70, potencia mayor a 0, longitud mayor a 0. El borrado de un piloto se bloquea si tiene un monoplaza asignado (restricción de clave foránea).

---

# Ampliación: datos propios y tendencia central

Todo el agregado vive en el módulo **Estadísticas** del menú lateral, que tiene dos pestañas: *Importar CSV* y *Análisis*.

## Parte 1 — Dataset propio (CSV)

Armamos dos archivos con datos ficticios pero realistas, cuyas columnas coinciden con los atributos de las entidades que ya teníamos modeladas:

| Archivo | Filas | Columnas | Columna numérica |
|---|---|---|---|
| `datos/circuitos.csv` | 22 | `nombre_gp`, `pais`, `longitud_km`, `tipo_pista` | `longitud_km` |
| `datos/pilotos.csv` | 18 | `nombre`, `apellido`, `nacionalidad`, `edad` | `edad` |

Dejamos valores repetidos a propósito en las columnas numéricas para que la moda tenga sentido: `5.412` km aparece 3 veces (Baréin, Miami y Qatar) y la edad `28` aparece 3 veces (Verstappen, Leclerc y Russell).

## Parte 2 — Importación con Pandas

`importador.py` lee el archivo con `pandas.read_csv()` y recorre el DataFrame con un `for`, llamando en cada vuelta a la **misma función de alta que ya usaba el CRUD** (`repo.crear_circuito()` / `repo.crear_piloto()`). No hay inserts masivos ni SQL nuevo.

Además, la importación omite los registros que ya están en la base, así que se puede correr más de una vez sin duplicar nada. Al volver a importar, la app responde *"No se agregó nada: los 22 registros del CSV ya estaban en la base"*.

Después de importar, los registros nuevos se ven en las vistas de listado de **Calendario** y **Pilotos**, con los filtros y las categorías calculadas funcionando normalmente.

## Parte 3 — Medidas de tendencia central

`estadisticas.py` toma los datos ya cargados en la base y calcula **media, mediana y moda** sobre la columna numérica de cada entidad, más la moda de una columna de texto. La pestaña **Análisis** los muestra rotulados, junto con un párrafo de interpretación que se arma a partir de los valores calculados (compara la media contra la mediana y mira cuántas veces se repite la moda), así que si cambian los datos cambia el texto.

Las filas no se piden con una consulta propia: llegan desde las **mismas funciones de listado que ya usaba el CRUD** (`repo.listar_circuitos()`, `repo.listar_pilotos()`, `repo.listar_monoplazas()`), y con ellas se arma el DataFrame. De esa forma el cálculo se hace íntegramente con Pandas sobre los datos de la base, pero sin sacar el SQL de la capa que le corresponde. Es el mismo criterio que en la Parte 2, donde la importación reutiliza las funciones de alta en lugar de escribir sus propios `INSERT`.

No se usó `groupby` ni se agregaron gráficos, tal como aclara la consigna.

### Resultados

**Circuitos** — longitud, en km (22 registros):

| Medida | Valor |
|---|---|
| Media | 5.131 |
| Mediana | 5.279 |
| Moda | 5.412 |
| Mínimo / Máximo | 3.337 / 7.004 |
| Moda de `tipo_pista` | Mixto (7 de 22) |

**Pilotos** — edad, en años (18 registros):

| Medida | Valor |
|---|---|
| Media | 27.278 |
| Mediana | 27 |
| Moda | 28 |
| Mínimo / Máximo | 19 / 44 |
| Moda de `nacionalidad` | Reino Unido (4 de 18) |

---

## Conclusión del grupo

En los circuitos, la media (5.131 km) y la mediana (5.279 km) se llevan menos de 0.15 km, alrededor de un 3 % de diferencia. Eso nos dice que la distribución de longitudes es bastante simétrica: no hay trazados tan extremos como para arrastrar el promedio hacia un lado. La media queda apenas por debajo de la mediana porque los circuitos urbanos cortos —Mónaco, con 3.337 km, es el mínimo— pesan un poco más que el máximo de Bélgica (7.004 km). La moda es clara: 5.412 km aparece 3 veces sobre 22 registros, así que la longitud más típica del calendario ronda los 5.4 km. Sumado a que el tipo de pista más frecuente es Mixto (7 de 22), el retrato que sale es el de un calendario parejo, sin demasiados casos raros.

Con los pilotos aprendimos algo que no esperábamos. La media (27.278 años) y la mediana (27) también quedan casi iguales, y con el criterio anterior habríamos concluido que las edades están repartidas de forma pareja. Pero al mirar los datos vimos que no es así: conviven un grupo de pilotos muy jóvenes (de 19 a 22 años) con algunos veteranos de 41 y 44, y esos dos extremos se terminan compensando entre sí. La conclusión que nos llevamos es que **que la media y la mediana coincidan no garantiza que los datos sean homogéneos**; recién mirando el mínimo, el máximo y la moda (28 años, 3 pilotos) se entiende la forma real del conjunto.

También nos sirvió para ver por qué la consigna insistía con armar un dataset más grande. Con los 3 registros de prueba que teníamos mientras programábamos el CRUD, las tres medidas no decían nada: la moda no existía porque ningún valor se repetía. Recién con 22 y 18 registros los cálculos empiezan a describir algo. En lo técnico, lo que más valoramos es que no tuvimos que reescribir nada de lo que ya andaba: la importación con Pandas reutiliza las mismas funciones de alta del CRUD, y el módulo de estadísticas lee de la base sin tocar la capa de datos. La separación en capas que habíamos hecho en la primera entrega hizo que agregar todo esto fuera cuestión de sumar dos archivos y una vista.

---

## Correcciones posteriores a la entrega

### 20/08/2026 — El módulo de estadísticas rompía la separación de capas

**El error.** `estadisticas.py` consultaba la base con SQL propio: tenía escritas sus consultas (`SELECT nombre_gp, pais, longitud_km, tipo_pista FROM circuitos`) y las ejecutaba con `pandas.read_sql()` abriendo su propia conexión. Eso contradecía lo que dice este mismo README —que el SQL vive únicamente en `repository.py` y `db.py`— y dejaba la capa de datos salteada justo en el archivo que agregamos en la ampliación. El código funcionaba, pero la arquitectura que veníamos sosteniendo desde la primera entrega ya no era cierta.

**Cómo quedó.** `estadisticas.py` no escribe una sola línea de SQL ni abre conexiones. Las filas se piden a las funciones de listado que ya existían en el repository, las mismas que usan las vistas de listado de la app:

```python
def filas_circuitos():
    """Reutiliza el listado del repository y arma una fila por circuito."""
    return [{"nombre_gp": c.nombre_gp,
             "pais": c.pais,
             "longitud_km": c.longitud_km,
             "tipo_pista": c.tipo_pista}
            for c in repo.listar_circuitos()]


def cargar_dataframe(nombre_dataset):
    """Devuelve un DataFrame de pandas con los datos cargados en la base."""
    config = DATASETS[nombre_dataset]
    return pd.DataFrame(config["filas"](), columns=config["columnas"])
```

El cálculo de media, mediana y moda no se tocó: sigue siendo Pandas puro sobre el DataFrame, y los resultados son idénticos a los de antes. Lo único que cambió es de dónde salen las filas. Ahora la Parte 3 usa el mismo criterio que la Parte 2, donde la importación reutiliza `crear_circuito()` y `crear_piloto()` en vez de escribir sus propios `INSERT`.

**Verificación.** Buscando `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `read_sql`, `.execute(` y `get_connection` en todos los `.py` del proyecto, las coincidencias aparecen solo en `repository.py` y `db.py`. Ni `app.py`, ni `importador.py`, ni `estadisticas.py` tienen una sola.
