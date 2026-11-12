# 03 · La skill del analista

Una skill de Claude Code que va de los gráficos a un Excel con veredicto, sin supervisión.

> **Este módulo es opcional.** Si con el `01` y el `02` ya consigues lo que querías, puedes parar
> ahí. Esto es el ejemplo completo de hasta dónde se puede llevar.

---

## Qué hace

```
"analiza el complejo del uranio"
        ↓
resuelve los símbolos → barre uno a uno → archiva capturas → extrae a CSV
        ↓
mira los gráficos → cruza con 120 velas diarias → decide
        ↓
Excel de 4 hojas + ficha por instrumento + entrada de bitácora
```

Sin pedirte confirmación en medio. Si algo la bloquea, te manda una notificación y sigue con el
resto en vez de quedarse esperando a que vuelvas.

---

## Instalar

**1.** Copia la carpeta `analista/` a tus skills de Claude Code:

```bash
cp -r ./analista ~/.claude/skills/analista          # macOS / Linux
```
```powershell
Copy-Item .\analista "$env:USERPROFILE\.claude\skills\analista" -Recurse   # Windows
```

**2.** Dependencia:

```bash
pip install openpyxl
```

**3.** Crea la carpeta de trabajo:

```bash
python ~/.claude/skills/analista/scripts/preparar.py
```

Te dirá dónde la creó. Para ponerla en otro sitio, define `ANALISTA_BASE`.

**4.** Abre `analista/SKILL.md` y **pon el nombre de tu indicador** donde dice `NOMBRE_INDICADOR`.
La skill lee una tabla multitemporal; si no tienes una, créala con el prompt del
[`02-leer-datos`](../02-leer-datos/).

**5.** Comprueba que Claude la ve: escribe `/` y busca `analista`.

---

## Usar

```
/analista majors
/analista Tesla, Nvidia y AMD
/analista mi watchlist
analiza el oro y la plata
```

O en lenguaje normal. La skill resuelve los símbolos sola: si dices "el oro", los busca y te dice
cuál eligió.

### Qué produce

| Fichero | Qué lleva |
|---|---|
| `analisis/ANALISIS_<TEMA>_<FECHA>.xlsx` | **Veredictos** (tesis + qué lo cambiaría) · **Técnico** (rangos, RSI, ATR, posición en rango) · **Niveles** (soportes, resistencias, invalidación) · **Método y avisos** |
| `analisis/<INS>/<FECHA>/<INS>_analisis_<FECHA>.md` | Ficha por instrumento: observado / interpretado / veredicto |
| `datos/lecturas_mtf.csv` | Una fila por instrumento y temporalidad. Para calcular. |
| `datos/BITACORA.md` | La lectura en prosa, fechada, con la captura que la respalda |

En [`ejemplo/`](ejemplo/) tienes una salida real para ver la pinta antes de instalar nada.

---

## Las decisiones de diseño (esto es lo que vale la pena copiar)

Aunque no uses esta skill, estas cinco ideas se aplican a cualquier automatización parecida.

**1. Separar lo que se lee de lo que se concluye.** `datos/` guarda lo extraído; `analisis/` lo
interpretado. Si mañana el veredicto resulta malo, los datos siguen sirviendo. Mezclarlos hace que
un error de juicio contamine el histórico.

**2. Observado ≠ interpretado.** En cada ficha van en campos distintos. Dentro de tres meses no vas
a recordar qué leíste en el gráfico y qué dedujiste tú — y esa diferencia es todo.

**3. Nunca inventar un dato.** Lo que no se lee va como `?`. Un hueco visible es información; un
hueco rellenado con una estimación plausible es una mentira que no se puede detectar después.

**4. Crear carpetas y mover ficheros pasa por dos scripts.** No es manía de orden: así no hace
falta concederle permiso de mover ficheros por todo el disco, sino de ejecutar *esos dos scripts
concretos*. El CSV y la bitácora sí se escriben directo, así que además hacen falta `Write` y
`Edit` **acotados a la carpeta de trabajo** — cuatro entradas en total, todas explicables. La idea
es diseñar para el permiso mínimo, no que la lista sea corta a costa de mentir sobre lo que hace.

**5. El rango de 120 días — medido en diario.** Es lo que separa un análisis de una foto. Un
indicador te dice que algo está alcista *ahora*; el rango te dice si eso es una tendencia o un
rebote dentro de una caída de cuatro meses. Sin ese contexto, todas las señales parecen igual de
buenas.

Con una trampa que costó encontrar: `data_get_ohlcv` lee la temporalidad **del gráfico**. Si no
la fijas a diario antes de pedirla, con el gráfico en 4H mides 20 días creyendo que mides 120, sin
ningún aviso. En BTCUSDT, el mismo instante daba −9,55% de variación leyendo 4H y +13,95% leyendo
diario: signo opuesto. La skill fija la temporalidad en la Fase 2 por esto.

---

## No te fíes de tu indicador

La skill trae una sección para **auditar el indicador que uses**. Salió de encontrar tres defectos
reales en uno que parecía perfecto:

- una columna que siempre valía `0` por un error de formato (y que además entraba en el «score»)
- una fila de tamaño de posición equivocada por un factor de 100.000
- la tabla devolviendo el cierre de *ayer* como si fuera el de hoy

Ninguno fallaba ruidosamente. Los tres devolvían números plausibles. **Verifica los cálculos de tu
indicador con un ejemplo hecho a mano antes de construir nada encima**, y cruza siempre el precio
de la tabla contra el OHLCV.

---

## Aviso

El ejemplo incluido es **material didáctico fechado**, no una señal para operar. Ningún veredicto
que produce esta skill tiene backtest ni expectativa medida detrás: son lecturas de gráficos
razonadas y trazables, que es otra cosa. Antes de operar con esto, mide si tiene ventaja real.
