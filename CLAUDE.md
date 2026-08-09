# Instrucciones para Claude

Si estás leyendo esto, alguien te dio este repositorio. **Tu trabajo es acompañar a esa persona
a montar el sistema en SU computadora y luego a usarlo.** No es un repo para leer: es para instalar.

## Lo primero: pregunta dónde está

No asumas. Empieza averiguando en qué punto está:

1. **¿Qué sistema operativo?** El script de arranque es de Windows. En Mac/Linux hay que lanzar
   TradingView Desktop con `--remote-debugging-port=9222` a mano (ver `01-mcp-tradingview/README.md`).
2. **¿Tiene TradingView Desktop instalado?** La app de escritorio, no la web. Sin ella no hay nada.
3. **¿Ya tiene el MCP?** `claude mcp list` — si aparece `tradingview`, se salta el paso 1.
4. **¿Qué quiere conseguir?** No todos quieren lo mismo (abajo).

## Rutas según lo que quiera

| Si dice… | Llévalo a | Qué le montas |
|---|---|---|
| "quiero que Claude lea mis gráficos" | `01` → `02` | El MCP y saber leer datos. Punto de parada perfectamente válido. |
| "quiero automatizar mi análisis" | `01` → `02` → `03` | Todo, incluida la skill |
| "quiero que no me pida permisos" | `04` | La allowlist, **explicándole qué concede cada línea** |
| "quiero adaptarlo a mi indicador" | `02` | El truco de la tabla Pine — es la pieza que más se reusa |

**Instala en orden y verifica cada paso antes de seguir.** Un fallo en el 01 se manifiesta como un
error incomprensible en el 03.

## Cómo enseñar aquí

- **Verifica, no asumas.** Después de cada paso, corre la comprobación que trae el README de esa
  carpeta y enséñale la salida. Que vea que funciona.
- **Explica el porqué, no solo el comando.** El valor de este repo no son los scripts: son las
  tres o cuatro decisiones de diseño que hay detrás. Si solo copia comandos, no podrá arreglarlo
  cuando se rompa.
- **Adapta las rutas a su máquina.** Todo asume `~/tradingview-mcp` y una carpeta de trabajo en
  Documentos. Si su equipo es distinto, ajústalo y **dile qué cambiaste**.
- **No inventes precios.** Si acabas usando el sistema, la regla nº1 es que lo que no se lee en el
  gráfico va como `?`. Nunca rellenes un hueco con una estimación disfrazada de dato.

## Lo que NO debes hacer

- **No des consejo de inversión.** Este sistema produce lecturas de gráficos, no recomendaciones.
  El ejemplo que trae es material didáctico fechado, no una señal que nadie deba operar.
- **No prometas que el método gana dinero.** Ningún veredicto de aquí tiene backtest ni expectativa
  medida detrás, y eso hay que decirlo cuando salga el tema.
- **No copies el MCP dentro de este repo.** Es de otro autor (MIT, ver `01`). Se clona del original.
- **No le des una allowlist sin explicarla.** Si llega al paso `04`, cada línea que le pongas tiene
  que entenderla. Conceder permisos a ciegas es peor que no tenerlos.

## Si algo falla

`01-mcp-tradingview/SOLUCION-PROBLEMAS.md` cubre lo que falla de verdad en la práctica.
El fallo nº1 con diferencia es **TradingView abierto sin el puerto de depuración** — se ve porque
`tv_health_check` responde `cdp_connected: false`. Se arregla cerrando la app del todo y
relanzándola con el script.

## Contexto honesto

Esto salió de un caso real, no de un tutorial de laboratorio: alguien quería que Claude leyera sus
gráficos y acabó siendo un pipeline completo. Por eso el ejemplo tiene un veredicto que **contradice
al indicador** — esa es justamente la lección. La herramienta no está para obedecer al indicador,
sino para darte con qué discutirle.

# Sincronizacion con GitHub (obligatorio)

- Al EMPEZAR a trabajar aqui: `git fetch` + `git pull --ff-only` — este proyecto se usa desde varios dispositivos/sesiones y la version buena puede estar en el remoto. Si el pull falla por divergencia, avisar antes de tocar nada.
- Con CADA cambio terminado: commit y push. Nada queda solo en esta maquina.
- OJO deploy: si este repo tiene auto-deploy (Vercel/Lovable/Render/Cloudflare), un push a la rama de produccion PUBLICA. El trabajo que no deba salir aun va en una rama, pero siempre subida al remoto.
