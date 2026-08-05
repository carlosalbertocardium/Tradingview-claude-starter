# Empieza aquí

Ruta manual, paso a paso. Si prefieres que Claude te lo monte, dale la URL del repo y pídeselo —
trae un `CLAUDE.md` con instrucciones para guiarte.

**Tiempo:** unos 20 minutos hasta ver a Claude leyendo tu gráfico.

---

## Antes de empezar

- [ ] **TradingView Desktop** instalado (la app, no la web)
- [ ] **Claude Code** funcionando
- [ ] **Node.js** — comprueba con `node --version`
- [ ] **Python 3** — `python --version` (solo si vas a llegar al paso 3)

---

## Paso 1 · Conectar (10 min) — obligatorio

Instala el puente y aprende a lanzar TradingView con el puerto de depuración abierto.

→ **[`01-mcp-tradingview/`](01-mcp-tradingview/)**

**Sabrás que funciona cuando:** le pidas a Claude que compruebe la conexión y responda
`cdp_connected: true`.

Si falla → [`SOLUCION-PROBLEMAS.md`](01-mcp-tradingview/SOLUCION-PROBLEMAS.md). El 90% de las veces
es TradingView abierto sin el puerto.

---

## Paso 2 · Leer (10 min) — obligatorio

Aprende qué expone el MCP, qué **no**, y el truco para leer cualquier indicador.

→ **[`02-leer-datos/`](02-leer-datos/)**

**Sabrás que funciona cuando:** Claude te dé el RSI exacto de tres temporalidades como texto.

Este paso es el que más se reutiliza. Aunque no sigas al 3, aquí ya tienes algo útil todos los días.

---

## Paso 3 · Automatizar (15 min) — opcional

Instala la skill que hace el ciclo completo sola.

→ **[`03-skill-analista/`](03-skill-analista/)**

**Sabrás que funciona cuando:** `/analista majors` termine solo y te deje un Excel.

---

## Paso 4 · Sin interrupciones (5 min) — opcional

Autoriza lo que el pipeline necesita para poder lanzarlo e irte.

→ **[`04-permisos/`](04-permisos/)**

Hazlo **al final**, cuando ya viste qué te pide. Así entiendes lo que autorizas.

---

## Puntos de parada válidos

No hace falta llegar al final. Cada paso deja algo que funciona:

| Si paras en… | Te llevas |
|---|---|
| **1** | Claude ve tu gráfico: precios, velas, capturas, cambiar de símbolo |
| **2** | Claude lee los valores exactos de tus indicadores como texto |
| **3** | El ciclo completo automatizado con veredicto |
| **4** | Todo lo anterior, sin que te pida permiso |

---

## Cuando algo se rompa

Pásale el repo a Claude con el error literal:

> Estoy en el paso [N] de este repo y me sale esto: [pega el error completo].
> Ayúdame a diagnosticarlo.

Pega la salida real, no tu resumen. La diferencia entre "no funciona" y el mensaje exacto es la
mitad del diagnóstico.
