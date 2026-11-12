# 01 · Conectar Claude a TradingView

Al terminar este paso, Claude podrá leer y controlar tu gráfico en vivo.

## Cómo funciona

TradingView Desktop es una app **Electron** (Chrome por dentro). Si la lanzas con el parámetro
`--remote-debugging-port=9222`, abre un puerto local por el que otro programa puede inspeccionarla
y controlarla. Es el **Chrome DevTools Protocol (CDP)**, la misma tecnología con la que se depuran
páginas web.

```
Claude Code  ←→  MCP (Node)  ←→  CDP :9222  ←→  TradingView Desktop
```

El MCP es el traductor: convierte "dame el RSI" en instrucciones que la app entiende.

**Es local.** No sale nada a internet, no hay API key, no hay cuenta de terceros. Si cierras
TradingView, se acabó la conexión.

---

## Paso 1 · Instalar el MCP

El puente es **[tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)** de
tradesdontlie (MIT). Lo clonas del original:

```bash
cd ~
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
npm install
```

Y lo registras en Claude Code:

```bash
claude mcp add tradingview -- node ~/tradingview-mcp/src/server.js
```

En Windows, con la ruta completa:

```powershell
claude mcp add tradingview -- node "$env:USERPROFILE\tradingview-mcp\src\server.js"
```

Comprueba:

```bash
claude mcp list
```

Debe aparecer `tradingview`. **No lleva API key ni variables de entorno** — si algo te pide una
credencial para esto, algo va mal.

---

## Paso 2 · Lanzar TradingView con el puerto abierto

Aquí está el problema que este repo te ahorra.

### El problema

Si instalaste TradingView Desktop desde la Microsoft Store, se instala como paquete **MSIX** y el
ejecutable acaba en `C:\Program Files\WindowsApps\TradingView.Desktop_…\TradingView.exe` — una
carpeta **oculta y protegida** por el sistema. La herramienta `tv_launch` del MCP busca en las rutas
normales, no lo encuentra, y falla sin explicar por qué.

### La solución

`launch_tradingview_cdp.ps1` resuelve la ruta real preguntándole a Windows por el paquete instalado
(`Get-AppxPackage *TradingView*`) y lanza el ejecutable con el puerto de depuración.

**Doble clic en `launch_tradingview_cdp.cmd`.** Eso es todo.

Además el script:
- Comprueba primero si el puerto ya está activo (si sí, no abre nada — es idempotente)
- Espera hasta 30 segundos a que responda y te dice si lo logró
- Devuelve código de salida `0` si todo bien, `1` si TradingView no está instalado, `2` si no respondió

Cópialos donde quieras y créate un acceso directo en el escritorio.

### A mano (si prefieres, o si el script falla)

**Windows:**
```powershell
& (Join-Path (Get-AppxPackage *TradingView*).InstallLocation 'TradingView.exe') --remote-debugging-port=9222
```

**macOS:**
```bash
open -a "TradingView" --args --remote-debugging-port=9222
```

**Linux:**
```bash
tradingview --remote-debugging-port=9222
```

⚠ **Importante:** TradingView tiene que estar **cerrado del todo** antes. Si ya hay una instancia
abierta, el sistema reusa esa —sin el puerto— y el script parece funcionar pero no sirve.
Cierra también el icono de la bandeja del sistema.

---

## Paso 3 · Verificar

En Claude:

```
Comprueba la conexión con TradingView.
```

Claude llamará a `tv_health_check`. Lo que buscas:

```json
{ "cdp_connected": true, "chart_symbol": "...", "api_available": true }
```

Si sale `cdp_connected: false` → TradingView no está corriendo con el puerto.
Vuelve al paso 2 y asegúrate de que estaba **cerrado** antes de lanzarlo.

Comprobación directa desde el navegador o la terminal — si esto responde, el puerto está vivo:

```
http://127.0.0.1:9222/json/version
```

---

## Qué puedes hacer ya

Sin nada más instalado:

```
¿Qué símbolo tengo abierto y qué indicadores tiene el gráfico?
Dame el precio actual y el resumen de las últimas 100 velas diarias.
Cámbiame el gráfico a EURUSD en 4 horas.
Tómame una captura del gráfico.
```

Para leer varios indicadores y varias temporalidades de una vez, en texto exacto y barato, sigue al
[`02-leer-datos/`](../02-leer-datos/) — ahí está el truco.

---

## Seguridad

- El puerto `9222` queda abierto **en tu máquina** mientras TradingView corra así. Cualquier
  programa local puede hablarle. En tu equipo personal es equivalente a tener el navegador abierto;
  en una máquina compartida, ciérralo cuando termines (basta cerrar TradingView).
- El MCP puede **modificar** tu gráfico: cambiar símbolo, añadir indicadores, crear y guardar
  scripts Pine. Si eso te incomoda, en el paso [`04`](../04-permisos/) puedes autorizar solo las
  herramientas de lectura.
- Nada de esto toca tu cuenta de TradingView ni tu broker. No hay órdenes de por medio.
