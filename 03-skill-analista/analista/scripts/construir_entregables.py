# -*- coding: utf-8 -*-
"""Construye los entregables del analista grafico a partir de un JSON.

Uso:  python construir_entregables.py <ruta_al_json>

El JSON lo escribe Claude durante el barrido. Este script NO analiza nada:
solo da formato. Toda la interpretacion vive en el JSON.

Contrato del JSON: ver CONTRATO_JSON.md en la carpeta de la skill.
"""
from __future__ import print_function
import io
import json
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------- estilos
AZUL = PatternFill('solid', fgColor='1F3864')
VERDE = PatternFill('solid', fgColor='C6EFCE')
ROJO = PatternFill('solid', fgColor='FFC7CE')
AMAR = PatternFill('solid', fgColor='FFEB9C')
HDR = Font(bold=True, color='FFFFFF', size=11)
BOLD = Font(bold=True)
WRAP = Alignment(wrap_text=True, vertical='top')
CENTER = Alignment(horizontal='center', vertical='center')
THIN = Border(*[Side(style='thin', color='BFBFBF')] * 4)
FILL_VER = {'COMPRAR': VERDE, 'VENDER': ROJO, 'ESPERAR': AMAR}


def cabecera(ws, cols, widths, fila=1):
    for i, (c, w) in enumerate(zip(cols, widths), start=1):
        cell = ws.cell(row=fila, column=i, value=c)
        cell.fill, cell.font, cell.alignment, cell.border = AZUL, HDR, CENTER, THIN
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[fila].height = 30


def pos_rango(h, l, c):
    if h == l:
        return 50.0
    return round((c - l) / float(h - l) * 100, 1)


def fmt_de(dec):
    dec = int(dec)
    return '0' if dec <= 0 else '0.' + '0' * dec


def decimales_de(it):
    """Decimales del instrumento. Se pasan en el JSON; esto es solo la red de seguridad
    para cuando no vienen: sirve para forex y es razonable en el resto."""
    if it.get('decimales') is not None:
        return int(it['decimales'])
    c = abs(float(it.get('close') or 0))
    if c == 0:
        return 2
    if c < 10:        # EURUSD 1,15 · AUDUSD 0,70
        return 5
    if c < 1000:      # USDJPY 157 · acciones · indices
        return 3
    return 2          # BTC, indices grandes


# ---------------------------------------------------------------- excel
def construir_excel(cfg, salida):
    ins = cfg['instrumentos']
    fecha, hora, tema = cfg['fecha'], cfg.get('hora', ''), cfg.get('tema', 'ANALISIS')
    wb = Workbook()

    # ---- hoja Veredictos
    ws = wb.active
    ws.title = 'Veredictos'
    ws['A1'] = cfg.get('titulo', 'Analisis grafico y tecnico')
    ws['A1'].font = Font(bold=True, size=14)
    ws['A2'] = ('Fecha: %s %s  ·  Fuente: %s  ·  Veredicto propio, no del indicador'
                % (fecha, hora, cfg.get('fuente', 'TradingView')))
    ws['A2'].font = Font(italic=True, size=9, color='595959')

    cabecera(ws, ['Instrumento', 'Veredicto\nindicador', 'Score\nindicador %',
                  'VEREDICTO\nPROPIO', 'Confianza', 'Tesis (analisis grafico y tecnico)',
                  'Que lo cambiaria', 'Captura'],
             [13, 12, 12, 13, 10, 62, 46, 46], fila=4)

    r = 5
    for it in ins:
        ws.cell(row=r, column=1, value=it['instrumento']).font = BOLD
        c2 = ws.cell(row=r, column=2, value=it.get('ver_ind', '-'))
        if it.get('ver_ind') in FILL_VER:
            c2.fill = FILL_VER[it['ver_ind']]
        ws.cell(row=r, column=3, value=it.get('score_ind')).number_format = '+0.0;-0.0'
        cm = ws.cell(row=r, column=4, value=it['ver_mio'])
        cm.fill, cm.font = FILL_VER.get(it['ver_mio'], AMAR), BOLD
        ws.cell(row=r, column=5, value=it.get('confianza', ''))
        ws.cell(row=r, column=6, value=it.get('tesis', ''))
        ws.cell(row=r, column=7, value=it.get('condicion', ''))
        ws.cell(row=r, column=8, value=it.get('captura', ''))
        for col in range(1, 9):
            cell = ws.cell(row=r, column=col)
            cell.border = THIN
            cell.alignment = WRAP if col in (6, 7, 8) else CENTER
        ws.row_dimensions[r].height = 74
        r += 1

    if cfg.get('conjunto'):
        r += 1
        ws.cell(row=r, column=1, value='LECTURA DE CONJUNTO').font = Font(bold=True, size=12)
        r += 1
        for linea in cfg['conjunto']:
            ws.cell(row=r, column=1, value=linea).alignment = WRAP
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
            ws.row_dimensions[r].height = 32
            r += 1
    ws.freeze_panes = 'A5'

    # ---- hoja Tecnico
    ws2 = wb.create_sheet('Tecnico')
    n = cfg.get('velas', 120)
    ws2['A1'] = 'Base cuantitativa del veredicto (%s velas diarias)' % n
    ws2['A1'].font = Font(bold=True, size=12)
    cabecera(ws2, ['Instrumento', 'Cierre', 'Maximo\n%sd' % n, 'Minimo\n%sd' % n,
                   'Posicion en\nrango %', 'Var %sd\n%%' % n, 'RSI\ndiario', 'RSI\n60 min',
                   'ATR\n240', 'Estructura\ndiaria', 'Stop 1,5xATR\n(240)',
                   'Lectura del dato'],
             [13, 11, 11, 11, 12, 10, 9, 9, 10, 21, 12, 58], fila=3)
    r = 4
    for it in ins:
        dec = decimales_de(it)
        fmt = fmt_de(dec)
        h, l, c = it['high120'], it['low120'], it['close']
        atr = it.get('atr240')
        vals = [it['instrumento'], c, h, l, pos_rango(h, l, c), it.get('chg120'),
                it.get('rsi_d'), it.get('rsi_60'), atr, it.get('estructura_d', ''),
                round(1.5 * atr, dec) if atr else None, it.get('lectura_dato', '')]
        for col, v in enumerate(vals, start=1):
            cell = ws2.cell(row=r, column=col, value=v)
            cell.border = THIN
            if col in (2, 3, 4, 9, 11):
                cell.number_format = fmt
            if col == 5:
                cell.number_format = '0.0"%"'
                cell.fill = VERDE if v < 40 else (ROJO if v > 70 else AMAR)
            if col == 6:
                cell.number_format = '+0.00"%";-0.00"%"'
            cell.alignment = WRAP if col == 12 else CENTER
        ws2.cell(row=r, column=1).font = BOLD
        ws2.row_dimensions[r].height = 30
        r += 1
    r += 1
    nota = ('Posicion en rango: 0% = en el minimo del periodo, 100% = en el maximo. '
            'Verde <40% (zona baja), amarillo 40-70% (medio, sin ventaja), rojo >70% (zona alta).')
    ws2.cell(row=r, column=1, value=nota).font = Font(italic=True, size=9, color='595959')
    ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12)
    ws2.freeze_panes = 'A4'

    # ---- hoja Niveles
    ws3 = wb.create_sheet('Niveles')
    ws3['A1'] = 'Niveles operativos - los mios, no los del indicador'
    ws3['A1'].font = Font(bold=True, size=12)
    cabecera(ws3, ['Instrumento', 'Precio\nactual', 'Soporte\nclave', 'Resistencia\nclave',
                   'Zona de compra\nque yo esperaria', 'Zona de venta\nque yo esperaria',
                   'Invalidacion'],
             [13, 12, 12, 12, 22, 22, 34], fila=3)
    r = 4
    for it in ins:
        dec = decimales_de(it)
        fmt = fmt_de(dec)
        vals = [it['instrumento'], it['close'], it.get('soporte'), it.get('resistencia'),
                it.get('zona_compra', ''), it.get('zona_venta', ''), it.get('invalidacion', '')]
        for col, v in enumerate(vals, start=1):
            cell = ws3.cell(row=r, column=col, value=v)
            cell.border = THIN
            if col in (2, 3, 4):
                cell.number_format = fmt
            cell.alignment = WRAP if col == 7 else CENTER
        ws3.cell(row=r, column=1).font = BOLD
        ws3.row_dimensions[r].height = 30
        r += 1
    ws3.freeze_panes = 'A4'

    # ---- hoja Metodo y avisos
    ws4 = wb.create_sheet('Metodo y avisos')
    ws4['A1'] = 'Como se hizo este analisis y de que NO hay que fiarse'
    ws4['A1'].font = Font(bold=True, size=12)
    ws4.column_dimensions['A'].width = 26
    ws4.column_dimensions['B'].width = 108
    r = 3
    for a, b in cfg.get('avisos', []):
        ca, cb = ws4.cell(row=r, column=1, value=a), ws4.cell(row=r, column=2, value=b)
        if not b:
            ca.font = Font(bold=True, color='FFFFFF')
            ca.fill, cb.fill = AZUL, AZUL
        else:
            ca.font = BOLD
            ca.alignment = cb.alignment = WRAP
            ws4.row_dimensions[r].height = 42
        r += 1

    return guardar_sin_perder(wb, salida)


def guardar_sin_perder(wb, salida):
    """Guarda el libro. Si el fichero esta abierto en Excel y bloqueado, no falla:
    guarda una copia con sufijo de hora y devuelve esa ruta. Nunca se pierde el trabajo."""
    try:
        wb.save(salida)
        return salida
    except (IOError, OSError):
        import time
        raiz, ext = os.path.splitext(salida)
        alt = '%s_%s%s' % (raiz, time.strftime('%H%M'), ext)
        wb.save(alt)
        print('AVISO  el fichero destino estaba bloqueado (abierto en Excel).')
        print('AVISO  guardado como: %s' % os.path.basename(alt))
        return alt


# ---------------------------------------------------------------- fichas
FICHA = u"""# %(ins)s - Analisis grafico y tecnico

**Simbolo:** `%(simbolo)s`
**Fecha:** %(fecha)s %(hora)s
**Captura:** `%(captura)s`
**Datos:** `datos/lecturas_mtf.csv` + %(velas)s velas diarias

## Observado (leido del grafico y del indicador)

### Estructura
%(estructura_txt)s

### Numeros
%(numeros_txt)s

## Interpretado (lectura mia, no dato)

%(interp_txt)s

## VEREDICTO: %(ver_mio)s

**Que lo cambiaria:** %(condicion)s

**Invalidacion:** %(invalidacion)s

---
*Veredicto propio. Cuando difiere del indicador, el motivo esta arriba. Esto no es una
recomendacion de inversion: es una lectura fechada de un grafico, sin backtest ni
expectativa medida detras.*
"""


def construir_fichas(cfg, base):
    fecha = cfg['fecha']
    hechas = []
    for it in cfg['instrumentos']:
        d = os.path.join(base, 'analisis', it['instrumento'], fecha)
        if not os.path.isdir(d):
            os.makedirs(d)
        p = os.path.join(d, '%s_analisis_%s.md' % (it['instrumento'], fecha))
        datos = dict(it)
        datos.update({'ins': it['instrumento'], 'fecha': fecha,
                      'hora': cfg.get('hora', ''), 'velas': cfg.get('velas', 120)})
        datos.setdefault('simbolo', it['instrumento'])
        for k in ('estructura_txt', 'numeros_txt', 'interp_txt', 'condicion',
                  'invalidacion', 'captura'):
            datos.setdefault(k, '?')
        with io.open(p, 'w', encoding='utf-8') as fh:
            fh.write(FICHA % datos)
        hechas.append(p)
    return hechas


def main():
    if len(sys.argv) < 2:
        print('uso: construir_entregables.py <ruta_json>')
        return 1
    with io.open(sys.argv[1], encoding='utf-8') as fh:
        cfg = json.load(fh)
    base = cfg['base']
    dest = os.path.join(base, 'analisis')
    if not os.path.isdir(dest):
        os.makedirs(dest)
    xlsx = os.path.join(dest, 'ANALISIS_%s_%s.xlsx' % (cfg.get('tema', 'ANALISIS'), cfg['fecha']))
    print('EXCEL  ->', construir_excel(cfg, xlsx))
    for p in construir_fichas(cfg, base):
        print('FICHA  ->', p.replace(base + os.sep, ''))
    print('OK %d instrumentos' % len(cfg['instrumentos']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
