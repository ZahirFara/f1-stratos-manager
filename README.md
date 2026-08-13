# F1 Stratos Manager — ORT Racing Team

Sistema de gestión de escudería (temporada 2026): pilotos, monoplazas y circuitos, con persistencia en SQLite e interfaz Streamlit.

## Arquitectura

SQL aislado de la interfaz.

- `db.py` — conexión y creación del schema (FK activadas).
- `models.py` — clases POO `Piloto`, `Monoplaza`, `Circuito` (2 métodos de instancia c/u).
- `repository.py` — capa de datos: CRUD completo, convierte filas → objetos con bucles.
- `importador.py` — lectura de los CSV con pandas y alta de cada fila vía `repository`.
- `estadisticas.py` — cálculo de media, mediana y moda con pandas (`read_sql`).
- `app.py` — interfaz Streamlit: navegación, filtros, formularios y validaciones.
- `datos/` — datasets propios en CSV (`circuitos.csv`, `pilotos.csv`).

## Métodos de instancia

- **Piloto**: `nombre_completo()`, `categoria()` (Junior/Senior/Veterano).
- **Monoplaza**: `es_alta_potencia()`, `piloto_asignado()`.
- **Circuito**: `es_largo()`, `clasificacion_longitud()` (Largo/Corto).

## Validaciones

Campos no vacíos, edad 16–70, potencia > 0, longitud > 0. Borrado de piloto bloqueado si tiene monoplaza asignado (FK).

## Uso

```bash
pip install -r requirements.txt
streamlit run app.py
```

Botón **Cargar datos de ejemplo** en el sidebar para datos demo.

---

# Ampliación: datos propios y tendencia central

Módulo **Estadísticas** del menú lateral. Resuelve las tres partes de la ampliación.

## Parte 1 — Dataset propio (CSV)

Dos archivos en `datos/`, con columnas que coinciden con los atributos de las entidades ya modeladas:

| Archivo | Filas | Columnas | Columna numérica |
|---|---|---|---|
| `datos/circuitos.csv` | 22 | `nombre_gp`, `pais`, `longitud_km`, `tipo_pista` | `longitud_km` |
| `datos/pilotos.csv` | 18 | `nombre`, `apellido`, `nacionalidad`, `edad` | `edad` |

Hay valores repetidos a propósito en las columnas numéricas (`5.412` km aparece 3 veces; la edad `28` aparece 3 veces) para que la moda tenga sentido.

## Parte 2 — Importación con pandas

`importador.py` lee el CSV con `pandas.read_csv()` y recorre el DataFrame con un `for`, dando de alta cada fila con las **mismas funciones del CRUD** (`repo.crear_circuito()` / `repo.crear_piloto()`). No usa inserts masivos ni SQL propio.

Desde la app: **Estadísticas → pestaña Importar CSV** → vista previa del archivo → botón *Importar*. Los registros que ya están en la base se omiten, así que se puede importar más de una vez sin duplicar. Después se verifica el resultado en el listado de Calendario o Pilotos.

## Parte 3 — Medidas de tendencia central

`estadisticas.py` lee los datos ya cargados con `pandas.read_sql()` y calcula **media, mediana y moda** sobre la columna numérica de cada entidad (más la moda de una columna de texto). La pestaña **Análisis** los muestra rotulados junto con un párrafo de interpretación generado a partir de esos valores.

### Interpretación de los resultados (circuitos)

Con los 22 circuitos del CSV: **media 5.131 km**, **mediana 5.279 km**, **moda 5.412 km**.

La media y la mediana son muy parecidas (se llevan menos de 0.15 km, un 3 % de diferencia), así que la distribución de longitudes es bastante simétrica: no hay circuitos tan extremos como para arrastrar el promedio. La media queda apenas por debajo de la mediana porque los trazados urbanos cortos —Mónaco con 3.337 km es el mínimo— pesan un poco más que el máximo de Bélgica (7.004 km). La moda es clara: 5.412 km aparece 3 veces sobre 22 registros, o sea que la longitud más típica del calendario ronda los 5.4 km. En la columna de texto, la moda de `tipo_pista` es **Mixto** (7 de 22), el tipo de circuito más habitual.

En pilotos: **media 27.28 años**, **mediana 27**, **moda 28** (3 pilotos). También quedan casi iguales, pero acá conviven dos grupos —varios juniors de 19 a 22 y algunos veteranos de 41 y 44— que terminan compensándose; la moda de nacionalidad es **Reino Unido** (4 de 18).
