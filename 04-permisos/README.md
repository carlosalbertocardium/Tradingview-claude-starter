# 04 · Que deje de pedirte permiso a cada paso

Por defecto, Claude Code te pide confirmación antes de ejecutar comandos o escribir ficheros. Está
bien mientras aprendes. Cuando ya sabes qué hace el pipeline, ese goteo de prompts es justo lo que
impide dejarlo corriendo e irte.

> **Lee esto antes de copiar nada.** Conceder permisos que no entiendes es peor que tener que
> aprobarlos a mano. Si vas a pegar una lista, que sea una que puedas explicar línea por línea.

---

## Cómo funciona

En `~/.claude/settings.local.json` hay una lista `permissions.allow`. Lo que coincida con un patrón
de ahí se ejecuta sin preguntar.

```json
{
  "permissions": {
    "allow": [
      "mcp__tradingview__quote_get"
    ]
  }
}
```

---

## La lista mínima para este pipeline

Copia esto dentro de tu `permissions.allow` y **cambia `TU_USUARIO` por el tuyo**:

```json
"mcp__tradingview__tv_launch",
"mcp__tradingview__tv_health_check",
"mcp__tradingview__chart_get_state",
"mcp__tradingview__chart_set_symbol",
"mcp__tradingview__chart_set_timeframe",
"mcp__tradingview__capture_screenshot",
"mcp__tradingview__data_get_ohlcv",
"mcp__tradingview__data_get_pine_tables",
"mcp__tradingview__data_get_pine_labels",
"mcp__tradingview__data_get_study_values",
"mcp__tradingview__quote_get",
"mcp__tradingview__symbol_search",
"mcp__tradingview__watchlist_get"
```

### Qué concede exactamente

**Leer el gráfico** (`quote_get`, `data_get_*`, `chart_get_state`, `symbol_search`,
`watchlist_get`) — solo lectura, no cambia nada.

**Cambiar el gráfico** (`chart_set_symbol`, `chart_set_timeframe`) — modifica lo que tienes en
pantalla. La skill guarda el símbolo original y lo restaura al terminar, pero si estás mirando algo
mientras corre, te lo va a mover.

**Capturar** (`capture_screenshot`) — escribe un PNG en la carpeta del MCP.

**Lanzar** (`tv_launch`) — abre TradingView si está cerrado.

### Lo que deliberadamente NO está

Las herramientas `pine_*` (`pine_set_source`, `pine_save`, `pine_new`…) **no están en la lista a
propósito**: pueden crear y sobrescribir tus indicadores. Si le pides a Claude que te escriba uno,
te va a pedir permiso — y ahí sí quieres enterarte.

---

## Si además usas la skill del `03`

Necesitas dos permisos más: ejecutar sus scripts y escribir en la carpeta de trabajo.

**macOS / Linux:**
```json
"Bash(python ~/.claude/skills/analista/scripts/preparar.py*)",
"Bash(python ~/.claude/skills/analista/scripts/construir_entregables.py*)"
```

**Windows:**
```json
"PowerShell(python \"C:\\\\Users\\\\TU_USUARIO\\\\.claude\\\\skills\\\\analista\\\\scripts\\\\preparar.py\"*)",
"PowerShell(python \"C:\\\\Users\\\\TU_USUARIO\\\\.claude\\\\skills\\\\analista\\\\scripts\\\\construir_entregables.py\"*)"
```

Más la carpeta de trabajo (ajusta la ruta a la tuya):
```json
"Write(//c/Users/TU_USUARIO/OneDrive/Documentos/Mi analista grafico/**)",
"Edit(//c/Users/TU_USUARIO/OneDrive/Documentos/Mi analista grafico/**)"
```

**Fíjate en el detalle:** se autoriza *ejecutar esos dos scripts concretos*, no «mover ficheros» ni
«ejecutar python». La skill está diseñada para que toda su escritura pase por ahí precisamente para
que esta lista pueda ser tan corta. Autorizar `Move-Item` a secas le daría permiso para mover
cualquier fichero de tu disco.

---

## Lo que esto NO arregla

Claude Code tiene una capa de seguridad **por encima** de tu allowlist que juzga las acciones por su
naturaleza. Todo lo que huela a modificar configuración o credenciales va a seguir pidiendo
confirmación, tengas el permiso o no. Es a propósito y no conviene buscarle la vuelta.

Por eso la skill del `03` tiene protocolo de notificación: si algo la para, te avisa y sigue con lo
demás, en vez de quedarse esperando a que te des cuenta.

**Los permisos reducen las interrupciones. No las eliminan.**

---

## Consejo

Empieza **sin** allowlist. Corre el pipeline una vez aprobando a mano y mira qué te pide. Añade solo
eso. Vas a entender qué concede cada línea porque la viste pasar, y no vas a autorizar cosas que tu
flujo no usa.
