# -*- coding: utf-8 -*-
"""Prepara la carpeta del analista y archiva las capturas de TradingView.

Uso:
    python preparar.py                          -> solo crea/verifica el esqueleto
    python preparar.py <FECHA> <INS1,INS2,...>  -> ademas archiva las capturas

Archiva desde  <carpeta del MCP>/screenshots/<INS>_MTF_<FECHA>.png
hacia          <base>/imagenes/<INS>/<FECHA>/<INS>_MTF_<FECHA>_<HHMM>.png

Existe para que el pipeline no necesite permisos sueltos de crear ni mover ficheros:
toda la escritura pasa por aqui.

RUTAS: se resuelven solas. Para forzarlas, define variables de entorno:
    ANALISTA_BASE      carpeta de trabajo   (por defecto: <Documentos>/Mi analista grafico)
    ANALISTA_SCREENS   capturas del MCP     (por defecto: <HOME>/tradingview-mcp/screenshots)
"""
from __future__ import print_function
import io
import os
import shutil
import sys
import time

HOME = os.path.expanduser('~')


def _documentos():
    """Carpeta de Documentos real. En Windows suele estar redirigida a OneDrive."""
    candidatas = [
        os.path.join(HOME, 'OneDrive', 'Documentos'),   # Windows en espanol + OneDrive
        os.path.join(HOME, 'OneDrive', 'Documents'),    # Windows en ingles + OneDrive
        os.path.join(HOME, 'Documentos'),
        os.path.join(HOME, 'Documents'),
    ]
    for c in candidatas:
        if os.path.isdir(c):
            return c
    return HOME


BASE = os.environ.get('ANALISTA_BASE') or os.path.join(_documentos(), 'Mi analista grafico')
SCREENS = os.environ.get('ANALISTA_SCREENS') or os.path.join(HOME, 'tradingview-mcp', 'screenshots')

CAB_LECTURAS = (
    'fecha,hora,instrumento,tf,open,high,low,close,var_pct,estructura_ema,vs_ema200_pct,'
    'macd_hist,macd_dir,rsi,rsi_dir,atr,score_tf,veredicto,score_ponderado_pct,motivo,'
    'precio_ref,largo_sl,largo_tp,corto_sl,corto_tp,captura\n')
CAB_OPERACIONES = (
    'fecha,hora,instrumento,temporalidad,direccion,entrada,stop,objetivo,salida,'
    'resultado_R,estado,captura,notas\n')

ILEGALES = '<>:"/\\|?* '


def limpiar(simbolo):
    """Nombre de carpeta/fichero a partir de un simbolo de TradingView.

        BINANCE:BTCUSDT -> BTCUSDT
        OANDA:XAUUSD    -> XAUUSD
        NASDAQ:AAPL     -> AAPL
    """
    s = simbolo.strip()
    if ':' in s:
        s = s.rsplit(':', 1)[1]
    for ch in ILEGALES:
        s = s.replace(ch, '_')
    return s.strip('_').upper() or 'INSTRUMENTO'


def asegurar_dir(p):
    if not os.path.isdir(p):
        os.makedirs(p)
        return True
    return False


def esqueleto():
    creadas = []
    for sub in ('', 'imagenes', 'datos', 'analisis'):
        p = os.path.join(BASE, sub) if sub else BASE
        if asegurar_dir(p):
            creadas.append(p)
    for nombre, cab in (('lecturas_mtf.csv', CAB_LECTURAS),
                        ('operaciones.csv', CAB_OPERACIONES)):
        p = os.path.join(BASE, 'datos', nombre)
        if not os.path.exists(p):
            with io.open(p, 'w', encoding='utf-8') as fh:
                fh.write(cab)
            creadas.append(p)
    p = os.path.join(BASE, 'datos', 'BITACORA.md')
    if not os.path.exists(p):
        with io.open(p, 'w', encoding='utf-8') as fh:
            fh.write(u'# Bit\xe1cora del analista gr\xe1fico\n\n'
                     u'Entrada nueva arriba del todo. No se reescriben entradas viejas.\n\n---\n')
        creadas.append(p)
    return creadas


def archivar(fecha, instrumentos):
    hhmm = time.strftime('%H%M')
    movidas, faltan = [], []
    for crudo in instrumentos:
        ins = limpiar(crudo)
        origen = os.path.join(SCREENS, '%s_MTF_%s.png' % (ins, fecha))
        destino_dir = os.path.join(BASE, 'imagenes', ins, fecha)
        asegurar_dir(destino_dir)
        if not os.path.exists(origen):
            faltan.append(ins)
            continue
        destino = os.path.join(destino_dir, '%s_MTF_%s_%s.png' % (ins, fecha, hhmm))
        shutil.move(origen, destino)
        movidas.append(os.path.relpath(destino, BASE))
    return movidas, faltan


def main():
    print('BASE    :', BASE)
    print('SCREENS :', SCREENS)
    if not os.path.isdir(SCREENS):
        print('AVISO   la carpeta de capturas no existe todavia;')
        print('        se crea sola la primera vez que el MCP tome una captura.')
    for p in esqueleto():
        print('CREADO  ->', p.replace(BASE + os.sep, '') or p)
    if len(sys.argv) >= 3:
        fecha = sys.argv[1]
        instrumentos = [s for s in sys.argv[2].split(',') if s.strip()]
        movidas, faltan = archivar(fecha, instrumentos)
        for m in movidas:
            print('ARCHIVO ->', m)
        if faltan:
            print('SIN CAPTURA -> ' + ', '.join(faltan))
        print('OK %d archivadas, %d sin captura' % (len(movidas), len(faltan)))
    else:
        print('OK esqueleto verificado')
    return 0


if __name__ == '__main__':
    sys.exit(main())
