# F1 Stratos Manager — ORT Racing Team

Sistema de gestión de escudería (temporada 2026): pilotos, monoplazas y circuitos, con persistencia en SQLite e interfaz Streamlit.

## Arquitectura

SQL aislado de la interfaz.

- `db.py` — conexión y creación del schema (FK activadas).
- `models.py` — clases POO `Piloto`, `Monoplaza`, `Circuito` (2 métodos de instancia c/u).
- `repository.py` — capa de datos: CRUD completo, convierte filas → objetos con bucles.
- `app.py` — interfaz Streamlit: navegación, filtros, formularios y validaciones.

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
