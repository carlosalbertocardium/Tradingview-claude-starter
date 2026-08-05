# 02 · Leer datos del gráfico

La parte que casi nadie resuelve bien. Aquí está el truco que hace que valga la pena todo lo demás.

---

## Qué se lee directamente

| Dato | Herramienta | ¿Sale limpio? |
|---|---|---|
| Precio, OHLC, volumen actual | `quote_get` | ✅ |
| Histórico de velas (resumen o barras) | `data_get_ohlcv` | ✅ |
| Símbolo, temporalidad, lista de indicadores | `chart_get_state` | ✅ |
| Medias móviles del **panel principal** | `data_get_study_values` | ✅ |
| **RSI, MACD, ATR** y todo lo de subpaneles | `data_get_study_values` | ❌ **no aparecen** |
| Captura de pantalla | `capture_screenshot` | ✅ (imagen) |

Esa fila roja es el problema. Los indicadores que viven en su propio panel abajo **no están
expuestos**. Y son justo los que quieres.

---

## El truco: que el indicador escriba su propia tabla

En vez de pelearte con el MCP, das la vuelta al problema.

Pine Script puede dibujar tablas en el gráfico con `table.new()`. Y el MCP **sí sabe leer esas
tablas** como texto, con `data_get_pine_tables`.

Entonces: escribes un indicador de pocas líneas que calcule lo que quieras y lo vuelque en una
tabla. A partir de ahí Claude lo lee como texto limpio y exacto.

```
       ANTES                              DESPUÉS
  RSI en un subpanel            Indicador propio → table.new()
         ↓                                  ↓
  invisible para el MCP            data_get_pine_tables
                                            ↓
                                  "RSI(14) | 1H 71.85 | 4H 66.28 | 1D 60.84"
```

**Esto generaliza a todo.** Cualquier cosa que sepas calcular en Pine —tu propia lógica, métricas
de varias temporalidades a la vez, distancias a niveles, lo que sea— se vuelve legible por Claude.
Deja de importar si el MCP "soporta" tu indicador.

---

## Créate el tuyo

Pídeselo a Claude con el MCP conectado. Este prompt funciona; **cambia las filas por lo que tú uses**:

```
Tengo el MCP de TradingView conectado. Necesito valores numéricos EXACTOS como TEXTO,
pero data_get_study_values solo devuelve los indicadores del panel principal — RSI, MACD
y ATR viven en subpaneles y no aparecen. Sé que data_get_pine_tables SÍ lee lo que un
indicador dibuja con table.new.

Créame un indicador en Pine Script v6 llamado "Mi Tabla" que dibuje UNA tabla legible con
data_get_pine_tables study_filter="Mi Tabla".

Columnas: Métrica | 1H | 4H | 1D
Filas (todas vía request.security con barmerge.gaps_off y barmerge.lookahead_off para NO repintar):
- Precio (close)
- RSI(14)
- MACD línea, señal e histograma
- EMA20, EMA50, EMA200
- ATR(14)
- Volumen relativo: volume / ta.sma(volume,20) en %
- Tendencia: "Alcista" si close>EMA200, si no "Bajista"

Requisitos:
- indicator("Mi Tabla", overlay=true)
- Celda (0,0) con el texto "MI TABLA" para poder filtrar
- Valores como texto con 2-3 decimales (str.tostring con "#.###")
- position.top_right, legible
- Hazlo end-to-end con las tools del MCP: pine_new/pine_set_source → pine_smart_compile →
  si hay errores pine_get_errors y corrige → pine_save → añádelo al gráfico y déjalo VISIBLE
- Verifica con data_get_pine_tables y pégame la salida
```

Claude lo escribe, lo compila, corrige los errores y lo deja funcionando. Suele salir a la primera
o a la segunda.

### Los dos detalles que importan

**`barmerge.lookahead_off`.** Sin esto, `request.security` te deja ver datos del futuro en las velas
históricas. Tu indicador parecerá un oráculo en el pasado y fallará en vivo. Es el error clásico de
Pine multitemporal, y arruina cualquier backtest hecho encima.

**La celda de filtro.** Poner un texto identificable en la celda `(0,0)` te deja usar
`study_filter="MI TABLA"` y leer solo esa tabla, en vez de recibir todas las del gráfico.

---

## Lee números como texto, no como imágenes

Regla de economía que cambia el coste de todo:

| | Tokens | Exactitud |
|---|---|---|
| Captura de pantalla | 1.000–2.000 | Claude puede leer mal un dígito |
| La misma tabla como texto | ~200 | Exacta |

**Usa la captura para ver estructura** —dónde están los máximos y mínimos, si hubo una rotura, si
una vela tiene volumen anómalo—, no para leer valores. Los números que vayan a acabar en una
decisión, siempre como texto.

Si vas a barrer treinta instrumentos, esta diferencia decide si el proceso es viable o no.

---

## Otras herramientas de lectura Pine

`data_get_pine_tables` no es la única. El mismo principio vale para:

| Lo que dibuja tu indicador | Cómo se lee |
|---|---|
| `table.new()` | `data_get_pine_tables` |
| `label.new()` | `data_get_pine_labels` |
| `line.new()` | `data_get_pine_lines` |
| `box.new()` | `data_get_pine_boxes` |

Las **etiquetas** van muy bien para niveles con nombre (`"Soporte 1.0850"`) y las **líneas** para
sacar la lista de niveles horizontales que pinta tu indicador. Todo tiene que estar **visible** en
el gráfico para poder leerse.

---

## Antes de seguir

Comprueba que tienes esto funcionando:

```
Léeme la tabla de mi indicador y dime el RSI de las tres temporalidades.
```

Si Claude te devuelve números exactos, ya tienes lo esencial. Lo del [`03`](../03-skill-analista/)
es automatizar el ciclo completo encima de esta base.
