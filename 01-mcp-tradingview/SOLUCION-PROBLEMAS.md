# Solución de problemas

Ordenado por frecuencia real, no por gravedad.

---

## `cdp_connected: false`

**El 90% de los problemas.** TradingView está abierto, pero sin el puerto de depuración.

Casi siempre es lo mismo: **ya había una instancia corriendo**. Windows y macOS reusan el proceso
existente e ignoran los parámetros nuevos, así que el script "funciona" pero no sirve de nada.

1. Cierra TradingView **del todo**, incluido el icono de la bandeja del sistema
   (Windows: mira la flechita junto al reloj; macOS: `Cmd+Q`, no la X)
2. Comprueba que no queda ningún proceso:
   ```powershell
   Get-Process *trading* -ErrorAction SilentlyContinue
   ```
3. Vuelve a lanzarlo con el script
4. Verifica el puerto: abre `http://127.0.0.1:9222/json/version`

---

## "TradingView Desktop no está instalado (MSIX no encontrado)"

El script busca el paquete con `Get-AppxPackage *TradingView*`. Sale esto si:

- **Lo instalaste con un `.exe` normal, no desde la Store.** Entonces no es MSIX y no hace falta el
  truco: lanza el ejecutable directamente con `--remote-debugging-port=9222`. Búscalo en
  `%LOCALAPPDATA%\Programs\` o en `C:\Program Files\`.
- **Tienes la web, no la app.** El puente necesita la aplicación de escritorio. No hay forma de
  hacerlo con `tradingview.com` en el navegador.
- **Está instalado en otra cuenta de Windows.** `Get-AppxPackage` solo ve los paquetes de tu usuario.

Comprueba qué tienes:
```powershell
Get-AppxPackage *TradingView* | Select-Object Name, Version, InstallLocation
```

---

## "CDP no respondió en 30s"

TradingView abrió pero tardó más de la cuenta. Suele ser el primer arranque del día o tras una
actualización. Espera a que cargue el gráfico del todo y vuelve a correr el script: como es
idempotente, si el puerto ya está vivo te lo dirá y no abrirá nada.

Si nunca responde, prueba a mano y mira si la app se queja de algo:
```powershell
& (Join-Path (Get-AppxPackage *TradingView*).InstallLocation 'TradingView.exe') --remote-debugging-port=9222
```

---

## Los valores del indicador salen vacíos

Dos causas, y conviene distinguirlas:

**El indicador no está visible en el gráfico.** Las herramientas de lectura solo ven lo que está
pintado. Un indicador oculto (ojo tachado) o quitado no devuelve nada.

**El indicador vive en un subpanel.** `data_get_study_values` solo devuelve los del panel principal.
RSI, MACD, ATR y compañía no aparecen aunque estén visibles. **No es un fallo** — es la limitación
que resuelve el [`02-leer-datos/`](../02-leer-datos/).

---

## Los precios no corresponden al símbolo que pedí

Cambiaste de símbolo y leíste demasiado rápido: el gráfico aún no había recargado y devolvió los
datos del anterior.

`chart_set_symbol` responde `chart_ready: false` — eso es normal, no es error. Pero **verifica
siempre que los valores tengan sentido para el instrumento nuevo** antes de usarlos. Si pediste
USDJPY y ves `1.15`, esa lectura es del par anterior: vuelve a leer.

Es el error más silencioso de todos, porque no falla nada — solo te da datos equivocados.

---

## `PermissionError` al guardar el Excel

Lo tienes abierto en Excel, que bloquea el fichero. El script de la skill lo detecta, guarda una
copia con sufijo de hora y te avisa; no se pierde nada. Cierra Excel y repite.

---

## `ModuleNotFoundError: openpyxl`

```bash
pip install openpyxl
```

Solo hace falta para la skill del `03`. Los pasos `01` y `02` no usan Python.

---

## Claude no ve las herramientas del MCP

```bash
claude mcp list
```

- Si `tradingview` no aparece → no quedó registrado, repite el `claude mcp add`
- Si aparece pero falla → comprueba que la ruta al `server.js` existe y que corriste `npm install`
- Reinicia Claude Code después de registrarlo

En algunas configuraciones las herramientas se cargan bajo demanda: si Claude dice que no las tiene,
pídele explícitamente que **busque las herramientas de TradingView** antes de usarlas.

---

## Sigue sin funcionar

Pásale este repo a Claude y cuéntale qué pasó:

> Estoy siguiendo el `01-mcp-tradingview` y me pasa esto: [pega el error].
> Mira `SOLUCION-PROBLEMAS.md` y ayúdame a diagnosticarlo.

Dale la salida real del comando, no tu resumen de lo que pasó. La diferencia entre
"no funciona" y el mensaje literal es la mitad del diagnóstico.
