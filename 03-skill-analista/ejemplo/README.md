# ⚠ Ejemplo didáctico — NO es una recomendación

Salida real de la skill sobre los 7 pares mayores de forex, **4 de agosto de 2026, 22:58**.

Está aquí para que veas **la forma del entregable** antes de instalar nada. Los precios llevan
meses caducados y los veredictos no valen para hoy ni valían para mañana. **No operes nada de
esto.** No tiene backtest ni expectativa medida detrás.

Las capturas de pantalla originales no se incluyen (eran de una sesión personal de TradingView).
En tu instalación irían en `imagenes/<INSTRUMENTO>/<FECHA>/`.

---

## Qué hay

| Fichero | Qué es |
|---|---|
| `EJEMPLO_ANALISIS_MAJORS.xlsx` | El entregable principal, 4 hojas |
| `EJEMPLO_ficha_USDJPY.md` | Una ficha por instrumento |
| `EJEMPLO_lecturas_mtf.csv` | Los datos crudos, una fila por instrumento y temporalidad |

---

## Lo interesante del ejemplo

En este barrido, **el veredicto propio contradijo al indicador en 4 de 7 casos**. Esa es la lección
del módulo entero: la herramienta no está para obedecer al indicador, sino para darte con qué
discutirle.

Tres desacuerdos, y por qué:

**El indicador daba COMPRAR en tres pares a la vez.** Pero los tres eran pares con el dólar de
cotizada: no eran tres oportunidades, era **una sola apuesta al dólar repetida tres veces**. Y al
mirar los 120 días, esa apuesta iba *en contra* de cuatro meses de dólar fuerte. Lo que parecía
alineación era un rebote contratendencia.

**El par con el score más alto (+83%) era la peor entrada.** Llevaba 120 días plano y el precio
estaba al 61% de un rango de cuatro meses. El score venía de tener las medias alineadas — que es lo
que hacen las medias en mitad de un rango.

**El único VENDER llegaba tarde.** El par había caído un 5% en tres sesiones con volumen 3,7× la
media y el RSI diario en 28. El movimiento ya había ocurrido; vender ahí era perseguir.

Ninguna de esas tres cosas se ve en la tabla del indicador. Las tres salen de mirar el gráfico y de
cruzarlo con el rango de 120 días.

---

## Cómo leer el Excel

- **Veredictos** — la tabla principal. Fíjate en las columnas *Tesis* y *Qué lo cambiaría*: un
  veredicto sin condición de cambio es una opinión, no un plan.
- **Técnico** — la base cuantitativa. La columna *Posición en rango* va coloreada: verde bajo 40%,
  rojo sobre 70%. Comprar en rojo o vender en verde es pagar el peor precio disponible.
- **Niveles** — soportes, resistencias e invalidación por instrumento.
- **Método y avisos** — cómo se hizo y **de qué no fiarse**. Es la hoja que la mayoría de informes
  no trae y la que más se debería leer.
