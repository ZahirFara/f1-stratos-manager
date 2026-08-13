"""Interfaz grafica (Streamlit). Sin SQL: solo consume repository,
importador (carga de CSV con pandas) y estadisticas (tendencia central)."""
import streamlit as st
from db import init_db
import repository as repo
import importador
import estadisticas as stats

st.set_page_config(page_title="F1 Stratos Manager", layout="wide")
init_db()


# ============================== PILOTOS ==============================
def vista_pilotos():
    st.header("Pilotos")
    tab_lista, tab_alta, tab_edit = st.tabs(["Listado", "Alta", "Editar / Baja"])

    with tab_lista:
        opciones = ["Todas"] + repo.nacionalidades_unicas()
        filtro = st.selectbox("Filtrar por nacionalidad", opciones)
        pilotos = (repo.listar_pilotos() if filtro == "Todas"
                   else repo.filtrar_pilotos_por_nacionalidad(filtro))
        if pilotos:
            st.dataframe([{
                "ID": p.id,
                "Piloto": p.nombre_completo(),
                "Nacionalidad": p.nacionalidad,
                "Edad": p.edad,
                "Categoria": p.categoria(),
            } for p in pilotos], use_container_width=True)
        else:
            st.info("Sin pilotos cargados.")

    with tab_alta:
        with st.form("alta_piloto", clear_on_submit=True):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            nacionalidad = st.text_input("Nacionalidad")
            edad = st.number_input("Edad", min_value=0, max_value=99, value=25, step=1)
            if st.form_submit_button("Crear piloto"):
                errores = []
                if not nombre.strip():
                    errores.append("Nombre vacio.")
                if not apellido.strip():
                    errores.append("Apellido vacio.")
                if not nacionalidad.strip():
                    errores.append("Nacionalidad vacia.")
                if edad < 16 or edad > 70:
                    errores.append("Edad fuera de rango (16-70).")
                if errores:
                    st.error(" ".join(errores))
                else:
                    repo.crear_piloto(nombre.strip(), apellido.strip(),
                                      nacionalidad.strip(), int(edad))
                    st.success("Piloto creado.")
                    st.rerun()

    with tab_edit:
        pilotos = repo.listar_pilotos()
        if not pilotos:
            st.info("Sin pilotos para editar.")
            return
        mapa = {f"{p.id} - {p.nombre_completo()}": p for p in pilotos}
        sel = st.selectbox("Seleccionar piloto", list(mapa.keys()), key="edit_pil")
        p = mapa[sel]
        nombre = st.text_input("Nombre", p.nombre, key="en")
        apellido = st.text_input("Apellido", p.apellido, key="ea")
        nacionalidad = st.text_input("Nacionalidad", p.nacionalidad, key="enac")
        edad = st.number_input("Edad", min_value=0, max_value=99, value=p.edad, step=1, key="ee")
        c1, c2 = st.columns(2)
        if c1.button("Guardar cambios"):
            if not (nombre.strip() and apellido.strip() and nacionalidad.strip()):
                st.error("Campos obligatorios vacios.")
            elif edad < 16 or edad > 70:
                st.error("Edad fuera de rango (16-70).")
            else:
                repo.actualizar_piloto(p.id, nombre.strip(), apellido.strip(),
                                       nacionalidad.strip(), int(edad))
                st.success("Actualizado.")
                st.rerun()
        if c2.button("Eliminar", type="primary"):
            if repo.eliminar_piloto(p.id):
                st.success("Eliminado.")
                st.rerun()
            else:
                st.error("No se puede borrar: tiene un monoplaza asignado.")


# ============================ MONOPLAZAS ============================
def vista_monoplazas():
    st.header("Monoplazas")
    pilotos = repo.listar_pilotos()
    if not pilotos:
        st.warning("Carga al menos un piloto antes de registrar monoplazas.")
        return
    mapa_pil = {f"{p.id} - {p.nombre_completo()}": p.id for p in pilotos}

    tab_lista, tab_alta, tab_edit = st.tabs(["Listado", "Alta", "Editar / Baja"])

    with tab_lista:
        monoplazas = repo.listar_monoplazas()
        if monoplazas:
            st.dataframe([{
                "ID": m.id,
                "Modelo": m.modelo,
                "Motor": m.motor,
                "Potencia (hp)": m.potencia,
                "Alta potencia": "Si" if m.es_alta_potencia() else "No",
                "Piloto": m.piloto_asignado(),
            } for m in monoplazas], use_container_width=True)
        else:
            st.info("Sin monoplazas cargados.")

    with tab_alta:
        with st.form("alta_mono", clear_on_submit=True):
            modelo = st.text_input("Modelo")
            motor = st.text_input("Motor")
            potencia = st.number_input("Potencia (hp)", min_value=0, value=800, step=10)
            piloto_sel = st.selectbox("Asignar piloto", list(mapa_pil.keys()))
            if st.form_submit_button("Crear monoplaza"):
                errores = []
                if not modelo.strip():
                    errores.append("Modelo vacio.")
                if not motor.strip():
                    errores.append("Motor vacio.")
                if potencia <= 0:
                    errores.append("Potencia debe ser positiva.")
                if errores:
                    st.error(" ".join(errores))
                else:
                    repo.crear_monoplaza(modelo.strip(), motor.strip(),
                                         int(potencia), mapa_pil[piloto_sel])
                    st.success("Monoplaza creado.")
                    st.rerun()

    with tab_edit:
        monoplazas = repo.listar_monoplazas()
        if not monoplazas:
            st.info("Sin monoplazas para editar.")
            return
        mapa = {f"{m.id} - {m.modelo}": m for m in monoplazas}
        sel = st.selectbox("Seleccionar monoplaza", list(mapa.keys()), key="edit_mono")
        m = mapa[sel]
        modelo = st.text_input("Modelo", m.modelo, key="mm")
        motor = st.text_input("Motor", m.motor, key="mt")
        potencia = st.number_input("Potencia (hp)", min_value=0, value=m.potencia, step=10, key="mp")
        claves = list(mapa_pil.keys())
        idx = next((i for i, k in enumerate(claves) if mapa_pil[k] == m.id_piloto), 0)
        piloto_sel = st.selectbox("Piloto", claves, index=idx, key="mpil")
        c1, c2 = st.columns(2)
        if c1.button("Guardar cambios", key="mg"):
            if not (modelo.strip() and motor.strip()):
                st.error("Campos obligatorios vacios.")
            elif potencia <= 0:
                st.error("Potencia debe ser positiva.")
            else:
                repo.actualizar_monoplaza(m.id, modelo.strip(), motor.strip(),
                                          int(potencia), mapa_pil[piloto_sel])
                st.success("Actualizado.")
                st.rerun()
        if c2.button("Eliminar", type="primary", key="md"):
            repo.eliminar_monoplaza(m.id)
            st.success("Eliminado.")
            st.rerun()


# ============================= CIRCUITOS ============================
def vista_circuitos():
    st.header("Calendario de Circuitos")
    tipos_base = ["Urbano", "Velocidad", "Mixto", "Tecnico"]
    tab_lista, tab_alta, tab_edit = st.tabs(["Listado", "Alta", "Editar / Baja"])

    with tab_lista:
        opciones = ["Todos"] + repo.tipos_pista_unicos()
        filtro = st.selectbox("Filtrar por tipo de pista", opciones)
        circuitos = (repo.listar_circuitos() if filtro == "Todos"
                     else repo.filtrar_circuitos_por_tipo(filtro))
        if circuitos:
            st.dataframe([{
                "ID": c.id,
                "GP": c.nombre_gp,
                "Pais": c.pais,
                "Longitud (km)": c.longitud_km,
                "Tipo": c.tipo_pista,
                "Clasificacion": c.clasificacion_longitud(),
            } for c in circuitos], use_container_width=True)
        else:
            st.info("Sin circuitos cargados.")

    with tab_alta:
        with st.form("alta_circ", clear_on_submit=True):
            nombre_gp = st.text_input("Nombre del GP")
            pais = st.text_input("Pais")
            longitud = st.number_input("Longitud (km)", min_value=0.0, value=5.0, step=0.1, format="%.3f")
            tipo = st.selectbox("Tipo de pista", tipos_base)
            if st.form_submit_button("Crear circuito"):
                errores = []
                if not nombre_gp.strip():
                    errores.append("Nombre del GP vacio.")
                if not pais.strip():
                    errores.append("Pais vacio.")
                if longitud <= 0:
                    errores.append("Longitud debe ser positiva.")
                if errores:
                    st.error(" ".join(errores))
                else:
                    repo.crear_circuito(nombre_gp.strip(), pais.strip(),
                                        float(longitud), tipo)
                    st.success("Circuito creado.")
                    st.rerun()

    with tab_edit:
        circuitos = repo.listar_circuitos()
        if not circuitos:
            st.info("Sin circuitos para editar.")
            return
        mapa = {f"{c.id} - {c.nombre_gp}": c for c in circuitos}
        sel = st.selectbox("Seleccionar circuito", list(mapa.keys()), key="edit_circ")
        c = mapa[sel]
        nombre_gp = st.text_input("Nombre del GP", c.nombre_gp, key="cn")
        pais = st.text_input("Pais", c.pais, key="cp")
        longitud = st.number_input("Longitud (km)", min_value=0.0, value=float(c.longitud_km),
                                   step=0.1, format="%.3f", key="cl")
        tipo_actual = c.tipo_pista if c.tipo_pista in tipos_base else tipos_base[0]
        tipo = st.selectbox("Tipo de pista", tipos_base,
                            index=tipos_base.index(tipo_actual), key="ct")
        col1, col2 = st.columns(2)
        if col1.button("Guardar cambios", key="cg"):
            if not (nombre_gp.strip() and pais.strip()):
                st.error("Campos obligatorios vacios.")
            elif longitud <= 0:
                st.error("Longitud debe ser positiva.")
            else:
                repo.actualizar_circuito(c.id, nombre_gp.strip(), pais.strip(),
                                         float(longitud), tipo)
                st.success("Actualizado.")
                st.rerun()
        if col2.button("Eliminar", type="primary", key="cd"):
            repo.eliminar_circuito(c.id)
            st.success("Eliminado.")
            st.rerun()


# =========================== ESTADISTICAS ===========================
def vista_estadisticas():
    st.header("Estadisticas - Tendencia central")
    tab_import, tab_analisis = st.tabs(["Importar CSV", "Analisis"])

    # --- Parte 2: importar el dataset propio con pandas.read_csv() ---
    with tab_import:
        st.caption("Los CSV de la carpeta datos/ se leen con pandas.read_csv() y "
                   "cada fila se da de alta con las mismas funciones del CRUD.")
        nombre_csv = st.selectbox("Dataset a importar",
                                  list(importador.DATASETS_CSV.keys()), key="csv_ds")
        config_csv = importador.DATASETS_CSV[nombre_csv]
        try:
            df_csv = importador.leer_csv(config_csv["ruta"])
        except FileNotFoundError:
            st.error(f"No se encontro el archivo {config_csv['ruta']}.")
        else:
            st.write(f"{len(df_csv)} filas leidas del CSV.")
            st.dataframe(df_csv, use_container_width=True)
            if st.button(f"Importar {nombre_csv.lower()} a la base", key="btn_csv"):
                insertados, omitidos = config_csv["importar"](config_csv["ruta"])
                if insertados:
                    st.success(f"Se dieron de alta {insertados} registros nuevos. "
                               f"Omitidos por estar repetidos: {omitidos}.")
                else:
                    st.info(f"No se agrego nada: los {omitidos} registros del CSV "
                            "ya estaban en la base.")

    # --- Parte 3: media, mediana y moda calculadas con pandas ---
    with tab_analisis:
        nombre_ds = st.selectbox("Datos a analizar",
                                 list(stats.DATASETS.keys()), key="stats_ds")
        config = stats.DATASETS[nombre_ds]
        df = stats.cargar_dataframe(nombre_ds)
        if df.empty:
            st.info("No hay registros cargados. Importa el CSV desde la pestania anterior.")
            return
        st.caption(f"{len(df)} registros leidos de la base con pandas.read_sql().")

        resumen = stats.tendencia_central(df, config["columna_numerica"])
        if resumen is None:
            st.info("La columna numerica no tiene valores para analizar.")
            return

        st.subheader(f"{config['etiqueta_numerica']} ({config['unidad']})")
        c1, c2, c3 = st.columns(3)
        c1.metric("Media", stats.formatear(resumen["media"]))
        c2.metric("Mediana", stats.formatear(resumen["mediana"]))
        c3.metric("Moda", stats.texto_moda(resumen))
        st.caption(f"Minimo {stats.formatear(resumen['minimo'])} - "
                   f"maximo {stats.formatear(resumen['maximo'])} "
                   f"sobre {resumen['n']} registros.")

        st.markdown("**Interpretacion**")
        st.info(stats.interpretar(resumen, config["etiqueta_numerica"], config["unidad"]))

        modas_texto, frecuencia = stats.moda_categorica(df, config["columna_categorica"])
        if modas_texto:
            st.markdown(f"**Moda de {config['etiqueta_categorica'].lower()}:** "
                        f"{', '.join(modas_texto)} "
                        f"({frecuencia} de {len(df)} registros).")

        with st.expander("Ver los datos analizados"):
            st.dataframe(df, use_container_width=True)


# =============================== MAIN ===============================
st.title("F1 Stratos Manager - ORT Racing Team")

st.sidebar.title("Navegacion")
if st.sidebar.button("Cargar datos de ejemplo"):
    repo.seed()
    st.sidebar.success("Datos demo cargados.")

seccion = st.sidebar.radio("Modulo",
                           ["Pilotos", "Monoplazas", "Calendario", "Estadisticas"])

if seccion == "Pilotos":
    vista_pilotos()
elif seccion == "Monoplazas":
    vista_monoplazas()
elif seccion == "Calendario":
    vista_circuitos()
else:
    vista_estadisticas()
