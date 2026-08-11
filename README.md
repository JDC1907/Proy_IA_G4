# Clasificación de cuentas auténticas y falsas en Instagram
**CCPG1044 Inteligencia Artificial — Grupo N.° 4 — ESPOL**

Sistema de clasificación binaria de cuentas de Instagram a partir de 17 atributos públicos de perfil,
comportamiento y engagement, con cinco modelos de aprendizaje automático supervisado entrenados desde
cero e interfaz gráfica de consulta.

---

## Contenido del paquete

| Archivo | Descripción |
|---|---|
| `00_base_compartida.ipynb` | Carga, análisis exploratorio, limpieza, partición 80/20 y escalado. Genera `split/` |
| `01_regresion_logistica_arbol.ipynb` | Regresión Logística y Árbol de Decisión |
| `02_random_forest_gradient_boosting.ipynb` | Random Forest y Gradient Boosting |
| `03_red_neuronal_mlp.ipynb` | Red neuronal multicapa entrenada desde cero |
| `04_comparacion_final.ipynb` | Comparación de los cinco modelos, pruebas de McNemar e interpretabilidad |
| `05_interfaz.ipynb` | Documentación y validación de los casos de uso UC1, UC2 y UC3 |
| **`app_interfaz.py`** | **Interfaz gráfica del sistema (se ejecuta en el navegador)** |
| `ejemplos_prueba.csv` | 20 cuentas reales del conjunto de prueba (10 falsas, 10 auténticas) con su etiqueta |
| `requirements.txt` | Librerías necesarias |
| `user_fake_authentic_2class.csv` | Conjunto de datos (Purba, Asirvatham y Murugesan, 2020) |

---

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

### 1. Entrenamiento (una sola vez, en orden)

```
00_base_compartida.ipynb   ->  genera split/particion.npz
01_regresion_logistica_arbol.ipynb
02_random_forest_gradient_boosting.ipynb
03_red_neuronal_mlp.ipynb  ->  generan resultados/*.joblib, *.keras, *.npz, *.json
04_comparacion_final.ipynb ->  comparación de los cinco modelos
```

Los cuatro notebooks de modelado deben ejecutarse **después** del 00 y sobre la misma partición.
El notebook 04 verifica automáticamente esa condición y se detiene si no se cumple.

En cada notebook, ajustar la variable `CARPETA` de la primera celda a la ruta local del proyecto.
En Google Colab la ruta se detecta sola.

### 2. Interfaz gráfica

```bash
python app_interfaz.py
```

Abre automáticamente `http://127.0.0.1:7860` en el navegador. Si la carpeta del proyecto no se
detecta sola:

```bash
python app_interfaz.py --carpeta "C:/ruta/del/proyecto"
```

En Google Colab, para obtener un enlace público temporal:

```bash
!python app_interfaz.py --publica
```

---

## Qué hace la interfaz

**Pestaña "Analizar una cuenta"** — Formulario con los 17 atributos. Devuelve el veredicto, la
probabilidad, el nivel de confianza, el veredicto de los cinco modelos y el gráfico de aportes
de cada variable a esa decisión concreta. Tres botones cargan cuentas reales del conjunto de prueba
(una falsa clara, una auténtica clara y una ambigua) para probar el sistema de inmediato.

**Pestaña "Analizar un archivo"** — Procesa un CSV con muchas cuentas y devuelve las predicciones de
los cinco modelos, descargables. Si el archivo incluye la columna `class`, reporta además el
porcentaje de coincidencia con la etiqueta real. Puede probarse directamente con `ejemplos_prueba.csv`.

**Pestaña "Acerca del sistema"** — Modelo principal, criterio de selección y limitaciones declaradas.

---

## Casos de uso implementados

| Caso de uso | Implementación |
|---|---|
| **UC1** — Cargar datos de la cuenta | Formulario con validación de tipo y rango; el flujo alterno muestra los errores y solicita corrección antes de clasificar |
| **UC2** — Clasificar la cuenta | Clasificación con los cinco modelos; el flujo alterno reporta confianza baja cuando la probabilidad queda cerca del umbral |
| **UC3** — Visualizar resultado y variables influyentes | Gráfico de aportes SHAP por variable y tabla de detalle ampliado |

---

## Modelo principal

**Gradient Boosting**, con umbral de decisión ajustado para maximizar F1 sobre la clase falsa.

Empata estadísticamente en F1 con Random Forest (prueba de McNemar, p = 0.451), produce menos falsos
negativos —el error más costoso según el objetivo del proyecto— y permite explicar cada decisión
individual con SHAP de forma inmediata. La interfaz consulta igualmente los cinco modelos y muestra
el veredicto de cada uno.

---

## Limitación declarada

Los modelos se entrenaron con datos recolectados en 2020. Una cuenta con valores muy por encima de
los máximos observados entonces queda fuera del rango aprendido; en ese caso la interfaz emite una
advertencia explícita, porque la predicción es una extrapolación.

---

## Referencia del conjunto de datos

K. R. Purba, D. Asirvatham y R. K. Murugesan, "Classification of Instagram fake users using
supervised machine learning algorithms", *International Journal of Electrical and Computer
Engineering (IJECE)*, vol. 10, n.º 3, pp. 2763–2772, jun. 2020.
