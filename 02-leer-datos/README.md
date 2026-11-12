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
| **RSI, MACD, ATR** y todo lo de subpaneles | `data_get_study_values` | ⚠ **sí, pero mal** |
| Captura de pantalla | `capture_screenshot` | ✅ (imagen) |

Esa fila es el problema, y no es el que parece.

**Sí aparecen.** Verificado el 2026-11-11 contra el MCP: `data_get_study_values` devolvió RSI,
MACD, ATR, Connors RSI y un indicador propio, todos de subpanel. Si leíste en otro sitio que los
subpaneles son invisibles —o en una versión anterior de este repo—, está desactualizado.

Lo que falla son otras tres cosas, y pesan más:

1. **Solo la temporalidad del gráfico.** Un valor por indicador, el de la resolución que tengas
   puesta. Para el RSI de 1H, 4H y 1D son tres cambios de temporalidad y tres llamadas, moviéndole
   el gráfico al usuario tres veces.
2. **Los números vienen con el locale de la aplicación.** En una instalación en español salen
   `35,40` y `−29,00`: coma decimal y signo menos **Unicode** (U+2212), que no es el guión ASCII.
   Un `float()` directo revienta — o, peor, funciona en unos valores y falla en otros.
3. **El coste.** La respuesta incluye el código fuente ofuscado de cada indicador en
   `inputs.text`: unos **8.000 tokens para leer cinco números**. La misma información en una tabla
   Pine son ~200.

Por eso el truco de abajo sigue siendo la pieza central del repo. Pero por estas tres razones, no
porque los datos sean inaccesibles.

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
  1 sola temporalidad               data_get_pine_tables
  "35,40" y 8k tokens                       ↓
                                  "RSI(14) | 1H 71.85 | 4H 66.28 | 1D 60.84"
```

**Esto generaliza a todo.** Cualquier cosa que sepas calcular en Pine —tu propia lógica, métricas
de varias temporalidades a la vez, distancias a niveles, lo que sea— se vuelve legible por Claude.
Deja de importar si el MCP "soporta" tu indicador.

---

## Créate el tuyo

Pídeselo a Claude con el MCP conectado. Este prompt funciona; **cambia las filas por lo que tú uses**:

```
Tengo el MCP de TradingView conectado. Necesito valores numéricos EXACTOS como TEXTO y de
VARIAS temporalidades a la vez. data_get_study_values me sirve de a poco: da una sola
temporalidad, con el locale de la app (coma decimal y signo menos Unicode) y miles de
tokens de código ofuscado por respuesta. Sé que data_get_pine_tables lee limpio lo que un
indicador dibuja con table.new.

Créame un indicador en Pine Script v6 llamado "Mi Tabla" que dibuje UNA tabla legible con
data_get_pine_tables study_filter="Mi Tabla".

Columnas: Métrica | 1H | 4H | 1D
Filas (todas vía request.security con barmerge.gaps_off y barmerge.lookahead_off para NO repintar):
- Precio (close), Apertura, Máximo, Mínimo
- Var %: (close - close[1]) / close[1] * 100
- EMA20, EMA50, EMA200
- vs EMA200 %: (close - EMA200) / EMA200 * 100
- Estructura: "Alcista" si EMA20>EMA50>EMA200, "Bajista" si al revés, si no "Mixto"
- MACD histograma, y su dirección ("sube"/"baja") con ta.change
- RSI(14), y su dirección
- ATR(14)
- Volumen relativo: volume / ta.sma(volume,20) en %

Requisitos:
- indicator("Mi Tabla", overlay=true)
- Celda (0,0) con el texto "MI TABLA" como rótulo de la tabla (el study_filter filtra por
  el NOMBRE del indicador, no por la celda, pero el rótulo ayuda a leer la salida)
- Precios con str.tostring(v, format.mintick), NO con un número fijo de decimales: un "#.##"
  sobre un par de 5 decimales redondea a cero y parece un mercado plano
- Porcentajes y osciladores con "#.##"
- Lo que salga na() va como "?", nunca como 0
- position.top_right, legible
- Hazlo end-to-end con las tools del MCP: pine_new/pine_set_source → pine_smart_compile →
  si hay errores pine_get_errors y corrige → pine_save → añádelo al gráfico y déjalo VISIBLE
- Verifica con data_get_pine_tables y pégame la salida
```

**Dos cosas que van a pasar y no son fallos.** El editor Pine tiene que estar abierto o `pine_new`
responde `Could not open Pine Editor`: se abre con `ui_open_panel` → `pine-editor`. Y al guardar un
script nuevo, TradingView abre un diálogo pidiendo nombre; hasta que no se escribe y se pulsa
Guardar, el script no existe y `pine_list_scripts` no lo muestra. Si el campo ya traía texto, el
nombre sale duplicado — se arregla renombrando, y en todo caso el `study_filter` usa el título que
va dentro de `indicator(...)`, no el nombre con el que se guardó.

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

## Si piensas seguir al `03`, lee esto antes

La tabla que sale del prompt de arriba **no llena todo lo que la skill del `03` escribe**. Su CSV
tiene 26 columnas, y de ahí salen unas 15. Las que faltan —`score_tf`, `veredicto`,
`score_ponderado_pct`, `motivo`, `precio_ref` y los niveles `largo_sl`, `largo_tp`, `corto_sl`,
`corto_tp`— vienen de un indicador con lógica de señal propia, **que no está en este repo** y que
el prompt de arriba no reconstruye.

No es un fallo: el `03` está pensado para montarse encima del indicador que ya uses. Si no tienes
uno que dé veredicto y niveles, tienes dos salidas honestas:

- **Dejar esas columnas como `?`.** El pipeline corre igual: `ver_ind` y `score_ind` son
  opcionales en el constructor del Excel, y la hoja de veredictos sale con el tuyo. Es la regla
  nº1 de la skill —lo que no se lee no se inventa— aplicada a su propio esquema.
- **Añadir tus propias filas de señal a la tabla Pine.** Si tu lógica cabe en Pine, cabe en la
  tabla, y entonces sí se llenan.

Lo que no hay que hacer es rellenarlas con algo plausible para que el Excel quede bonito.

---

## Antes de seguir

Comprueba que tienes esto funcionando:

```
Léeme la tabla de mi indicador y dime el RSI de las tres temporalidades.
```

Si Claude te devuelve números exactos, ya tienes lo esencial. Lo del [`03`](../03-skill-analista/)
es automatizar el ciclo completo encima de esta base.
