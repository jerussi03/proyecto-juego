"""Keep the in-game lists in the engine's native button notation."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
common='''
KOF A / B / C / D = ^X / ^A / ^Y / ^B
Xbox: X / A / Y / B. RT esquive, RB MAX.

<#ead08e>:Basicos y sistema:</>
Punio ligero / fuerte                 ^X / ^Y
Patada ligera / fuerte                ^A / ^B
Agachado / aire                       mismos cuatro botones
Correr / salto atras                  _F_F / _B_B
Bloquear                              _B / _DB
Esquive adelante                      ^X_+^A o ^C
Esquive atras                         _B + ^X_+^A o ^C
MAX (1000; durante golpe 2000)         ^A_+^Y o ^Z
Golpe de rechazo                      ^Y_+^B
Esquive al bloquear: 1000 de energia.
'''
moves={
'hector': '''
<#ead08e>:Especiales sin barra:</>
Paquete de red                        _D_DF_F + ^X / ^Y
Gancho de protocolo                   _F_D_DF + ^X / ^Y
Latigazo RJ-45                        _D_DB_B + ^X / ^Y
Barrida capa fisica                   _B_DB_D_DF_F + ^A / ^B
Firewall parry                        _D_DB_B + ^A / ^B
Error 403 tras parry                  ^Y
Handshake (cerca)                     _F_DF_D_DB_B + ^X

<#ead08e>:Supers - 1000 de energia:</>
Sin conexion                         _B_DB_D_DF_F + ^X / ^Y
Drone Deploy                         _D_DF_F_D_DF_F + ^X / ^Y
DDoS                                 _D_DF_F_D_DF_F + ^A / ^B
Modo FPV                             _D_DB_B_D_DB_B + ^A / ^B
CTRL ALT SUPR                        _D_DF_F_DF_D_DB_B + ^X / ^Y
Desconectado (rival <=120 vida)       _F_DF_D_DB_B + ^Y

<#ead08e>:MAX2 - 2000 y MAX activo:</>
Denegacion de servicio               _D_DB_B_D_DB_B + ^X_+^Y
''',
'chava': '''
<#63ded7>:Especiales sin barra:</>
Codigo compilado                      _D_DF_F + ^X / ^Y
Codigo, alternativa U                 _B_DB_D_DF_F + ^X / ^Y
Gancho compilacion                    _F_D_DF + ^X / ^Y
Mochilazo de avance                   _D_DB_B + ^X / ^Y
Barrida de semestre                   _B_DB_D_DF_F + ^A / ^B

<#63ded7>:Supers - 1000 de energia:</>
Asistente IA                          _D_DF_F_D_DF_F + ^X / ^Y
Entrega final                         _D_DF_F_DF_D_DB_B + ^X / ^Y

<#63ded7>:MAX2 - 2000 y MAX activo:</>
Compilacion final + IA                _D_DB_B_D_DB_B + ^X_+^Y
'''}
for name,movelist in moves.items():
    text=f'<#abf2eb>:{name.upper()} / CONTROLES KOF:</>\n'+common+movelist+'''
MAX permite cancelar entre especiales distintos al conectar.
Cada cancelacion de especial consume tiempo de MAX.
Las direcciones se invierten al cambiar de lado.
'''
    (ROOT/f'chars/{name}/{name}-movelist.dat').write_text(text,encoding='utf-8')
chava=ROOT/'chars/chava/CHAVA.md'
text=chava.read_text(encoding='utf-8-sig')
if not text.startswith('# Controles actualizados'):
    text=text.replace('| D | Invocar IA, cuesta 1000 de energía |','| D | Activar MAX, cuesta 1000 de energía |')
    text='# Controles actualizados: estilo KOF\n\nConsulta [CONTROLES-KOF.md](../../CONTROLES-KOF.md) para los poderes por movimientos, esquive A+B/RT y MAX B+C/RB. El resto describe la revisión artística anterior.\n\n'+text
    chava.write_text(text,encoding='utf-8')
