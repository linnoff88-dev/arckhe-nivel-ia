# nivel-ia: ¿en qué peldaño está la IA en tu trabajo?

[![Escalera de la IA: AL1 a AL5](guia/assets/banner-es.jpg)](https://inematds.github.io/nivel-ia/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Sin medir, no sabes qué sigues haciendo a mano, qué ya hace la IA por sí sola ni qué puertas le has abierto. Este kit ofrece una escala de cinco peldaños, desde AL1 (tú lo haces por tu cuenta) hasta AL5 (la IA funciona sola), y dos formas de medir: una ficha en papel, que sirve para cualquier persona y cualquier IA, y un programa que lee los registros de Claude Code y Codex en tu computadora y anota cada conexión usada. Al final, sabes en qué peldaño está cada tarea, cuál puede subir ahora y cuándo debe bajar. Para empezar, basta con imprimir la ficha.

## 📖 Guía de uso

Guía completa (página de presentación + paso a paso): **https://inematds.github.io/nivel-ia/guia/es/**

## En detalle

Kit abierto y gratuito para medir cuánto de tu trabajo ya hace la IA, tarea por tarea, en la **escalera AL1 a AL5**. Puedes medir **en papel** (una ficha para imprimir) o **automáticamente** (un programa lee los registros de Claude Code y Codex en tu computadora). Ambos registran **todas las conexiones** que usó la IA e indican **quién puede subir un peldaño** y cuándo debe bajar.

| Peldaño | Qué significa |
|---|---|
| AL1 | Tú lo haces por tu cuenta. La IA no participa. |
| AL2 | La IA ayuda: tú preguntas, ella responde y tú haces el trabajo. |
| AL3 | La IA colabora: trabajan juntos paso a paso y tú diriges. |
| AL4 | La IA dirige y tú solo revisas antes de que salga. |
| AL5 | La IA funciona sola, con horario, regla y alarma. |

La escalera completa, con **cómo subir cada peldaño y cuándo bajar**, está en [ESCADA.md (en portugués)](ESCADA.md).

## El proceso, de principio a fin

Quién lo hace: 🧠 tú · ⚙️ script o temporizador

1. 🧠 **Lee la escalera** y elige 3 tareas que haces todas las semanas: [ESCADA.md (en portugués)](ESCADA.md).
2. 🧠 **En papel:** imprime la ficha (https://inematds.github.io/nivel-ia/kit/ficha-papel.es.html) y anota una línea por tarea (fecha, tarea, ¿crítica? s/n, peldaño 1 a 5, minutos, conexión usada, ¿corregí? n/p/g, ¿error grave? s/n). Sirve para cualquier IA y para lo que haces sin IA (AL1).
3. 🧠 **Digitaliza la ficha** (opcional): copia `kit/papel-modelo.csv` en `registro/papel.csv`, ábrelo en una hoja de cálculo, escribe las líneas y guárdalo como CSV. Compruébalo con `python3 medir/nivel.py papel`. Si solo usas la ficha, puedes omitir los pasos 4 y 6: el informe sale solo con ella.
4. ⚙️ **Automático:** `python3 medir/nivel.py varrer --dias 30` lee los registros de Claude Code y Codex de esta computadora y los guarda en `registro/sessoes.json`.
5. ⚙️ **Informe:** `python3 medir/nivel.py relatorio --lang es` genera la escalera, las tareas, el próximo peldaño de cada una, las conexiones y «quién puede subir ahora» en `registro/relatorio.md` (combina la ficha en papel si existe).
6. ⚙️ **Todas las conexiones:** `python3 medir/nivel.py conexoes` enumera cada programa, sitio, servicio, agente y skill, con la primera y la última vez que se usaron.
7. ⚙️ **Todos los días, automáticamente:** `sh systemd/instalar.sh` activa un temporizador a las 06:20 que repite los pasos 4 y 5 y guarda el historial en `registro/historico.jsonl`.
8. ⚙️ **Certificado:** `python3 medir/certificado.py --nome "Tu Nombre" --lang es` genera `registro/certificado-AAAA-MM-DD-es.html`: escalón, escalera AL1–AL5, tareas, evolución semana a semana y proyección (1, 3 y 6 meses). Ábrelo en el navegador y usa el botón para guardarlo como PDF. Período más largo: `nivel.py --registro /tmp/n90 varrer --dias 90`, `nivel.py --registro /tmp/n90 relatorio --lang es` y `certificado.py --nome "Tu Nombre" --lang es --registro /tmp/n90`.
9. 🧠 **Una vez por semana:** lee el informe, elige UNA tarea para subir un peldaño (criterios en ESCADA.md) y baja la que tuvo un error grave.

## 🎓 Certificado: paso a paso

Una página con el % de tu trabajo realizado por la IA, la escala AL1–AL5, las tareas principales, la evolución semana a semana y la proyección para 1, 3 y 6 meses. Es HTML: se abre en cualquier navegador y se convierte en PDF con el botón "Guardar como PDF".

**La forma más fácil (forma B): pídeselo a tu IA.** Abre Claude Code o Codex y pega esto (cambia el nombre). ¿Datos confidenciales? Usa el método de la terminal, justo abajo (consulta Privacidad).

> Descarga el kit https://github.com/inematds/nivel-ia en una carpeta nivel-ia (si ya existe, úsala), mide mis últimos 30 días con `python3 medir/nivel.py varrer --dias 30` y `python3 medir/nivel.py relatorio --lang es`, genera mi certificado con `python3 medir/certificado.py --nome "Tu Nombre" --lang es` y abre el certificado en el navegador. Al final, dime dónde quedaron el certificado y el informe y resume en 3 líneas qué resultado dio. No abras el archivo registro/sessoes.json ni envíes mis datos a ningún otro servicio ni sitio.

**Hazlo tú, comando por comando** (Linux o Mac; en Windows, WSL; Python 3.9+; haber usado Claude Code o Codex en esta máquina):

```bash
git clone https://github.com/inematds/nivel-ia && cd nivel-ia
python3 medir/nivel.py varrer --dias 30          # 1. mide los últimos 30 días (nada sale de la máquina)
python3 medir/nivel.py relatorio --lang es                 # 2. prepara el informe
python3 medir/certificado.py --nome "Tu Nombre" --lang es   # 3. genera el certificado
xdg-open registro/certificado-*.html             # 4. abre (en Mac: open) → botón "Guardar em PDF"
```

Período más largo (p. ej., 90 días), sin modificar el registro diario: `python3 medir/nivel.py --registro /tmp/n90 varrer --dias 90`, `python3 medir/nivel.py --registro /tmp/n90 relatorio --lang es` y `python3 medir/certificado.py --nome "Tu Nombre" --registro /tmp/n90`. Claude Code borra los registros de más de 30 días, a menos que aumentes `cleanupPeriodDays`; lo que ya se borró no se puede recuperar. Si los registros cubren menos días de los solicitados, el medidor lo avisa en la terminal, en el informe y en el certificado.

**Dónde quedan los archivos**

| Archivo | Qué es |
|---|---|
| `registro/certificado-AAAA-MM-DD-es.html` | El certificado (ábrelo en el navegador → "Guardar como PDF") |
| `registro/relatorio.md` | El informe completo: escala, tareas, próximo nivel, quién puede subir, conexiones |
| `registro/relatorio.json` | Los mismos números en formato de datos (el certificado los lee de aquí) |
| `registro/sessoes.json` | La medición sesión por sesión (solo en tu máquina, fuera de git) |

## Requisitos

Terminal, Python 3.9 o posterior (solo biblioteca estándar, sin instalar nada) y git para descargarlo (o descarga el ZIP: https://github.com/inematds/nivel-ia/archive/refs/heads/main.zip). Linux o macOS (en Windows, usa WSL). El temporizador usa systemd (Linux). Sin red, sin API: nada sale de tu computadora.

## Qué ve y qué no ve la medición automática

- **Ve:** sesiones de Claude Code (`~/.claude/projects`) y de Codex (`~/.codex*/sessions`), cuántos mensajes enviaste, cuántas acciones hizo la IA, cuánto tiempo, qué programas, sitios y servicios (MCP), agentes y skills usó, y qué acciones tuvieron efecto fuera de la computadora (publicar, enviar, subir).
- **No ve:** lo que haces sin IA (AL1: solo en la ficha), otras IA (ChatGPT en el navegador: ficha), si aprobaste en el prompt ni si la IA acertó (columna «¿corregí?» de la ficha).
- **Cómo decide el peldaño:** una sesión iniciada por script, bot u horario (`claude -p`, `codex exec`) con hasta 2 mensajes = AL5 (3 o más = conversación); un pedido tuyo hecho por el bot (Telegram) = AL4; una conversación tuya en la terminal: 15 o más acciones de la IA por cada mensaje tuyo = AL4, de 5 a 14 = AL3, menos = AL2 (una pregunta suelta es AL2).
- **Subir y bajar:** se determina con las columnas «¿corregí?» (n/p/g) y «¿error grave?» (s/n) de la ficha. AL1→AL2 sin criterio; AL2→AL3: como máximo 1 corrección grande en las últimas 10 veces; AL3→AL4: como máximo 2 en 20; AL4→AL5: como máximo 2 en 50 y ningún error grave. Bajar: 1 error grave o 3 correcciones grandes en las últimas 10 veces. Solo cuentan las veces del peldaño actual (al cambiar de peldaño, el conteo empieza de nuevo). Una tarea crítica (marcada en la ficha o reconocida por palabras como publicar, cliente, servidor, correo electrónico…) se detiene en AL4. Sin ficha, el informe incluye la tarea como candidata e indica cuántas veces debes anotarla. Más detalles en [ESCADA.md (en portugués)](ESCADA.md). Los límites están al principio de `medir/nivel.py`.
- **Tareas:** se agrupan por palabras clave del primer pedido. Para usar las tuyas, copia `medir/tarefas.exemplo.json` en `medir/tarefas.json` y edítalo (formato `[["Nombre de la tarea", crítica true/false, ["palabra", "otra"]]]`). Las tareas críticas se detienen en AL4.

## Ejemplo real

[exemplo/relatorio-agregado.json (en portugués)](exemplo/relatorio-agregado.json): medición del trabajo de Nei Maldaner (INEMA) durante 30 días, solo con totales (sin pedidos, carpetas ni sitios).

## Pruebas

`python3 tests/run.py` (46 pruebas con registros falsos, nada de tu computadora).

## Privacidad

**Dos formas de ejecutarlo.** El medidor es Python puro y se ejecuta solo en tu máquina, sin internet. **A. Desde la terminal**: ejecutas los comandos y abres el certificado; nada sale de la computadora. **B. Pidiéndoselo a tu IA**: Claude Code o Codex ejecuta los comandos y lee el informe para resumírtelo, y esa lectura pasa por el servidor del proveedor (Anthropic u OpenAI), como cualquier sesión. El informe incluye los nombres de las tareas y las conexiones (programas, agentes, skills y sitios). Estos nombres pueden revelar el nombre de un cliente o de un proyecto. **Datos confidenciales (trabajo de clientes, confidencialidad): usa la forma A.**

`registro/` queda fuera de git. Se guarda una versión breve del primer pedido de cada sesión, con las claves, los correos electrónicos y los números largos reemplazados por `[oculto]`.

Licencia MIT · kit abierto y gratuito · [inema.club](https://inema.club)