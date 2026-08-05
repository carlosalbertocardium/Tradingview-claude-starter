# Contrato del JSON para `construir_entregables.py`

El script no analiza nada: da formato. Toda la interpretación va escrita en este JSON.
Guárdalo en un temporal de la sesión, no en la carpeta de trabajo del usuario.

```json
{
  "base": "C:/Users/TU_USUARIO/OneDrive/Documentos/Mi analista grafico",
  "fecha": "2026-08-04",
  "hora": "22:58 hora local (00:01 UTC-4 en el grafico)",
  "tema": "MAJORS",
  "titulo": "Analisis grafico y tecnico - 7 majors de forex",
  "fuente": "TradingView feed FX/FXCM",
  "velas": 120,

  "instrumentos": [
    {
      "instrumento": "USDJPY",
      "simbolo": "FX:USDJPY",
      "decimales": 3,

      "close": 157.407,
      "high120": 163.987,
      "low120": 153.994,
      "chg120": 1.71,
      "rsi_d": 28.3,
      "rsi_60": 44.2,
      "atr240": 0.793,
      "estructura_d": "Mixto / bajo EMA200",

      "ver_ind": "VENDER",
      "score_ind": -62.50,

      "ver_mio": "ESPERAR",
      "confianza": "Alta",
      "tesis": "Una frase densa: qué ve el indicador, qué ves tú, por qué difieren.",
      "condicion": "Qué tendría que pasar para cambiar el veredicto.",
      "invalidacion": "Qué nivel rompe la tesis.",

      "soporte": 155.226,
      "resistencia": 160.879,
      "zona_compra": "155,2 con vela de giro",
      "zona_venta": "159,5 - 160,0",

      "lectura_dato": "Una línea para la hoja Técnico: qué dice la posición en el rango.",

      "estructura_txt": "Párrafo de análisis gráfico: máximos, mínimos, roturas, volumen.",
      "numeros_txt": "Cierre X · rango 120d A-B · posicion N% · var 120d ±X% · RSI D … ",
      "interp_txt": "Párrafo de interpretación. Aquí va el desacuerdo con el indicador.",

      "captura": "imagenes/USDJPY/2026-08-04/USDJPY_MTF_2026-08-04_2258.png"
    }
  ],

  "conjunto": [
    "1. Frase de lectura transversal (correlaciones, tema único, sesgo de conjunto).",
    "2. Otra."
  ],

  "avisos": [
    ["METODO", ""],
    ["Fuente de precio", "…"],
    ["", ""],
    ["AVISOS DE CALIDAD", ""],
    ["MACD inservible en FX", "…"],
    ["Tamano de posicion mal", "…"]
  ]
}
```

## Notas

- **Orden de `instrumentos`** = orden en el Excel. Pon primero el más accionable.
- `instrumento` es el nombre **limpio** (carpetas y ficheros); `simbolo` el de TradingView con
  prefijo de mercado. Si omites `simbolo`, la ficha usa `instrumento`.
- `decimales`: cuántos usa el activo. 5 en forex normal, 3 en pares con JPY, 2 en acciones,
  índices y cripto de precio alto, hasta 8 en cripto barata. **Pásalo siempre**: si falta, el
  script lo deduce del precio y acierta en forex, pero es una red de seguridad, no un sustituto.
- `ver_ind` / `ver_mio` deben ser `COMPRAR`, `VENDER` o `ESPERAR` — el script les da color.
- `score_ind` es el número que dé tu indicador (`score ponderado` o equivalente), con signo.
- `chg120`, `rsi_*` van como número, no como texto con `%`.
- En `avisos`, una fila con el segundo campo vacío se pinta como cabecera de sección.
- **Sin acentos ni caracteres raros en los textos que van al Excel**: openpyxl los admite, pero
  la consola de Windows en cp1252 rompe al imprimir el resultado. Escribe «analisis», no
  «análisis», dentro del JSON. En los Markdown de la bitácora sí se usan acentos normales.
