---
name: analista
description: Ejecuta de punta a punta un analista gráfico sobre CUALQUIER activo o lista de activos — divisas, acciones, índices, materias primas, cripto, futuros o ETFs, uno o cincuenta. Resuelve los símbolos en TradingView, los barre leyendo la tabla del indicador multitemporal, archiva las capturas por instrumento y fecha, extrae los datos a CSV, hace análisis gráfico y técnico propio con 120 velas diarias y entrega un Excel con veredicto COMPRAR/VENDER/ESPERAR más una ficha por instrumento. Úsala cuando el usuario diga "analista", "corre el analista", "analiza <cualquier activo o lista>", "analiza mi watchlist", "barre los gráficos", "dame el veredicto de", "análisis gráfico/técnico de". Corre sola de principio a fin sin pedir confirmaciones; si algo la bloquea, avisa con notificación en vez de quedarse esperando.
---

# Analista gráfico

Pipeline completo: de los gráficos de TradingView a un Excel con veredicto propio.
**Corre entero sin parar a preguntar.** El usuario lanza esto y se desconecta.

## Requisitos

1. El MCP de TradingView conectado (ver `01-mcp-tradingview` del kit).
2. **Un indicador que resuma OHLC + EMAs + MACD + RSI en tres temporalidades en una tabla.**
   Si no lo tienes, créalo con el prompt de `02-leer-datos`. La skill lee esa tabla; el nombre lo
   configuras abajo.
3. Python con `openpyxl`.

**Configura tu indicador aquí** (o pídele al usuario cómo se llama la primera vez):

```
NOMBRE_INDICADOR = "Mi Tabla"     <- el study_filter que usa data_get_pine_tables
```

## Carpeta de trabajo

Por defecto `<Documentos>/Mi analista grafico`. Se puede forzar con la variable de entorno
`ANALISTA_BASE`. En Windows, «Documentos» suele estar redirigido a OneDrive: los scripts lo
detectan solos.

```
Mi analista grafico/
├── imagenes/<INSTRUMENTO>/<AAAA-MM-DD>/   <- capturas
├── datos/                                  <- lo que se LEE
│   ├── BITACORA.md · lecturas_mtf.csv · operaciones.csv
└── analisis/                               <- lo que se CONCLUYE
    ├── ANALISIS_<TEMA>_<FECHA>.xlsx
    └── <INSTRUMENTO>/<FECHA>/<INSTRUMENTO>_analisis_<FECHA>.md
```

`datos/` y `analisis/` van separados a propósito: si mañana un veredicto resulta malo, los datos
siguen siendo válidos.

## Regla de oro: no pares, avisa

Nunca te quedes esperando en silencio. Si algo te bloquea (permiso denegado, TradingView caído,
un dato ilegible), **manda `PushNotification`** con qué te frenó y qué necesitas, y **sigue con
todo lo que no dependa de eso**. Al terminar, entrega lo que sí salió y di qué faltó.

Notifica solo en estos casos:
- Te deniegan un permiso y no puedes seguir por otra vía.
- TradingView no responde tras un reintento.
- Terminaste el pipeline completo.

No notifiques progreso intermedio.

## Fase 0 — Preflight

1. `tv_health_check`. Si falla, `tv_launch` y reintenta una vez. Si sigue caído → notifica y para.
2. **Apunta el símbolo y la temporalidad originales.** Al final hay que devolver el gráfico como
   estaba: es el gráfico de trabajo del usuario.
3. `chart_get_state` → confirma que el indicador de resumen está cargado. Si no está, notifica:
   sin él no hay barrido.
4. Verifica el esqueleto de carpetas (idempotente):

   ```bash
   python <ruta>/scripts/preparar.py
   ```

## Fase 1 — Qué instrumentos (cualquiera)

**Vale para cualquier activo que TradingView pueda pintar**: divisas, acciones, índices, materias
primas, cripto, futuros, ETFs. Uno o cincuenta.

1. **Símbolos exactos** (`NASDAQ:AAPL`, `BINANCE:BTCUSDT`) → úsalos tal cual.
2. **Nombres sueltos** ("Tesla", "el oro", "petróleo") → `symbol_search`. Ante varios resultados
   elige el contrato más líquido y **di cuál elegiste** ("USOIL de TVC, no el futuro CL1!").
   No inventes prefijos de mercado: búscalos.
3. **"mi watchlist"** → `watchlist_get`.
4. **Grupos** — atajos, no el alcance:

   | Atajo | Símbolos |
   |---|---|
   | majors | `FX:EURUSD` `FX:USDJPY` `FX:GBPUSD` `FX:USDCHF` `FX:AUDUSD` `FX:USDCAD` `FX:NZDUSD` |
   | metales | `OANDA:XAUUSD` `OANDA:XAGUSD` |
   | índices | `OANDA:NAS100USD` `OANDA:US30USD` `OANDA:SPX500USD` |
   | cripto | `BINANCE:BTCUSDT` `BINANCE:ETHUSDT` |

5. **Si no dijo nada**, mira el contexto (¿qué hay en `imagenes/`?). Si no hay pista, arranca con
   majors y dilo — no bloquees el pipeline preguntando.

### Nombre de carpeta vs. símbolo

`:` no vale en rutas. Usa **dos campos**: `simbolo` (para las llamadas al MCP: `BINANCE:BTCUSDT`)
e `instrumento` (para carpetas: `BTCUSDT`). La regla es `limpiar()` en `preparar.py`.

### Cuántos caben

Cada instrumento son ~4 llamadas más una lectura de imagen. Hasta ~15 va fluido. Por encima:
**hazlos todos igual**, pero avisa al empezar de que tardará y ve guardando el CSV según avanzas.
Si un símbolo no resuelve, **sáltalo, sigue, y dilo al final**. Nunca recortes en silencio.

## Fase 2 — Barrido (por instrumento)

1. `chart_set_symbol` con el `simbolo` completo → devuelve `chart_ready: false`, es normal.
2. `data_get_pine_tables` con `study_filter` de tu indicador.
   **Verifica que los precios corresponden al instrumento nuevo.** Si se parecen al anterior, la
   tabla está rancia: repite la lectura. Es el error más silencioso del pipeline.
3. `capture_screenshot` con `filename: "<INSTRUMENTO>_MTF_<AAAA-MM-DD>"`, `region: "full"`.
4. `data_get_ohlcv` con `count: 120, summary: true`.
   **Esto es lo que separa un análisis de una foto**: sin el rango de 120 días no sabes si lo que
   ves es tendencia o rebote.

Secuencial: hay un solo gráfico. No intentes paralelizar.

## Fase 3 — Archivar

```bash
python <ruta>/scripts/preparar.py 2026-08-04 "EURUSD,USDJPY,GBPUSD"
```

Avisa de las que no encontró (`SIN CAPTURA`). **No muevas ficheros a mano**: toda la escritura pasa
por este script a propósito, para que la lista de permisos siga siendo de dos entradas.

## Fase 4 — Datos

Añade a `datos/lecturas_mtf.csv` una fila por instrumento y temporalidad (60/240/D).

## Fase 5 — Análisis propio

**Lee las capturas.** Sin mirar los gráficos esto no es análisis gráfico, es copiar una tabla.
Busca: estructura de máximos y mínimos, rangos, roturas, velas de volumen anómalo (compara el
volumen de las últimas barras contra `avg_volume`).

Decide **COMPRAR / VENDER / ESPERAR**. Criterios que valen para cualquier activo:

- **Posición en el rango de 120 días.** `(cierre − mínimo) / (máximo − mínimo)`. Comprar por
  encima del 60% o vender por debajo del 40% es pagar el peor precio del rango.
- **¿Tendencia o rebote?** Si la variación de 120 días va en contra de la señal, es rebote
  contratendencia. Dilo.
- **¿Ya pasó el movimiento?** Una caída vertical con volumen 3x+ y el RSI en extremo no es señal
  de entrada: es señal de que llegas tarde.
- **Factor común.** Agrupa antes de sumar riesgo. Lo compartido cambia según la clase, pero el
  error es el mismo: confundir varias señales con varias oportunidades.
  - divisas → la moneda repetida (todos los `XXX/USD` son la misma apuesta al dólar)
  - acciones → sector, y sobre todo el índice: seis tecnológicas son el Nasdaq con más pasos
  - índices → casi todo lo americano va junto
  - cripto → BTC manda; las alts son BTC apalancado hasta que se demuestre lo contrario
- **Coincidir con el indicador no es el objetivo.** Cuando discrepes, di por qué en la tesis.

### Lo que cambia según la clase de activo

| Clase | Qué mirar además | Qué NO aplicar |
|---|---|---|
| **Acciones** | Huecos de apertura (el rango intradía miente), volumen relativo, si hay resultados cerca | El ATR de 240 min subestima el riesgo: el hueco salta el stop |
| **Índices** | Si es CFD o futuro: distinto horario, volumen y spread | Comparar volumen de CFD con el de un futuro |
| **Cripto** | Cotiza 24/7; ojo con fines de semana de liquidez fina | La trampa horaria de abajo |
| **Materias primas** | Vencimientos y rolos; el continuo tiene saltos que no son mercado | Leer un salto de rolo como rotura |
| **Divisas** | La sesión (Asia/Londres/NY) manda en el corto plazo | — |

Si hay un motivo conocido detrás del movimiento (resultados, dato macro, vencimiento), **dilo**.
Un gráfico sin ese contexto es la mitad de la historia.

## Fase 6 — Entregables

Escribe un JSON (contrato en `CONTRATO_JSON.md`) y ejecútalo:

```bash
python <ruta>/scripts/construir_entregables.py <ruta_json>
```

Genera el Excel de 4 hojas (Veredictos · Técnico · Niveles · Método y avisos) y una ficha por
instrumento. Deja el JSON en un temporal, no en la carpeta del usuario.

`tema` es el nombre del fichero: `ANALISIS_<TEMA>_<FECHA>.xlsx`. Algo que describa el barrido —
`MAJORS`, `TECH_USA`, `CRIPTO`, `WATCHLIST`. Mayúsculas, sin espacios.

Luego:
- Añade la entrada a `datos/BITACORA.md`, **arriba del todo**.
- **Devuelve el gráfico al símbolo y temporalidad originales.**
- Notificación de cierre.

## Reglas de calidad (van en cada entrega)

1. **Nunca inventes un precio ni una hora.** Lo que no se lea, `?`.
2. **Separa observado de interpretado.** Campos distintos en la ficha y en la bitácora.
3. **Fecha y respalda.** Cada conclusión apunta a la captura que la sostiene.
4. **Di lo que el dato no puede decir.** Ninguna de estas lecturas tiene backtest ni expectativa
   medida detrás; que aparezca en la hoja de avisos.

## Audita tu indicador (no lo des por bueno)

Un indicador de resumen puede tener defectos que no se ven hasta que los buscas. **Compruébalo en
cada corrida** y mete en la hoja de avisos lo que aplique. Dos casos reales encontrados así:

| Defecto | Cómo se detecta |
|---|---|
| **Una columna sale siempre `0`** | Un MACD formateado a 2 decimales sobre precios de 5 decimales redondea siempre a cero. Parece un mercado plano; es un error de formato. Y si esa columna entra en un «score», el score está calculado con un componente muerto. |
| **El tamaño de posición está mal** | Una fila de riesgo que dice «lotes» pero da **unidades**, y que no convierte la divisa de cotización. En un par de 5 decimales la diferencia es de 100.000×. **Comprueba a mano el cálculo de tamaño antes de fiarte de él, siempre.** |
| **La tabla va una vela atrasada** | El indicador devuelve el cierre de *ayer* como si fuera el de hoy, en las tres temporalidades. Se caza cruzando el cierre de la tabla con el de `data_get_ohlcv`: si no coinciden, la tabla miente. Es el más peligroso de los tres, porque los números son reales — solo que de la vela anterior. |

**Cruza siempre el precio de la tabla contra el OHLCV antes de usarla.** Son dos líneas de
verificación y te ahorra un análisis entero construido sobre datos de ayer.

La lección general: **verifica los cálculos de tu indicador con un ejemplo hecho a mano** antes de
construir nada encima. Un error de formato, de unidades o de desfase no falla ruidosamente —
devuelve un número plausible y equivocado.

## Trampa horaria

Depende del activo:

- **Divisas y CFDs**: cerca del cambio de vela diaria o en apertura asiática, las velas D tienen
  minutos de vida y la estructura diaria no significa nada. Para comparar entre días, la hora buena
  es la apertura de Londres.
- **Acciones e índices al contado**: fuera de sesión el último precio está congelado. Un barrido a
  medianoche es válido, pero es de ayer: dilo.
- **Cripto**: no aplica, cotiza 24/7. Sí conviene notar si cae en fin de semana.

**La hora del barrido va siempre en la hoja de avisos.**
