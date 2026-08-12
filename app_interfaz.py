"""
Interfaz grafica — Clasificacion de cuentas de Instagram (autenticas / falsas)
CCPG1044 Inteligencia Artificial — Grupo N.4 — ESPOL

Aplicacion web propia (Flask + HTML/CSS/JS), sin depender del theming de terceros:
el backend reutiliza exactamente la misma logica de preprocesamiento, validacion,
clasificacion (UC1/UC2) y explicacion SHAP (UC3) que el resto del proyecto.

Ejecucion local:
    python app_interfaz.py
    (abre http://127.0.0.1:7860 — ábrelo manualmente en el navegador)

Ejecucion visible en la red local (para que otros equipos de la feria se conecten):
    python app_interfaz.py --publica
    (queda disponible en http://<tu-ip-local>:7860)

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

from flask import Flask, jsonify, render_template, request, send_file


# ============================================================================
# 1. Localizacion de la carpeta del proyecto
# ============================================================================

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
parser.add_argument('--publica', action='store_true',
                    help='Escucha en 0.0.0.0 para que otros equipos de la red local se conecten')
parser.add_argument('--puerto', type=int, default=7860)
ARGS, _ = parser.parse_known_args()

CARPETA = localizar_carpeta(ARGS.carpeta)
RUTA_SPLIT = os.path.join(CARPETA, 'split')
RUTA_RES = os.path.join(CARPETA, 'resultados')
print(f'Carpeta del proyecto: {CARPETA}')


# ============================================================================
# 2. Carga de datos, escalador y modelos entrenados
# ============================================================================

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
    'pic': 'Tiene foto de perfil',
    'lin': 'Tiene enlace externo en la biografia',
    'cl': 'Longitud promedio del texto de las publicaciones',
    'cz': 'Proporcion de publicaciones sin texto',
    'ni': 'Proporcion de publicaciones que no son imagen',
    'erl': 'Tasa de engagement por likes',
    'erc': 'Tasa de engagement por comentarios',
    'lt': 'Proporcion de publicaciones con ubicacion',
    'hc': 'Promedio de hashtags por publicacion',
    'pr': 'Promedio de cuentas etiquetadas por publicacion',
    'fo': 'Promedio de menciones por publicacion',
    'cs': 'Similitud promedio entre los textos de las publicaciones',
    'pi': 'Intervalo promedio entre publicaciones (horas)',
}

# Los 17 atributos agrupados por naturaleza (icono, titulo, subtitulo, claves)
GRUPOS = [
    ('👥', 'Audiencia', 'Tamano y equilibrio de la comunidad', ['flw', 'flg']),
    ('🪪', 'Perfil', 'Elementos declarativos de la cuenta', ['pic', 'lin', 'bl']),
    ('📊', 'Actividad', 'Volumen y ritmo de publicacion', ['pos', 'pi']),
    ('⚡', 'Engagement', 'Respuesta real de la audiencia', ['erl', 'erc']),
    ('📝', 'Contenido', 'Como son las publicaciones', ['cl', 'cz', 'ni', 'hc']),
    ('🔗', 'Interaccion', 'Referencias a terceros y consistencia', ['pr', 'fo', 'lt', 'cs']),
]

VAR_ICONOS = {
    'pos': '📝', 'flw': '👥', 'flg': '➕', 'bl': '📄', 'pic': '🖼️', 'lin': '🔗',
    'cl': '✏️', 'cz': '🚫', 'ni': '🎞️', 'erl': '❤️', 'erc': '💬', 'lt': '📍',
    'hc': '#️⃣', 'pr': '🏷️', 'fo': '📣', 'cs': '🔁', 'pi': '⏱️',
}

VARS_ENTERAS = ['pos', 'flw', 'flg', 'bl', 'pic', 'lin']
VARS_BINARIAS = ['pic', 'lin']
VARS_PROPORCION = ['pic', 'lin', 'cz', 'ni', 'lt', 'cs']

MEDIANA_AUT = X_train[y_train == 0].median()
MEDIANA_FAL = X_train[y_train == 1].median()
ORDENADOS_AUT = {v: np.sort(X_train.loc[y_train == 0, v].values) for v in VARIABLES}
ORDENADOS_FAL = {v: np.sort(X_train.loc[y_train == 1, v].values) for v in VARIABLES}

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

MODEL_ICONOS = {
    'Regresion Logistica': 'Σ',
    'Arbol de Decision': '🌳',
    'Random Forest': '🌲',
    'Gradient Boosting': '📈',
    'Red Neuronal MLP': '🧠',
}

try:
    import shap
    EXPLICADOR = shap.TreeExplainer(MODELOS[PRINCIPAL]['modelo'])
except Exception as exc:
    EXPLICADOR = None
    print(f'AVISO: SHAP no disponible ({type(exc).__name__}); '
          'se usara la importancia global del modelo.')


# ============================================================================
# 3. Logica: preprocesamiento, validacion (UC1), clasificacion (UC2), explicacion (UC3)
# ============================================================================

def preprocesar(valores):
    fila = pd.DataFrame([[float(valores[v]) for v in VARIABLES]], columns=VARIABLES)
    fila_log = fila.copy()
    fila_log[VARS_LOG] = np.log1p(fila_log[VARS_LOG])
    fila_esc = pd.DataFrame(ESCALADOR.transform(fila_log), columns=VARIABLES)
    return fila, fila_esc


def validar(valores):
    """UC1: verifica tipo y rango de los 17 atributos."""
    errores, advertencias = [], []
    for v in VARIABLES:
        bruto = valores.get(v)
        if bruto is None or bruto == '':
            errores.append(f'<b>{v}</b> ({DICCIONARIO[v]}): falta el valor.')
            continue
        try:
            valor = float(bruto)
        except (TypeError, ValueError):
            errores.append(f'<b>{v}</b>: "{bruto}" no es un numero.')
            continue
        if not np.isfinite(valor):
            errores.append(f'<b>{v}</b>: el valor no es finito.')
            continue
        if valor < 0:
            errores.append(f'<b>{v}</b>: no puede ser negativo (recibido {valor:g}).')
        if v in VARS_PROPORCION and valor > 1:
            errores.append(f'<b>{v}</b>: debe estar entre 0 y 1 (recibido {valor:g}).')
        elif v in VARS_ENTERAS and valor != int(valor):
            advertencias.append(f'<b>{v}</b>: se esperaba un entero, se recibio {valor:g}.')

    if not errores:
        if float(valores['pos']) == 0 and float(valores['erl']) > 0:
            advertencias.append('La cuenta no tiene publicaciones pero reporta engagement por likes.')
        if float(valores['flg']) / (float(valores['flw']) + 1) > 50:
            advertencias.append('Relacion seguidos/seguidores muy alta: verifique que los valores '
                                'no esten invertidos.')
        for v in VARIABLES:
            maximo = float(X_train[v].max())
            if float(valores[v]) > maximo:
                advertencias.append(
                    f'<b>{v}</b> supera el maximo visto en entrenamiento ({maximo:,.0f}); '
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
        imp = getattr(MODELOS[PRINCIPAL]['modelo'], 'feature_importances_', None)
        return np.zeros(len(VARIABLES)) if imp is None else np.asarray(imp)
    valores = np.array(EXPLICADOR.shap_values(fila, check_additivity=False))
    if valores.ndim == 3:
        valores = valores[:, :, 1]
    return valores[0]


def percentil(valor, ordenados):
    """Fraccion (0 a 1) de una poblacion ordenada que queda por debajo de 'valor'."""
    return float(np.searchsorted(ordenados, valor) / max(len(ordenados), 1))


def descriptor_percentil(frac):
    pct = frac * 100
    if pct >= 90:
        return 'Muy por encima del promedio'
    if pct >= 60:
        return 'Por encima del promedio'
    if pct > 40:
        return 'Dentro del promedio'
    if pct > 10:
        return 'Por debajo del promedio'
    return 'Muy por debajo del promedio'


def _fmt(v):
    v = float(v)
    return f'{v:,.0f}' if (abs(v) >= 100 or v.is_integer()) else f'{v:,.2f}'


def formatear(variable, valor):
    if variable in VARS_BINARIAS:
        return 'Si' if float(valor) >= 0.5 else 'No'
    return _fmt(valor)


# ============================================================================
# 4. Presentacion (fragmentos HTML que consume el frontend)
# ============================================================================

ESTADO_VACIO = '''
<div class="empty-state">
  <div class="empty-icon">🔍</div>
  <div>Completa los datos de la cuenta y presiona <b>Analizar cuenta</b>,
  o prueba un ejemplo rápido arriba.</div>
</div>
'''

RESUMEN_LOTE_VACIO = '<div class="empty-state small">Aún no se ha analizado ningún archivo por lotes.</div>'


def render_error(errores):
    lista = ''.join(f'<li>{e}</li>' for e in errores)
    return f'''
    <div class="card verdict-card border-danger">
      <div class="verdict-icon">⚠️</div>
      <div class="verdict-eyebrow">DATOS INVÁLIDOS</div>
      <div class="verdict-label text-danger">Corrige los siguientes puntos</div>
      <ul class="error-list">{lista}</ul>
    </div>
    '''


def render_veredicto(etiqueta, prob_mostrada, umbral_mostrado, confianza, coinciden, total, advertencias):
    es_autentica = etiqueta == 'AUTENTICA'
    clase = 'success' if es_autentica else 'danger'
    icono = '🛡️' if es_autentica else '🚩'
    etiqueta_txt = 'auténtica' if es_autentica else 'falsa'

    if confianza == 'ALTA' and coinciden == total:
        evidencia = f'Los modelos coinciden en que esta cuenta es {etiqueta_txt}.'
    elif coinciden == total:
        evidencia = f'Los {total} modelos coinciden, aunque la señal es de confianza {confianza.lower()}.'
    else:
        evidencia = f'{coinciden} de {total} modelos coinciden en este veredicto.'

    aviso_baja = ''
    if confianza == 'BAJA':
        aviso_baja = ('<div class="soft-warning">Las señales de esta cuenta no son concluyentes. '
                      'Se recomienda revisión manual antes de tomar una decisión comercial.</div>')

    aviso_datos = ''
    if advertencias:
        items = ''.join(f'<li>{a}</li>' for a in advertencias)
        aviso_datos = f'<div class="soft-warning"><b>Advertencias sobre los datos</b><ul>{items}</ul></div>'

    margen = abs(prob_mostrada - umbral_mostrado)
    return f'''
    <div class="card verdict-card border-{clase}">
      <div class="verdict-icon">{icono}</div>
      <div class="verdict-eyebrow">VEREDICTO FINAL</div>
      <div class="verdict-label text-{clase}">CUENTA {etiqueta}</div>
      <div class="verdict-evidence bg-{clase}-soft text-{clase}">
        <span class="dot dot-{clase}"></span> Evidencia {confianza.lower()} · {evidencia}
      </div>
      <div class="verdict-stats">
        <div><div class="stat-value">{prob_mostrada:.1%}</div>
             <div class="stat-label">Probabilidad de {etiqueta_txt}</div></div>
        <div><div class="stat-value">{umbral_mostrado:.1%}</div>
             <div class="stat-label">Umbral de decisión ({MODELOS[PRINCIPAL]['nombre']})</div></div>
        <div><div class="stat-value">±{margen:.1%}</div>
             <div class="stat-label">Margen sobre el umbral</div></div>
      </div>
      {aviso_baja}
      {aviso_datos}
    </div>
    '''


def render_gauge(p_autentica, umbral_autentica, confianza, margen):
    pct = max(0.0, min(100.0, p_autentica * 100))
    umbral_pct = max(0.0, min(100.0, umbral_autentica * 100))
    if confianza == 'BAJA':
        zona, zona_clase = 'Zona de incertidumbre', 'warning'
    elif p_autentica >= umbral_autentica:
        zona, zona_clase = 'Hacia AUTÉNTICA', 'success'
    else:
        zona, zona_clase = 'Hacia FALSA', 'danger'

    return f'''
    <div class="card">
      <div class="gauge-title">Puntaje del modelo
        <span class="gauge-hint">(más a la derecha = más auténtica)</span></div>
      <div class="gauge-wrap">
        <div class="gauge-pointer" style="left:{pct:.2f}%">
          <div class="gauge-pointer-value">{pct:.1f}%</div>
          <div class="gauge-pointer-line"></div>
        </div>
        <div class="gauge-track">
          <div class="gauge-threshold" style="left:{umbral_pct:.2f}%"></div>
        </div>
      </div>
      <div class="gauge-scale"><span>0%</span><span>50%</span><span>100%</span></div>
      <div class="gauge-zones">
        <div class="zone zone-danger">Hacia FALSA</div>
        <div class="zone zone-warning">Zona de incertidumbre<br><span>±{margen*100:.1f}%</span></div>
        <div class="zone zone-success">Hacia AUTÉNTICA</div>
      </div>
      <div class="gauge-current bg-{zona_clase}-soft text-{zona_clase}">{zona}</div>
    </div>
    '''


def render_consenso(votos, etiqueta_principal):
    tarjetas = []
    for v in votos:
        clase = 'success' if v['etiqueta'] == 'AUTENTICA' else 'danger'
        marca = '✓' if v['etiqueta'] == 'AUTENTICA' else '✕'
        p_aut = 1 - v['probabilidad']
        icono = MODEL_ICONOS.get(v['nombre'], '🤖')
        tarjetas.append(f'''
        <div class="consensus-card border-{clase}">
          <div class="consensus-icon">{icono}</div>
          <div class="consensus-name">{v['nombre']}</div>
          <div class="consensus-prob">{p_aut:.1%}</div>
          <div class="badge bg-{clase}-soft text-{clase}">{marca} {v['etiqueta']}</div>
        </div>''')
    coinciden = sum(1 for v in votos if v['etiqueta'] == etiqueta_principal)
    return f'''
    <div class="card">
      <div class="section-title">Consenso de modelos ({len(votos)})</div>
      <div class="consensus-grid">{''.join(tarjetas)}</div>
      <div class="consensus-summary">{coinciden} de {len(votos)} modelos clasifican esta cuenta como
        <b>{etiqueta_principal.lower()}</b>.</div>
    </div>
    '''


def render_features(tabla_top):
    max_abs = float(tabla_top['aporte'].abs().max()) if len(tabla_top) else 0.0
    tarjetas = []
    for r in tabla_top.itertuples():
        bajo_impacto = max_abs > 0 and abs(r.aporte) < 0.15 * max_abs
        if bajo_impacto:
            clase, texto_badge = 'warning', 'Impacto bajo'
        elif r.aporte > 0:
            clase, texto_badge = 'danger', 'Aporta a FALSA'
        else:
            clase, texto_badge = 'success', 'Aporta a AUTÉNTICA'
        flecha = '↑' if r.valor >= float(X_train[r.variable].median()) else '↓'
        icono = VAR_ICONOS.get(r.variable, '🔹')
        p_aut = percentil(r.valor, ORDENADOS_AUT[r.variable])
        contexto = (f'Más alto que el {p_aut:.0%} de las cuentas auténticas' if p_aut >= 0.5
                    else f'Más bajo que el {1 - p_aut:.0%} de las cuentas auténticas')
        tarjetas.append(f'''
        <div class="feature-card border-{clase}">
          <div class="feature-head">
            <span class="feature-var">{icono} {r.variable}</span>
            <span class="feature-arrow">{flecha}</span>
          </div>
          <div class="feature-value">{formatear(r.variable, r.valor)}</div>
          <div class="feature-desc">{r.descripcion}. {contexto}.</div>
          <div class="badge small bg-{clase}-soft text-{clase}">{texto_badge}</div>
        </div>''')
    return f'''
    <div class="card">
      <div class="section-title">Qué señales influyeron en la decisión</div>
      <div class="section-caption">Las variables con mayor impacto en el resultado, para esta cuenta</div>
      <div class="feature-grid">{''.join(tarjetas)}</div>
      <div class="legend">
        <span><span class="dot dot-success"></span> Aporta a auténtica</span>
        <span><span class="dot dot-danger"></span> Aporta a falsa</span>
        <span><span class="dot dot-warning"></span> Impacto bajo</span>
      </div>
    </div>
    '''


def render_percentiles(tabla_top):
    filas = []
    for r in tabla_top.itertuples():
        frac = percentil(r.valor, ORDENADOS_AUT[r.variable])
        filas.append(f'''
        <div class="percentile-row">
          <div class="percentile-label">{r.descripcion}</div>
          <div class="percentile-track">
            <div class="percentile-fill" style="width:{frac*100:.1f}%"></div>
            <div class="percentile-marker" style="left:50%"></div>
          </div>
          <div class="percentile-meta">{frac*100:.0f}° · {descriptor_percentil(frac)}</div>
        </div>''')
    return f'''
    <div class="card">
      <div class="section-title">Comparación con cuentas típicas</div>
      <div class="section-caption">Percentil del valor ingresado frente a las cuentas auténticas de entrenamiento</div>
      {''.join(filas)}
    </div>
    '''


def render_tabla_detalle(tabla):
    filas = []
    for r in tabla.itertuples():
        clase = 'danger' if r.aporte > 0 else 'success'
        filas.append(f'''
        <tr>
          <td><b>{r.variable}</b><br><span class="muted">{r.descripcion}</span></td>
          <td class="num">{formatear(r.variable, r.valor)}</td>
          <td class="num muted">{formatear(r.variable, r.tipico_autentica)}</td>
          <td class="num muted">{formatear(r.variable, r.tipico_falsa)}</td>
          <td class="num text-{clase}">{r.aporte:+.4f}</td>
          <td><span class="badge small bg-{clase}-soft text-{clase}">{r.empuja_hacia}</span></td>
        </tr>''')
    return f'''
    <table class="detail-table">
      <thead><tr><th>Variable</th><th>Valor</th><th>Típico autént.</th><th>Típico falsa</th>
      <th>Aporte SHAP</th><th>Empuja hacia</th></tr></thead>
      <tbody>{''.join(filas)}</tbody>
    </table>
    '''


def render_resumen_lote(nombre, total, n_falsas, n_autenticas):
    pct_f = (n_falsas / total * 100) if total else 0.0
    pct_a = (n_autenticas / total * 100) if total else 0.0
    return f'''
    <div class="batch-row"><span>Último análisis</span><b class="truncate">{nombre}</b></div>
    <div class="batch-row"><span>Cuentas analizadas</span><b>{total}</b></div>
    <div class="batch-row"><span>Auténticas</span><b class="text-success">{n_autenticas} ({pct_a:.1f}%)</b></div>
    <div class="batch-row"><span>Falsas</span><b class="text-danger">{n_falsas} ({pct_f:.1f}%)</b></div>
    '''


def render_tabla_lote(salida, columnas):
    encabezados = ''.join(f'<th>{c}</th>' for c in columnas)
    filas = []
    for _, fila in salida[columnas].head(100).iterrows():
        celdas = []
        for c in columnas:
            valor = fila[c]
            if c == 'veredicto' or c == 'etiqueta_real':
                clase = 'danger' if valor == 'FALSA' else 'success'
                celdas.append(f'<td><span class="badge small bg-{clase}-soft text-{clase}">{valor}</span></td>')
            else:
                celdas.append(f'<td class="num">{valor}</td>')
        filas.append(f'<tr>{"".join(celdas)}</tr>')
    return f'''
    <table class="detail-table">
      <thead><tr>{encabezados}</tr></thead>
      <tbody>{''.join(filas)}</tbody>
    </table>
    '''


# ============================================================================
# 5. Funcion principal de clasificacion (UC1 + UC2 + UC3)
# ============================================================================

N_DESTACADAS = 5


def analizar(valores):
    """Devuelve un dict con todos los fragmentos HTML que consume el frontend."""
    errores, advertencias = validar(valores)
    if errores:
        return {'valido': False, 'veredicto_html': render_error(errores),
                'gauge_html': ESTADO_VACIO, 'consenso_html': ESTADO_VACIO,
                'features_html': ESTADO_VACIO, 'percentiles_html': ESTADO_VACIO,
                'tabla_html': ''}

    fila, fila_esc = preprocesar(valores)

    votos = []
    for clave, info in MODELOS.items():
        p = probabilidad(clave, fila, fila_esc)
        votos.append({'clave': clave, 'nombre': info['nombre'], 'probabilidad': p,
                      'umbral': info['umbral'],
                      'etiqueta': 'FALSA' if p >= info['umbral'] else 'AUTENTICA'})

    p_falsa = next(v['probabilidad'] for v in votos if v['clave'] == PRINCIPAL)
    margen = abs(p_falsa - UMBRAL)
    confianza = nivel_confianza(margen)
    etiqueta = 'FALSA' if p_falsa >= UMBRAL else 'AUTENTICA'
    coinciden = sum(1 for v in votos if v['etiqueta'] == etiqueta)

    p_autentica = 1 - p_falsa
    umbral_autentica = 1 - UMBRAL
    prob_mostrada = p_autentica if etiqueta == 'AUTENTICA' else p_falsa
    umbral_mostrado = umbral_autentica if etiqueta == 'AUTENTICA' else UMBRAL

    aportes = aportes_shap(fila)
    tabla = pd.DataFrame({
        'variable': VARIABLES,
        'descripcion': [DICCIONARIO[v] for v in VARIABLES],
        'valor': fila.values[0],
        'tipico_autentica': MEDIANA_AUT.values,
        'tipico_falsa': MEDIANA_FAL.values,
        'aporte': np.round(aportes, 4),
    })
    tabla['empuja_hacia'] = np.where(tabla['aporte'] > 0, 'FALSA', 'AUTENTICA')
    tabla = tabla.reindex(tabla['aporte'].abs().sort_values(ascending=False).index).reset_index(drop=True)
    top = tabla.head(N_DESTACADAS)

    return {
        'valido': True,
        'veredicto_html': render_veredicto(etiqueta, prob_mostrada, umbral_mostrado, confianza,
                                           coinciden, len(votos), advertencias),
        'gauge_html': render_gauge(p_autentica, umbral_autentica, confianza, margen),
        'consenso_html': render_consenso(votos, etiqueta),
        'features_html': render_features(top),
        'percentiles_html': render_percentiles(top),
        'tabla_html': render_tabla_detalle(tabla),
    }


# --- Cuentas de ejemplo del conjunto de prueba ------------------------------

def _probabilidades_muestra(n=400):
    fila = X_test.head(n).reset_index(drop=True)
    fila_esc = X_test_esc.head(n).reset_index(drop=True)
    info = MODELOS[PRINCIPAL]
    entrada = fila_esc if info['escalado'] else fila
    if info['tipo'] == 'keras':
        return info['modelo'].predict(entrada.values, verbose=0).ravel()
    return info['modelo'].predict_proba(entrada)[:, 1]


_PROBS = _probabilidades_muestra()
EJEMPLOS = {'falsa': int(np.argmax(_PROBS)),
            'autentica': int(np.argmin(_PROBS)),
            'dudosa': int(np.argmin(np.abs(_PROBS - UMBRAL)))}


# --- Analisis por lotes -----------------------------------------------------

def analizar_archivo(archivo_storage):
    df = pd.read_csv(archivo_storage)

    faltan = [v for v in VARIABLES if v not in df.columns]
    if faltan:
        raise ValueError(f'Faltan columnas en el archivo: {", ".join(faltan)}')

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

    n_falsas = int((salida['veredicto'] == 'FALSA').sum())
    n_total = len(salida)
    n_autenticas = n_total - n_falsas
    if 'class' in df.columns:
        salida['etiqueta_real'] = np.where(
            df['class'].astype(str).str.lower().str[0] == 'f', 'FALSA', 'AUTENTICA')
        aciertos = (salida['veredicto'] == salida['etiqueta_real']).mean()
        resumen = (f'{n_total} cuentas analizadas · {n_falsas} clasificadas como falsas · '
                   f'coincidencia con la etiqueta real del archivo: {aciertos:.1%}')
    else:
        resumen = f'{n_total} cuentas analizadas · {n_falsas} clasificadas como falsas'

    destino = os.path.join(RUTA_RES, 'resultado_lote.csv')
    salida.to_csv(destino, index=False)

    vista = ['veredicto', 'votos_falsa', f'prob_{PRINCIPAL}'] + \
            (['etiqueta_real'] if 'etiqueta_real' in salida.columns else [])

    return {
        'ok': True,
        'resumen_texto': resumen,
        'resumen_html': render_resumen_lote(os.path.basename(archivo_storage.filename or 'archivo.csv'),
                                            n_total, n_falsas, n_autenticas),
        'tabla_html': render_tabla_lote(salida, vista),
        'descarga_url': '/api/descarga',
    }


# ============================================================================
# 6. Aplicacion Flask
# ============================================================================

app = Flask(__name__)

ACERCA_HTML = f'''
<h3>Sistema de clasificación de cuentas de Instagram</h3>
<p>Clasifica una cuenta como <b>auténtica</b> o <b>falsa</b> a partir de 17 atributos públicos de
perfil, comportamiento y engagement, usando cinco modelos de aprendizaje automático supervisado
entrenados desde cero sobre el conjunto de Purba, Asirvatham y Murugesan (IJECE, 2020):
64&nbsp;244 cuentas tras limpieza, partición estratificada 80/20.</p>
<p><b>Modelo principal: {MODELOS[PRINCIPAL]['nombre']}</b> (umbral de decisión {UMBRAL:.4f}).
Empata estadísticamente en F1 con Random Forest según la prueba de McNemar (p&nbsp;=&nbsp;0.451),
pero produce menos falsos negativos —el error más costoso según el objetivo del proyecto— y permite
explicar cada decisión individual de forma inmediata. La interfaz consulta igualmente los cinco
modelos.</p>
<p><b>Modelos consultados:</b> {', '.join(m['nombre'] for m in MODELOS.values())}.</p>
<h4>Cómo leer el resultado</h4>
<ul>
  <li>La probabilidad mostrada es la de la clase que ganó el veredicto, comparada contra el umbral
      propio de cada modelo (ajustado por curva precisión-recall, no el 0.5 por defecto).</li>
  <li>El nivel de confianza mide la distancia entre la probabilidad y ese umbral. Confianza
      <b>baja</b> significa que la cuenta cae en zona ambigua y conviene revisarla manualmente.</li>
  <li>Las señales indican cuánto empujó cada atributo hacia cada clase <b>para esa cuenta
      concreta</b>, no en promedio, y se contrastan con el perfil típico de cada clase.</li>
</ul>
<h4>Limitación declarada</h4>
<p>El conjunto de entrenamiento es de 2020. Una cuenta con valores muy por encima de los máximos
observados entonces cae fuera del rango aprendido; en ese caso la interfaz emite una advertencia,
porque la predicción es una extrapolación.</p>
<p class="muted">Grupo N.4 — CCPG1044 Inteligencia Artificial — ESPOL</p>
'''


@app.route('/')
def index():
    grupos = [{'icono': i, 'titulo': t, 'subtitulo': s,
              'campos': [{'clave': v, 'descripcion': DICCIONARIO[v],
                         'valor': float(X_train[v].median())} for v in claves]}
             for i, t, s, claves in GRUPOS]
    return render_template('index.html', grupos=grupos, variables=VARIABLES,
                           modelo_principal=MODELOS[PRINCIPAL]['nombre'],
                           modelos_count=len(MODELOS), acerca_html=ACERCA_HTML)


@app.route('/api/analizar', methods=['POST'])
def api_analizar():
    valores = request.get_json(force=True)
    resultado = analizar(valores)
    return jsonify(resultado)


@app.route('/api/ejemplo/<tipo>')
def api_ejemplo(tipo):
    if tipo not in EJEMPLOS:
        return jsonify({'error': 'tipo invalido'}), 400
    i = EJEMPLOS[tipo]
    fila = X_test.iloc[i]
    return jsonify({'valores': {v: float(fila[v]) for v in VARIABLES}})


@app.route('/api/medianas')
def api_medianas():
    return jsonify({'valores': {v: float(X_train[v].median()) for v in VARIABLES}})


@app.route('/api/lote', methods=['POST'])
def api_lote():
    archivo = request.files.get('archivo')
    if archivo is None or archivo.filename == '':
        return jsonify({'ok': False, 'mensaje': 'Selecciona un archivo CSV.'}), 400
    try:
        resultado = analizar_archivo(archivo)
        return jsonify(resultado)
    except Exception as exc:
        return jsonify({'ok': False, 'mensaje': f'No se pudo procesar el archivo: {exc}'}), 400


@app.route('/api/descarga')
def api_descarga():
    destino = os.path.join(RUTA_RES, 'resultado_lote.csv')
    if not os.path.exists(destino):
        return jsonify({'error': 'Aun no hay resultados generados.'}), 404
    return send_file(destino, as_attachment=True, download_name='resultado_lote.csv')


if __name__ == '__main__':
    host = '0.0.0.0' if ARGS.publica else '127.0.0.1'
    print(f'Abriendo en http://{"localhost" if not ARGS.publica else "0.0.0.0"}:{ARGS.puerto}')
    app.run(host=host, port=ARGS.puerto, debug=False)
