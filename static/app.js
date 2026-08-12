// Interfaz — Clasificador de cuentas de Instagram
// Solo maneja UI e IO: toda la logica de clasificacion vive en el backend (Flask).

const form = document.getElementById('form-cuenta');

function irATab(nombre) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === nombre));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === `tab-${nombre}`));
}

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => irATab(btn.dataset.tab));
});

function valoresFormulario() {
  const datos = {};
  new FormData(form).forEach((valor, clave) => { datos[clave] = valor; });
  return datos;
}

function aplicarValores(valores) {
  Object.entries(valores).forEach(([clave, valor]) => {
    const campo = form.querySelector(`[name="${clave}"]`);
    if (campo) campo.value = valor;
  });
}

async function analizarCuenta() {
  const boton = document.getElementById('btn-analizar');
  boton.disabled = true;
  boton.textContent = 'Analizando…';
  try {
    const resp = await fetch('/api/analizar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(valoresFormulario()),
    });
    const data = await resp.json();

    document.getElementById('veredicto').innerHTML = data.veredicto_html;
    document.getElementById('gauge').innerHTML = data.gauge_html;
    document.getElementById('consenso').innerHTML = data.consenso_html;
    document.getElementById('features').innerHTML = data.features_html;
    document.getElementById('percentiles').innerHTML = data.percentiles_html;
    document.getElementById('tabla-detalle').innerHTML = data.tabla_html;

    document.getElementById('veredicto').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (err) {
    document.getElementById('veredicto').innerHTML =
      `<div class="card verdict-card border-danger">
         <div class="verdict-eyebrow">ERROR</div>
         <div class="verdict-label text-danger">No se pudo contactar al servidor</div>
         <div class="muted">${err}</div>
       </div>`;
  } finally {
    boton.disabled = false;
    boton.textContent = '⚡ Analizar cuenta';
  }
}

document.getElementById('btn-analizar').addEventListener('click', analizarCuenta);

document.getElementById('btn-limpiar').addEventListener('click', () => {
  form.querySelectorAll('input[type=number]').forEach(i => { i.value = 0; });
});

document.getElementById('btn-medianas').addEventListener('click', async () => {
  const resp = await fetch('/api/medianas');
  const data = await resp.json();
  aplicarValores(data.valores);
});

document.querySelectorAll('[data-ejemplo]').forEach(boton => {
  boton.addEventListener('click', async () => {
    const resp = await fetch(`/api/ejemplo/${boton.dataset.ejemplo}`);
    const data = await resp.json();
    aplicarValores(data.valores);
    analizarCuenta();
  });
});

document.getElementById('btn-ir-archivo').addEventListener('click', () => irATab('archivo'));
document.getElementById('btn-ver-completo').addEventListener('click', () => irATab('archivo'));

// --- Analisis por lotes ------------------------------------------------------

document.getElementById('btn-analizar-archivo').addEventListener('click', async () => {
  const input = document.getElementById('input-archivo');
  const resumenTexto = document.getElementById('resumen-lote-texto');
  if (!input.files.length) {
    resumenTexto.textContent = 'Selecciona un archivo CSV.';
    return;
  }
  const boton = document.getElementById('btn-analizar-archivo');
  boton.disabled = true;
  boton.textContent = 'Analizando…';

  const cuerpo = new FormData();
  cuerpo.append('archivo', input.files[0]);

  try {
    const resp = await fetch('/api/lote', { method: 'POST', body: cuerpo });
    const data = await resp.json();

    if (!data.ok) {
      resumenTexto.textContent = data.mensaje || 'No se pudo procesar el archivo.';
      document.getElementById('tabla-lote').innerHTML = '';
      return;
    }

    resumenTexto.textContent = data.resumen_texto;
    document.getElementById('tabla-lote').innerHTML = data.tabla_html;

    const resumenSidebar = document.getElementById('resumen-lote-sidebar');
    resumenSidebar.innerHTML = data.resumen_html;

    const descarga = document.getElementById('btn-descarga-sidebar');
    descarga.href = data.descarga_url;
    descarga.style.display = 'block';
  } catch (err) {
    resumenTexto.textContent = `Error de conexión: ${err}`;
  } finally {
    boton.disabled = false;
    boton.textContent = 'Analizar archivo';
  }
});
