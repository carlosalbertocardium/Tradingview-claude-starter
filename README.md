# TradingView + Claude — kit de arranque

**Conecta Claude a tu TradingView y automatiza tu análisis técnico.**

> **Esta es una copia con correcciones.** El kit original es de
> [Juan Camilo Rico (@Jumilo098)](https://github.com/Jumilo098/tradingview-claude-starter), MIT.
> Aquí se probó entero el 2026-11-11 sobre BTCUSDT y ETHUSDT y se corrigió lo que falló por el
> camino: un bug que hacía medir 20 días donde decía 120, una afirmación sobre el MCP que ya no
> es cierta, y tres promesas de la documentación que no se sostenían. El detalle está en el
> commit «Corregir lo que fallo al probar el kit de punta a punta».
> Si buscas la versión del autor, ve al repo original.

Tres piezas que puedes tomar por separado o montar enteras:

1. **La conexión** — que Claude vea tu gráfico en vivo (precios, indicadores, capturas)
2. **La lectura** — cómo sacar valores exactos como *texto*, no como imagen
3. **El analista** — una skill que va de los gráficos a un Excel con veredicto, sola

---

## Empieza aquí

**¿Tienes Claude Code?** Dale esta URL y pídele que te lo monte:

```
https://github.com/Jumilo098/tradingview-claude-starter

Clona este repo y ayúdame a montarlo en mi computadora.
```

El repo trae un `CLAUDE.md` con instrucciones para que Claude te pregunte en qué punto estás
y te guíe paso a paso. **No tienes que entender nada de antemano.**

**¿Prefieres a mano?** → [`EMPIEZA-AQUI.md`](EMPIEZA-AQUI.md)

---

## Qué vas a poder hacer

Cuando termines, le vas a poder decir a Claude cosas como:

```
analiza el oro y la plata
analiza Tesla, Nvidia y AMD
analiza mi watchlist
¿qué ves en el gráfico que tengo abierto?
```

Y Claude va a: cambiar de símbolo, leer los valores exactos de tus indicadores, capturar la
pantalla, sacar el histórico, mirar los gráficos, y entregarte un Excel con su veredicto
razonado por instrumento. Sin que estés encima.

---

## Contenido

| Carpeta | Qué hay | ¿Obligatorio? |
|---|---|---|
| [`01-mcp-tradingview/`](01-mcp-tradingview/) | Conectar Claude a TradingView + script de un clic | ✅ Sí |
| [`02-leer-datos/`](02-leer-datos/) | Qué expone el MCP, y el truco para leer *cualquier* indicador | ✅ Sí |
| [`03-skill-analista/`](03-skill-analista/) | La skill completa + ejemplo real | Opcional |
| [`04-permisos/`](04-permisos/) | Que deje de pedirte permiso a cada paso | Opcional |

Cada carpeta funciona sola. Si solo quieres que Claude lea tus gráficos, con `01` y `02` sobra.

---

## Requisitos

- **TradingView Desktop** (la app, no la web — el puente necesita el proceso local)
- **Claude Code**
- **Node.js** (para el MCP) y **Python 3** con `openpyxl` (solo si usas la skill del `03`)
- Windows, Mac o Linux. El script de un clic es de Windows; en Mac/Linux se explica el equivalente.

No necesitas cuenta de pago de TradingView. Sí necesitas que los datos que quieres leer se vean
en tu gráfico.

---

## Las tres ideas que vale la pena robarse

Aunque nunca uses la skill, esto es lo transferible:

**1. TradingView Desktop se puede abrir en modo depuración y hablarle desde fuera.**
Es una app Electron. Lanzada con `--remote-debugging-port=9222` expone un puerto por el que un
programa puede leer y controlar el gráfico. Ahí es donde se engancha el MCP.

**2. Si leer un indicador te sale caro o incompleto, haz que lo dibuje en una tabla.**
Leer los indicadores uno a uno te da **una sola temporalidad**, los números con el locale de la
app (`35,40`, con signo menos Unicode) y unos 8.000 tokens de código ofuscado por respuesta. La
solución no es pelearse con el MCP: es escribir un indicador Pine de diez líneas que vuelque los
valores en un `table.new`, que se lee como texto limpio, con las tres temporalidades de una vez y
por ~200 tokens. Con eso, **cualquier cosa que puedas calcular en Pine se vuelve legible por
Claude.** Está en el `02`.

**3. Lee números como texto, no como imágenes.**
Una captura son 1–2k tokens y encima Claude puede leer mal un dígito. Los mismos datos como texto
son ~200 tokens y son exactos. La captura se usa para *ver estructura* (dónde están los máximos,
si hubo una rotura), no para *leer valores*.

---

## Aviso

Esto **no es asesoría de inversión ni un sistema probado**. Es una herramienta de lectura de
gráficos. El ejemplo del `03` es material didáctico fechado, no una señal para operar. Ningún
veredicto que produce tiene backtest ni expectativa medida detrás — antes de operar cualquier cosa
que salga de aquí, mídela.

## Créditos

El puente con TradingView es el proyecto **[tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)**
de [tradesdontlie](https://github.com/tradesdontlie), licencia MIT. **No está copiado en este repo:**
se clona del original para que recibas sus actualizaciones. Todo el mérito de esa pieza es suyo.

Este kit (los scripts de arranque, la skill, la documentación) es obra de **Juan Camilo Rico**
([@Jumilo098](https://github.com/Jumilo098)) y es MIT — ver [LICENSE](LICENSE), que se mantiene
intacta. Este repositorio es una copia suya con correcciones, no un trabajo propio: el mérito del
diseño es de él, y los fallos corregidos solo salieron a la luz porque el kit era lo bastante
bueno como para probarlo entero.

No está afiliado a TradingView Inc. ni a Anthropic.
