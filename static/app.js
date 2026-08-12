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

function fijarToggle(nombre, valor) {
  const grupo = form.querySelector(`.toggle-group[data-name="${nombre}"]`);
  if (!grupo) return;
  const oculto = form.querySelector(`input[type=hidden][name="${nombre}"]`);
  if (oculto) oculto.value = valor;
  grupo.querySelectorAll('.toggle-btn').forEach(b => {
    b.classList.toggle('active', Number(b.dataset.valor) === Number(valor));
  });
}

function validarCampoLocal(input) {
  const valor = parseFloat(input.value);
  const max = input.getAttribute('max');
  const invalido = input.value === '' || Number.isNaN(valor) || valor < 0 ||
    (max !== null && valor > parseFloat(max));
  input.classList.toggle('input-error', invalido);
}

function aplicarValores(valores) {
  Object.entries(valores).forEach(([clave, valor]) => {
    const toggle = form.querySelector(`.toggle-group[data-name="${clave}"]`);
    if (toggle) {
      fijarToggle(clave, Number(valor) >= 0.5 ? 1 : 0);
      return;
    }
    const campo = form.querySelector(`input[name="${clave}"]`);
    if (campo) {
      campo.value = valor;
      validarCampoLocal(campo);
    }
  });
}

// Botones +/- de los campos numericos
form.querySelectorAll('.step-btn').forEach(boton => {
  boton.addEventListener('click', () => {
    const input = boton.parentElement.querySelector('input[type=number]');
    const paso = parseFloat(input.dataset.paso || '1');
    const max = input.getAttribute('max');
    let nuevo = (parseFloat(input.value) || 0) + paso * Number(boton.dataset.dir);
    nuevo = Math.max(0, nuevo);
    if (max !== null) nuevo = Math.min(parseFloat(max), nuevo);
    input.value = Number.isInteger(paso) ? Math.round(nuevo) : Math.round(nuevo * 100) / 100;
    validarCampoLocal(input);
  });
});

// Botones Si/No de los campos binarios
form.querySelectorAll('.toggle-group').forEach(grupo => {
  grupo.querySelectorAll('.toggle-btn').forEach(boton => {
    boton.addEventListener('click', () => fijarToggle(grupo.dataset.name, boton.dataset.valor));
  });
});

// Validacion visual en vivo mientras se escribe
form.querySelectorAll('input[type=number]').forEach(input => {
  input.addEventListener('input', () => validarCampoLocal(input));
});

// Expandir / colapsar todos los grupos del formulario de un clic
document.getElementById('btn-expandir-todo').addEventListener('click', () => {
  form.querySelectorAll('.input-accordion').forEach(d => { d.open = true; });
});
document.getElementById('btn-colapsar-todo').addEventListener('click', () => {
  form.querySelectorAll('.input-accordion').forEach(d => { d.open = false; });
});

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
  form.querySelectorAll('input[type=number]').forEach(i => { i.value = 0; i.classList.remove('input-error'); });
  form.querySelectorAll('.toggle-group').forEach(g => fijarToggle(g.dataset.name, 0));
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
