"""
Interfaz grafica — Clasificacion de cuentas de Instagram (autenticas / falsas)
CCPG1044 Inteligencia Artificial — Grupo N.4 — ESPOL

Ejecucion local:
    python app_interfaz.py
    (abre automaticamente http://127.0.0.1:7860 en el navegador)

Ejecucion en Google Colab:
    !python app_interfaz.py --publica
    (genera un enlace publico temporal)

La carpeta del proyecto se busca en este orden:
    1. Variable de entorno PROYECTO_IA_CARPETA
    2. Argumento  --carpeta RUTA
    3. Rutas conocidas del grupo y la carpeta actual
"""

import argparse
import json
import os
import sys

import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import gradio as gr


# ----------------------------------------------------------------------------
# 1. Localizacion de la carpeta del proyecto
# ----------------------------------------------------------------------------

def localizar_carpeta(ruta_indicada=None):
    """Busca la carpeta que contiene split/particion.npz y resultados/."""
    candidatas = [
        ruta_indicada,
        os.environ.get('PROYECTO_IA_CARPETA'),
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
        '.',
        os.path.expanduser(r'C:/Users/JDC/Drive/Proyecto_IA_Grupo4'),
        '/content/drive/MyDrive/Proyecto_IA_Grupo4',
    ]
    for ruta in candidatas:
        if ruta and os.path.exists(os.path.join(ruta, 'split', 'particion.npz')):
            return os.path.abspath(ruta)
    raise FileNotFoundError(
        'No se encontro la carpeta del proyecto (debe contener split/particion.npz).\n'
        'Indiquela con:  python app_interfaz.py --carpeta "RUTA/DEL/PROYECTO"'
    )


parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--carpeta', default=None, help='Ruta de la carpeta del proyecto')
parser.add_argument('--publica', action='store_true', help='Genera un enlace publico (Colab)')
parser.add_argument('--puerto', type=int, default=7860)
ARGS, _ = parser.parse_known_args()

CARPETA = localizar_carpeta(ARGS.carpeta)
RUTA_SPLIT = os.path.join(CARPETA, 'split')
RUTA_RES = os.path.join(CARPETA, 'resultados')
print(f'Carpeta del proyecto: {CARPETA}')


# ----------------------------------------------------------------------------
# 2. Carga de datos, escalador y modelos entrenados
# ----------------------------------------------------------------------------

_datos = np.load(os.path.join(RUTA_SPLIT, 'particion.npz'), allow_pickle=True)
VARIABLES = [str(v) for v in _datos['variables']]
X_train = pd.DataFrame(_datos['X_train'], columns=VARIABLES)
X_test = pd.DataFrame(_datos['X_test'], columns=VARIABLES)
X_test_esc = pd.DataFrame(_datos['X_test_esc'], columns=VARIABLES)
y_train = _datos['y_train']
y_test = _datos['y_test']

ESCALADOR = joblib.load(os.path.join(RUTA_SPLIT, 'escalador.joblib'))

try:
    with open(os.path.join(RUTA_SPLIT, 'metadatos.json'), encoding='utf-8') as fh:
        METADATOS = json.load(fh)
    VARS_LOG = [str(v) for v in METADATOS['variables_log1p']]
except Exception:
    METADATOS = {}
    VARS_LOG = ['pos', 'flw', 'flg', 'bl', 'cl', 'erl', 'erc', 'hc', 'pr', 'fo', 'pi']

DICCIONARIO = {
    'pos': 'Numero de publicaciones',
    'flw': 'Seguidores (followers)',
    'flg': 'Cuentas seguidas (following)',
    'bl': 'Longitud de la biografia (caracteres)',
    'pic': 'Tiene foto de perfil (1 = si, 0 = no)',
    'lin': 'Tiene enlace externo en la biografia (1 = si, 0 = no)',
    'cl': 'Longitud promedio del texto de las publicaciones',
    'cz': 'Proporcion de publicaciones sin texto (0 a 1)',
    'ni': 'Proporcion de publicaciones que no son imagen (0 a 1)',
    'erl': 'Tasa de engagement por likes',
    'erc': 'Tasa de engagement por comentarios',
    'lt': 'Proporcion de publicaciones con ubicacion (0 a 1)',
    'hc': 'Promedio de hashtags por publicacion',
    'pr': 'Promedio de cuentas etiquetadas por publicacion',
    'fo': 'Promedio de menciones por publicacion',
    'cs': 'Similitud promedio entre los textos de las publicaciones (0 a 1)',
    'pi': 'Intervalo promedio entre publicaciones (horas)',
}

VARS_ENTERAS = ['pos', 'flw', 'flg', 'bl', 'pic', 'lin']
VARS_PROPORCION = ['pic', 'lin', 'cz', 'ni', 'lt', 'cs']

REFERENCIA = pd.DataFrame({
    'mediana_autenticas': X_train[y_train == 0].median(),
    'mediana_falsas': X_train[y_train == 1].median(),
}).round(3)

MODELOS = {}
for clave, archivo, nombre in [
    ('gradient_boosting', 'modelo_gradient_boosting.joblib', 'Gradient Boosting'),
    ('random_forest', 'modelo_random_forest.joblib', 'Random Forest'),
    ('arbol_decision', 'modelo_arbol_decision.joblib', 'Arbol de Decision'),
    ('regresion_logistica', 'modelo_regresion_logistica.joblib', 'Regresion Logistica'),
]:
    ruta = os.path.join(RUTA_RES, archivo)
    if os.path.exists(ruta):
        paquete = joblib.load(ruta)
        MODELOS[clave] = {'nombre': nombre, 'modelo': paquete['modelo'],
                          'umbral': float(paquete['umbral']),
                          'escalado': bool(paquete['usa_escalado']), 'tipo': 'sklearn'}
    else:
        print(f'AVISO: no se encontro {archivo}')

_ruta_mlp = os.path.join(RUTA_RES, 'modelo_mlp.keras')
_ruta_meta = os.path.join(RUTA_RES, 'modelo_mlp_meta.joblib')
if os.path.exists(_ruta_mlp) and os.path.exists(_ruta_meta):
    try:
        os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
        from tensorflow import keras
        _meta = joblib.load(_ruta_meta)
        MODELOS['red_neuronal_mlp'] = {'nombre': 'Red Neuronal MLP',
                                       'modelo': keras.models.load_model(_ruta_mlp),
                                       'umbral': float(_meta['umbral']),
                                       'escalado': bool(_meta['usa_escalado']), 'tipo': 'keras'}
    except Exception as exc:
        print(f'AVISO: la red neuronal no pudo cargarse ({type(exc).__name__}).')

if not MODELOS:
    sys.exit('No se cargo ningun modelo. Ejecute antes los notebooks 01, 02 y 03.')

PRINCIPAL = 'gradient_boosting' if 'gradient_boosting' in MODELOS else list(MODELOS)[0]
UMBRAL = MODELOS[PRINCIPAL]['umbral']
print(f'Modelos cargados: {len(MODELOS)} | Principal: {MODELOS[PRINCIPAL]["nombre"]} '
      f'(umbral {UMBRAL:.4f})')

try:
    import shap
    EXPLICADOR = shap.TreeExplainer(MODELOS[PRINCIPAL]['modelo'])
except Exception as exc:
    EXPLICADOR = None
    print(f'AVISO: SHAP no disponible ({type(exc).__name__}); '
          'se usara la importancia global del modelo.')


# ----------------------------------------------------------------------------
# 3. Logica: preprocesamiento, validacion (UC1), clasificacion (UC2), explicacion (UC3)
# ----------------------------------------------------------------------------

def preprocesar(valores):
    fila = pd.DataFrame([[float(valores[v]) for v in VARIABLES]], columns=VARIABLES)
    fila_log = fila.copy()
    fila_log[VARS_LOG] = np.log1p(fila_log[VARS_LOG])
    fila_esc = pd.DataFrame(ESCALADOR.transform(fila_log), columns=VARIABLES)
    return fila, fila_esc


def validar(valores):
    """UC1: tipo y rango de los 17 atributos."""
    errores, advertencias = [], []
    for v in VARIABLES:
        bruto = valores.get(v)
        if bruto is None or bruto == '':
            errores.append(f'{v} ({DICCIONARIO[v]}): falta el valor.')
            continue
        try:
            valor = float(bruto)
        except (TypeError, ValueError):
            errores.append(f'{v}: "{bruto}" no es un numero.')
            continue
        if not np.isfinite(valor):
            errores.append(f'{v}: el valor no es finito.')
            continue
        if valor < 0:
            errores.append(f'{v}: no puede ser negativo (recibido {valor:g}).')
        if v in VARS_PROPORCION and valor > 1:
            errores.append(f'{v}: debe estar entre 0 y 1 (recibido {valor:g}).')
        elif v in VARS_ENTERAS and valor != int(valor):
            advertencias.append(f'{v}: se esperaba un entero, se recibio {valor:g}.')

    if not errores:
        if float(valores['pos']) == 0 and float(valores['erl']) > 0:
            advertencias.append('La cuenta no tiene publicaciones pero reporta engagement por likes.')
        if float(valores['flg']) / (float(valores['flw']) + 1) > 50:
            advertencias.append('Relacion seguidos/seguidores muy alta: verifique que los valores '
                                'no esten invertidos.')
        for v in VARIABLES:
            maximo = float(X_train[v].max())
            if float(valores[v]) > maximo:
                advertencias.append(f'{v} supera el maximo visto en entrenamiento ({maximo:,.2f}); '
                                    'la prediccion es una extrapolacion.')
    return errores, advertencias


def probabilidad(clave, fila, fila_esc):
    info = MODELOS[clave]
    entrada = fila_esc if info['escalado'] else fila
    if info['tipo'] == 'keras':
        return float(info['modelo'].predict(entrada.values, verbose=0).ravel()[0])
    return float(info['modelo'].predict_proba(entrada)[0, 1])


def nivel_confianza(margen):
    if margen < 0.10:
        return 'BAJA'
    if margen < 0.25:
        return 'MEDIA'
    return 'ALTA'


def aportes_shap(fila):
    if EXPLICADOR is None:
        importancias = getattr(MODELOS[PRINCIPAL]['modelo'], 'feature_importances_', None)
        return np.zeros(len(VARIABLES)) if importancias is None else np.asarray(importancias)
    valores = np.array(EXPLICADOR.shap_values(fila, check_additivity=False))
    if valores.ndim == 3:
        valores = valores[:, :, 1]
    return valores[0]


# ----------------------------------------------------------------------------
# 4. Presentacion
# ----------------------------------------------------------------------------

TARJETA = """
<div style="border-radius:12px;padding:18px 22px;background:{fondo};
            border-left:10px solid {borde};font-family:system-ui,sans-serif">
  <div style="font-size:13px;letter-spacing:1.5px;color:#555">RESULTADO DEL ANALISIS</div>
  <div style="font-size:30px;font-weight:700;color:{borde};margin:6px 0">{etiqueta}</div>
  <div style="font-size:15px;color:#333">
     Probabilidad de que la cuenta sea falsa: <b>{prob:.1%}</b><br>
     Umbral de decision del modelo: {umbral:.3f}<br>
     Nivel de confianza: <b>{confianza}</b><br>
     Consenso: <b>{consenso} de {total}</b> modelos coinciden
  </div>
  {aviso}
</div>
"""

AVISO_DUDA = """
  <div style="margin-top:12px;padding:10px 14px;background:#FFF4CE;border-radius:8px;
              font-size:14px;color:#5B4A00">
     Las senales de esta cuenta no son concluyentes. Se recomienda revision manual
     antes de tomar una decision comercial.
  </div>
"""

TARJETA_ERROR = """
<div style="border-radius:12px;padding:18px 22px;background:#FDECEA;border-left:10px solid #C0392B;
            font-family:system-ui,sans-serif">
  <div style="font-size:22px;font-weight:700;color:#C0392B">Datos invalidos</div>
  <div style="font-size:14px;color:#333;margin-top:8px">
     Corrija los siguientes puntos antes de continuar:
     <ul>{lista}</ul>
  </div>
</div>
"""


def figura_aportes(tabla):
    d = tabla.sort_values('aporte')
    fig, ax = plt.subplots(figsize=(7.5, 0.42 * len(d) + 1.4))
    colores = ['#C0392B' if v > 0 else '#27AE60' for v in d['aporte']]
    etiquetas = [f"{r.variable} = {r.valor:,.2f}" for r in d.itertuples()]
    ax.barh(etiquetas, d['aporte'], color=colores)
    ax.axvline(0, color='#333', lw=1)
    ax.set_xlabel('Aporte a la decision   (rojo: hacia FALSA · verde: hacia AUTENTICA)')
    ax.set_title('Variables que mas influyeron', fontsize=11)
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout()
    return fig


def analizar(*entradas):
    """Funcion principal de la interfaz: UC1 + UC2 + UC3."""
    valores = dict(zip(VARIABLES, entradas))

    errores, advertencias = validar(valores)
    if errores:
        lista = ''.join(f'<li>{e}</li>' for e in errores)
        vacio = pd.DataFrame(columns=['modelo', 'probabilidad', 'clasifica_como'])
        return TARJETA_ERROR.format(lista=lista), vacio, None, pd.DataFrame(), ''

    fila, fila_esc = preprocesar(valores)

    votos = []
    for clave, info in MODELOS.items():
        p = probabilidad(clave, fila, fila_esc)
        votos.append({'modelo': info['nombre'], 'probabilidad': round(p, 4),
                      'umbral': round(info['umbral'], 4),
                      'clasifica_como': 'FALSA' if p >= info['umbral'] else 'AUTENTICA'})
    tabla_votos = pd.DataFrame(votos).sort_values('probabilidad', ascending=False)

    p_principal = next(v['probabilidad'] for v in votos
                       if v['modelo'] == MODELOS[PRINCIPAL]['nombre'])
    etiqueta = 'CUENTA FALSA' if p_principal >= UMBRAL else 'CUENTA AUTENTICA'
    margen = abs(p_principal - UMBRAL)
    confianza = nivel_confianza(margen)
    coinciden = sum(1 for v in votos
                    if v['clasifica_como'] == ('FALSA' if p_principal >= UMBRAL else 'AUTENTICA'))

    tarjeta = TARJETA.format(
        fondo='#FDECEA' if p_principal >= UMBRAL else '#EAF7EF',
        borde='#C0392B' if p_principal >= UMBRAL else '#27AE60',
        etiqueta=etiqueta, prob=p_principal, umbral=UMBRAL,
        confianza=confianza, consenso=coinciden, total=len(votos),
        aviso=AVISO_DUDA if confianza == 'BAJA' else '',
    )

    aportes = aportes_shap(fila)
    tabla_exp = pd.DataFrame({
        'variable': VARIABLES,
        'descripcion': [DICCIONARIO[v] for v in VARIABLES],
        'valor': fila.values[0],
        'mediana_autenticas': REFERENCIA['mediana_autenticas'].values,
        'mediana_falsas': REFERENCIA['mediana_falsas'].values,
        'aporte': np.round(aportes, 4),
    })
    tabla_exp['empuja_hacia'] = np.where(tabla_exp['aporte'] > 0, 'FALSA', 'AUTENTICA')
    tabla_exp = tabla_exp.reindex(tabla_exp['aporte'].abs().sort_values(ascending=False).index)
    top = tabla_exp.head(8).reset_index(drop=True)

    figura = figura_aportes(top[['variable', 'valor', 'aporte']])

    texto_avisos = ''
    if advertencias:
        texto_avisos = '**Advertencias sobre los datos ingresados**\n\n' + \
                       '\n'.join(f'- {a}' for a in advertencias)

    return tarjeta, tabla_votos, figura, top.round(4), texto_avisos


# --- Cuentas de ejemplo tomadas del conjunto de prueba -----------------------

def _probabilidades_muestra(n=400):
    fila = X_test.head(n).reset_index(drop=True)
    fila_esc = X_test_esc.head(n).reset_index(drop=True)
    info = MODELOS[PRINCIPAL]
    entrada = fila_esc if info['escalado'] else fila
    if info['tipo'] == 'keras':
        return info['modelo'].predict(entrada.values, verbose=0).ravel()
    return info['modelo'].predict_proba(entrada)[:, 1]


_PROBS = _probabilidades_muestra()
EJEMPLOS = {
    'falsa': int(np.argmax(_PROBS)),
    'autentica': int(np.argmin(_PROBS)),
    'dudosa': int(np.argmin(np.abs(_PROBS - UMBRAL))),
}


def cargar_ejemplo(tipo):
    i = EJEMPLOS[tipo]
    fila = X_test.iloc[i]
    real = 'FALSA' if y_test[i] == 1 else 'AUTENTICA'
    nota = (f'Cuenta #{i} del conjunto de prueba cargada en el formulario. '
            f'Etiqueta real registrada en el dataset: **{real}**. '
            'Presione "Analizar cuenta" para ver la respuesta del sistema.')
    return [float(fila[v]) for v in VARIABLES] + [nota]


def limpiar():
    return [0.0 for _ in VARIABLES] + ['Formulario limpio.']


# --- Analisis por lotes ------------------------------------------------------

def analizar_archivo(archivo):
    if archivo is None:
        return pd.DataFrame(), None, 'Seleccione un archivo CSV.'
    try:
        df = pd.read_csv(archivo.name if hasattr(archivo, 'name') else archivo)
    except Exception as exc:
        return pd.DataFrame(), None, f'No se pudo leer el archivo: {exc}'

    faltan = [v for v in VARIABLES if v not in df.columns]
    if faltan:
        return pd.DataFrame(), None, f'Faltan columnas en el archivo: {", ".join(faltan)}'

    fila = df[VARIABLES].astype(float).reset_index(drop=True)
    fila_log = fila.copy()
    fila_log[VARS_LOG] = np.log1p(fila_log[VARS_LOG])
    fila_esc = pd.DataFrame(ESCALADOR.transform(fila_log), columns=VARIABLES)

    salida = fila.copy()
    for clave, info in MODELOS.items():
        entrada = fila_esc if info['escalado'] else fila
        if info['tipo'] == 'keras':
            p = info['modelo'].predict(entrada.values, verbose=0).ravel()
        else:
            p = info['modelo'].predict_proba(entrada)[:, 1]
        salida[f'prob_{clave}'] = np.round(p, 4)
        salida[f'clase_{clave}'] = np.where(p >= info['umbral'], 'FALSA', 'AUTENTICA')

    columnas_clase = [f'clase_{k}' for k in MODELOS]
    salida['votos_falsa'] = (salida[columnas_clase] == 'FALSA').sum(axis=1)
    salida['veredicto'] = salida[f'clase_{PRINCIPAL}']
    if 'class' in df.columns:
        salida['etiqueta_real'] = np.where(df['class'].astype(str).str.lower().str[0] == 'f',
                                           'FALSA', 'AUTENTICA')
        aciertos = (salida['veredicto'] == salida['etiqueta_real']).mean()
        resumen = (f'{len(salida)} cuentas analizadas. '
                   f'{int((salida.veredicto == "FALSA").sum())} clasificadas como falsas. '
                   f'Coincidencia con la etiqueta real del archivo: {aciertos:.1%}.')
    else:
        resumen = (f'{len(salida)} cuentas analizadas. '
                   f'{int((salida.veredicto == "FALSA").sum())} clasificadas como falsas.')

    destino = os.path.join(RUTA_RES, 'resultado_lote.csv')
    salida.to_csv(destino, index=False)

    columnas_vista = ['veredicto', 'votos_falsa', f'prob_{PRINCIPAL}'] + \
                     (['etiqueta_real'] if 'etiqueta_real' in salida.columns else [])
    return salida[columnas_vista].head(100), destino, resumen


# ----------------------------------------------------------------------------
# 5. Construccion de la interfaz
# ----------------------------------------------------------------------------

ACERCA = f"""
### Sistema de clasificacion de cuentas de Instagram

Clasifica una cuenta como **autentica** o **falsa** a partir de 17 atributos publicos de perfil,
comportamiento y engagement, usando modelos de aprendizaje automatico supervisado entrenados
desde cero sobre el conjunto de Purba, Asirvatham y Murugesan (IJECE, 2020).

**Modelo principal:** {MODELOS[PRINCIPAL]['nombre']} (umbral de decision {UMBRAL:.4f}).
Se eligio porque empata estadisticamente con el mejor F1 segun la prueba de McNemar, produce menos
falsos negativos —el error mas costoso para el objetivo del proyecto— y permite explicar cada
decision individual con SHAP de forma inmediata.

**Modelos consultados:** {', '.join(m['nombre'] for m in MODELOS.values())}.

**Como leer el resultado**

- La probabilidad se compara contra el umbral del modelo, ajustado para maximizar el F1 sobre la
  clase falsa; no es el 0.5 por defecto.
- El nivel de confianza mide la distancia entre la probabilidad y ese umbral. Confianza *baja*
  significa que la cuenta cae en una zona ambigua y conviene revisarla manualmente.
- El grafico de aportes indica cuanto empujo cada atributo hacia cada clase **para esa cuenta**,
  no en promedio.

**Limitacion declarada:** el conjunto de entrenamiento es de 2020. Una cuenta con valores muy por
encima de los maximos observados entonces cae fuera del rango aprendido; en ese caso la interfaz
emite una advertencia porque la prediccion es una extrapolacion.

Grupo N.4 — CCPG1044 Inteligencia Artificial — ESPOL
"""

with gr.Blocks(title='Clasificador de cuentas de Instagram',
               theme=gr.themes.Soft(primary_hue='indigo')) as demo:

    gr.Markdown(
        '# Clasificador de cuentas de Instagram\n'
        'Determina si una cuenta es **autentica** o **falsa** a partir de sus atributos publicos, '
        'y muestra las variables que sustentan cada decision.'
    )

    with gr.Tab('Analizar una cuenta'):
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown('### Atributos de la cuenta')
                campos = []
                for inicio in range(0, len(VARIABLES), 3):
                    with gr.Row():
                        for v in VARIABLES[inicio:inicio + 3]:
                            campos.append(gr.Number(
                                value=float(X_train[v].median()),
                                label=f'{v} — {DICCIONARIO[v]}',
                                precision=None,
                            ))
                with gr.Row():
                    boton_analizar = gr.Button('Analizar cuenta', variant='primary', scale=2)
                    boton_limpiar = gr.Button('Limpiar', scale=1)
                gr.Markdown('**Cargar una cuenta real del conjunto de prueba:**')
                with gr.Row():
                    boton_falsa = gr.Button('Ejemplo de cuenta falsa')
                    boton_autentica = gr.Button('Ejemplo de cuenta autentica')
                    boton_dudosa = gr.Button('Ejemplo ambiguo')
                nota_ejemplo = gr.Markdown('')

            with gr.Column(scale=2):
                salida_tarjeta = gr.HTML()
                salida_avisos = gr.Markdown('')
                gr.Markdown('### Veredicto de cada modelo')
                salida_votos = gr.Dataframe(interactive=False, wrap=True)

        gr.Markdown('### Explicacion de la decision')
        with gr.Row():
            salida_figura = gr.Plot(label='Aporte de cada variable')
            salida_tabla = gr.Dataframe(label='Detalle de las variables mas influyentes',
                                        interactive=False, wrap=True)

        salidas = [salida_tarjeta, salida_votos, salida_figura, salida_tabla, salida_avisos]
        boton_analizar.click(analizar, inputs=campos, outputs=salidas)
        boton_limpiar.click(limpiar, inputs=None, outputs=campos + [nota_ejemplo])
        boton_falsa.click(lambda: cargar_ejemplo('falsa'), None, campos + [nota_ejemplo])
        boton_autentica.click(lambda: cargar_ejemplo('autentica'), None, campos + [nota_ejemplo])
        boton_dudosa.click(lambda: cargar_ejemplo('dudosa'), None, campos + [nota_ejemplo])

    with gr.Tab('Analizar un archivo'):
        gr.Markdown(
            'Cargue un archivo CSV con las 17 columnas de atributos '
            f'(`{", ".join(VARIABLES)}`). Si incluye la columna `class`, la interfaz reporta '
            'ademas el porcentaje de coincidencia con la etiqueta real.'
        )
        entrada_archivo = gr.File(label='Archivo CSV', file_types=['.csv'])
        boton_lote = gr.Button('Analizar archivo', variant='primary')
        resumen_lote = gr.Markdown('')
        tabla_lote = gr.Dataframe(label='Resultados (primeras 100 filas)', interactive=False)
        descarga_lote = gr.File(label='Descargar resultados completos')
        boton_lote.click(analizar_archivo, inputs=entrada_archivo,
                         outputs=[tabla_lote, descarga_lote, resumen_lote])

    with gr.Tab('Acerca del sistema'):
        gr.Markdown(ACERCA)


if __name__ == '__main__':
    demo.launch(share=ARGS.publica, server_port=ARGS.puerto, inbrowser=not ARGS.publica)
