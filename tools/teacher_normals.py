"""Original normal-attack repertoires for the UTC cast.

The four KOF buttons and state numbers stay stable. The individual attacks,
confirmed chains, footwork, launchers, jump trajectories and timings do not.
Generated art 8770..8773 replaces the old standing poses used for crouching
and jumping. No pose is scaled. Contact boxes are registered to the visible
extremity in the SFF, rather than extending into empty space.

Builders call apply_cns on each character state file, then apply_air and
apply_cmd. Only existing CNS states are replaced: Hector splits his normals
between hector.cns and kof-extra.cns. Variables 28 and 20..23 are local normal
input/Chava alternation buffers; the resource variables are untouched.
"""
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from io import BytesIO
from pathlib import Path
import argparse
import json
import re
import struct

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NORMAL_STATES = (200, 210, 230, 240, 400, 410, 430, 440, 600, 610, 630, 640)
BUTTONS = {200: 'x', 210: 'y', 230: 'a', 240: 'b', 400: 'x', 410: 'y',
           430: 'a', 440: 'b', 600: 'x', 610: 'y', 630: 'a', 640: 'b'}


@dataclass(frozen=True)
class Normal:
    name: str
    startup: int
    active: int
    recovery: int
    damage: int
    band: tuple
    push: float = 3.0
    stun: int = 17
    step: float = 0.0
    retreat: float = 0.0
    launch: float = 0.0
    fall: bool = False
    multi: int = 1
    air_x: float = 0.0
    dive: float = 0.0
    max_reach: int = 120
    low: bool = False


BASE = {
    200: Normal('', 6, 3, 10, 27, (-92, -43)),
    210: Normal('', 11, 4, 18, 69, (-120, -35), push=5.0, stun=23),
    230: Normal('', 7, 3, 12, 33, (-78, -24)),
    240: Normal('', 11, 4, 18, 64, (-108, -29), push=4.5, stun=22),
    400: Normal('', 5, 3, 10, 23, (-61, -20), push=2.0),
    410: Normal('', 10, 4, 17, 58, (-83, -21), push=3.5, stun=22),
    430: Normal('', 6, 3, 11, 25, (-31, -1), push=2.2, low=True),
    440: Normal('', 10, 4, 20, 57, (-36, -1), push=4.0, fall=True, low=True),
    600: Normal('', 6, 4, 10, 28, (-108, -44)),
    610: Normal('', 9, 5, 15, 55, (-100, -25), push=4.0, stun=23),
    630: Normal('', 7, 5, 10, 31, (-86, -22)),
    640: Normal('', 10, 5, 16, 59, (-100, -8), push=4.5, stun=23),
}

# Explicit move names describe the physical action, not a renamed projectile.
NAMES = {
    'chava': ('Jab alternado', 'Mochila ascendente', 'Patada frontal', 'Patada alta',
              'Jab desde cuclillas', 'Gancho agachado', 'Toque al tobillo', 'Barrida de semestre',
              'Jab de salto', 'Martillo descendente', 'Patada horizontal', 'Hacha aerea'),
    'hector': ('Ping inicial', 'Latigazo RJ45 corto', 'Puntapie de protocolo', 'Patada del firewall',
               'Ping bajo', 'Gancho de cable', 'Toque de capa fisica', 'Barrido de red',
               'Ping en salto', 'Codo de desconexion', 'Patada de enlace', 'Patada descendente'),
    'chan_kof': ('Palma de correccion', 'Empuje de crossfit', 'Puntapie de senderismo', 'Patada de precision',
                 'Correccion desde cuclillas', 'Elevacion de crossfit', 'Paso al tobillo', 'Barrido de indice',
                 'Palma de descenso', 'Codo de crossfit', 'Extension de senderismo', 'Patada de cumbre'),
    'felix': ('Toque de diagnostico', 'Codo de reparacion', 'Puntapie de comprobacion', 'Talon de soporte',
              'Ajuste bajo', 'Gancho de herramienta', 'Comprobacion al tobillo', 'Cable rasante',
              'Toque de mantenimiento', 'Codo de emergencia', 'Patada de alcance', 'Talon descendente'),
    'alejandro': ('Entrada corta', 'Codo de refactor', 'Patada de separacion', 'Extension de componente',
                  'Edicion baja', 'Compilacion ascendente', 'Paso de depuracion', 'Retirada de error',
                  'Entrada en salto', 'Codo de integracion', 'Cruce de componente', 'Descenso de deploy'),
    'daniela': ('Palma de requisito', 'Bolsazo documentado', 'Paso de negocio', 'Patada de cierre',
                'Revision baja', 'Carpeta ascendente', 'Puntapie de agenda', 'Cierre al tobillo',
                'Revision aerea', 'Bolsazo descendente', 'Extension de alcance', 'Patada de entrega'),
    'gameros': ('Jab de boxeo', 'Doble directo', 'Paso de gimnasio', 'Doble patada arcade',
                'Jab al cuerpo', 'Gancho de gimnasio', 'Pedal corto', 'Deslizamiento ciclista',
                'Directo de salto', 'Codo de gimnasio', 'Rodilla de salto', 'Patada en picada'),
    'armando': ('Toque de pingpong', 'Reves de raqueta', 'Paso de cancha', 'Patada de rebote',
                'Recepcion baja', 'Elevacion de cancha', 'Puntapie de defensa', 'Deslizamiento de cancha',
                'Manotazo de rebote', 'Manotazo de clavada', 'Rodilla de basquet', 'Patada de aterrizaje'),
    'vladimir': ('Palma de alto', 'Empuje de asistencia', 'Paso de director', 'Puntapie de retencion',
                 'Alto desde cuclillas', 'Codo de control', 'Puntapie al alumno', 'Barrido de salida',
                 'Palma de presencia', 'Golpe de autoridad', 'Patada de paso', 'Talon de retencion'),
    'jaime': ('Jab de apertura', 'Codo de gambito', 'Pedal de avance', 'Patada de caballo',
              'Apertura baja', 'Diagonal ascendente', 'Pedal rasante', 'Barrido de tablero',
              'Mano diagonal', 'Codo de calculo', 'Rodilla ciclista', 'Diagonal descendente'),
    'leonardo': ('Toque rapido', 'Codo elegante', 'Patada de toque', 'Circular de swipe',
                 'Toque desde cuclillas', 'Codo ascendente', 'Swipe al tobillo', 'Barrido de pantalla',
                 'Toque movil', 'Codo de desplazamiento', 'Patada cruzada', 'Circular aerea'),
    'cesar': ('Palma estricta', 'Baston de sentencia', 'Puntapie de advertencia', 'Talon de castigo',
              'Advertencia baja', 'Baston desde cuclillas', 'Puntapie estricto', 'Barrido disciplinario',
              'Palma de emergencia', 'Baston descendente', 'Puntapie de apoyo', 'Castigo al aterrizar'),
}


def _kit(id, changes):
    moves = {n: replace(BASE[n], name=name) for n, name in zip(NORMAL_STATES, NAMES[id])}
    for n, attrs in changes.items():
        moves[n] = replace(moves[n], **attrs)
    return moves


KITS = {
    'chava': _kit('chava', {
        200: dict(startup=5, recovery=9), 210: dict(startup=12, damage=76, step=1.0),
        410: dict(launch=-6.0, fall=True), 610: dict(fall=True, dive=1.6),
        640: dict(fall=True, dive=2.2),
    }),
    'hector': _kit('hector', {
        200: dict(startup=3, active=2, recovery=8, damage=22, push=1.2, stun=18),
        210: dict(startup=12, recovery=20, damage=72, push=6.0, step=1.1),
        230: dict(startup=7, damage=32), 240: dict(startup=10, damage=65),
        400: dict(startup=5, max_reach=72), 410: dict(startup=10, launch=-6.0, fall=True),
        440: dict(startup=9, damage=54, step=1.4), 610: dict(damage=58, fall=True),
        640: dict(startup=9, dive=2.8, fall=True),
    }),
    'chan_kof': _kit('chan_kof', {
        200: dict(startup=5, max_reach=55, push=1.5),
        210: dict(startup=10, damage=78, step=1.1, stun=26),
        230: dict(startup=6, recovery=10, retreat=-0.8),
        240: dict(startup=12, damage=72, push=5.0),
        400: dict(startup=5, recovery=8, push=1.1),
        410: dict(startup=11, damage=65, launch=-6.4, fall=True),
        430: dict(startup=6, recovery=9), 440: dict(startup=12, damage=65, step=1.0),
        610: dict(startup=9, damage=62, fall=True), 640: dict(startup=11, damage=65, dive=1.8),
    }),
    'felix': _kit('felix', {
        200: dict(startup=6, push=1.5), 210: dict(startup=11, damage=74, step=1.8, stun=26),
        230: dict(retreat=-1.0), 240: dict(startup=13, damage=70, push=5.5),
        400: dict(startup=5, push=0.8, stun=21),
        410: dict(startup=10, launch=-5.7, fall=True, damage=64),
        430: dict(startup=7, retreat=-0.7),
        440: dict(startup=11, fall=False, push=0.7, stun=29, retreat=-1.8),
        610: dict(startup=10, damage=62, fall=True),
        630: dict(air_x=-0.8), 640: dict(damage=65, push=5.7),
    }),
    'alejandro': _kit('alejandro', {
        200: dict(startup=4, active=2, recovery=8, damage=22, max_reach=49),
        210: dict(startup=8, recovery=14, damage=61, step=3.0),
        230: dict(startup=6, retreat=-1.5), 240: dict(startup=10, damage=61, step=1.2),
        400: dict(startup=4, damage=20, recovery=8),
        410: dict(startup=9, damage=51, launch=-5.5, fall=True),
        430: dict(startup=5, recovery=9),
        440: dict(startup=9, recovery=17, damage=50, retreat=-2.0),
        600: dict(startup=5, recovery=8), 610: dict(startup=8, damage=50),
        630: dict(startup=6, air_x=1.5), 640: dict(startup=9, damage=56, dive=3.0),
    }),
    'daniela': _kit('daniela', {
        200: dict(startup=5, recovery=9, push=1.0),
        210: dict(startup=9, recovery=16, damage=71, step=1.4, stun=25),
        230: dict(startup=6, active=3, damage=20, multi=2, step=1.1, push=0.8),
        240: dict(startup=11, damage=70, push=5.0),
        400: dict(startup=5, recovery=8),
        410: dict(startup=9, recovery=15, damage=57, step=1.0, stun=25),
        430: dict(startup=6, push=1.2),
        440: dict(startup=10, fall=False, push=1.0, stun=28),
        600: dict(startup=5), 610: dict(startup=9, damage=62, fall=True, dive=1.4),
        630: dict(startup=7, air_x=0.7), 640: dict(damage=63, push=5.5),
    }),
    'gameros': _kit('gameros', {
        200: dict(startup=4, active=2, recovery=7, damage=21, push=0.8, stun=18),
        210: dict(startup=7, active=3, recovery=15, damage=30, multi=2, step=1.8, push=1.1),
        230: dict(startup=5, recovery=8, damage=26, step=1.9, push=1.2),
        240: dict(startup=9, active=3, recovery=17, damage=29, multi=2, step=1.3, push=1.8),
        400: dict(startup=4, recovery=8, damage=20),
        410: dict(startup=8, damage=53, launch=-5.0, fall=True),
        430: dict(startup=5, recovery=8, step=1.5, damage=23),
        440: dict(startup=9, recovery=21, step=3.6, damage=54),
        600: dict(startup=4, recovery=8, damage=24),
        610: dict(startup=7, damage=48, air_x=1.1),
        630: dict(startup=5, damage=29, air_x=1.0),
        640: dict(startup=8, damage=58, dive=4.3, air_x=1.2, fall=True),
    }),
    'armando': _kit('armando', {
        200: dict(startup=5, active=2, recovery=8, damage=26, push=1.3),
        210: dict(startup=9, active=4, recovery=17, damage=33, multi=2, step=1.4, push=1.5),
        230: dict(startup=6, step=1.3),
        240: dict(startup=12, damage=67, launch=-7.0, fall=True),
        400: dict(startup=5, recovery=9),
        410: dict(startup=10, damage=60, launch=-6.2, fall=True),
        430: dict(startup=6, retreat=-0.5),
        440: dict(startup=10, recovery=22, damage=60, step=2.0),
        600: dict(startup=5, air_x=0.7),
        610: dict(startup=9, damage=63, dive=2.0, fall=True),
        630: dict(startup=6, damage=34, air_x=1.3),
        640: dict(startup=10, damage=64, dive=3.2, fall=True),
    }),
    'vladimir': _kit('vladimir', {
        200: dict(startup=7, damage=33, push=0.5, stun=21, max_reach=56),
        210: dict(startup=13, recovery=23, damage=84, step=2.3, push=1.0, stun=30),
        230: dict(startup=9, damage=38, push=1.1),
        240: dict(startup=15, recovery=24, damage=78, push=1.4, stun=29),
        400: dict(startup=6, damage=29, push=0.7, stun=21),
        410: dict(startup=12, damage=68, push=1.2, stun=28),
        430: dict(startup=8, damage=31, push=0.5),
        440: dict(startup=13, recovery=25, damage=69, step=1.0),
        600: dict(startup=7, damage=33), 610: dict(startup=11, damage=66, fall=True),
        630: dict(startup=9, damage=37, air_x=-0.6),
        640: dict(startup=13, damage=73, push=1.5, fall=True),
    }),
    'jaime': _kit('jaime', {
        200: dict(startup=5, recovery=9, damage=25, push=1.8),
        210: dict(startup=10, recovery=16, damage=65, step=1.6),
        230: dict(startup=6, recovery=10, damage=31, step=2.1),
        240: dict(startup=10, recovery=19, damage=66, step=1.3, launch=-5.0, fall=True),
        400: dict(startup=5, recovery=9),
        410: dict(startup=10, damage=62, launch=-6.8, fall=True),
        430: dict(startup=5, recovery=9, damage=26, retreat=-1.2),
        440: dict(startup=10, damage=59, step=1.7),
        600: dict(startup=5, air_x=1.1),
        610: dict(startup=8, damage=54, air_x=-0.8),
        630: dict(startup=6, damage=33, air_x=1.5),
        640: dict(startup=9, damage=64, dive=3.2, air_x=2.0, fall=True),
    }),
    'leonardo': _kit('leonardo', {
        200: dict(startup=4, active=2, recovery=8, damage=20, max_reach=48),
        210: dict(startup=8, recovery=14, damage=57, retreat=-1.1),
        230: dict(startup=5, recovery=8, damage=27, push=1.4),
        240: dict(startup=9, active=4, recovery=17, damage=30, multi=2, step=1.3, push=1.8),
        400: dict(startup=4, recovery=7, damage=19),
        410: dict(startup=8, recovery=14, damage=48, launch=-5.2, fall=True),
        430: dict(startup=5, recovery=8, damage=23, retreat=-1.4),
        440: dict(startup=9, recovery=18, damage=49, step=2.4),
        600: dict(startup=4, recovery=8, damage=23, air_x=-0.7),
        610: dict(startup=7, recovery=12, damage=47, air_x=-1.2),
        630: dict(startup=5, damage=28, air_x=1.5),
        640: dict(startup=8, active=4, recovery=15, damage=29, multi=2, air_x=-0.9),
    }),
    'cesar': _kit('cesar', {
        200: dict(startup=8, recovery=13, damage=38, push=3.6),
        210: dict(startup=16, active=5, recovery=27, damage=96, push=6.8, stun=30),
        230: dict(startup=10, recovery=16, damage=43, push=3.0),
        240: dict(startup=17, active=5, recovery=26, damage=85, fall=True, push=5.8),
        400: dict(startup=7, recovery=12, damage=34, stun=24, push=0.8),
        410: dict(startup=14, active=5, recovery=23, damage=78, push=5.5),
        430: dict(startup=9, recovery=14, damage=37, push=2.6),
        440: dict(startup=15, active=5, recovery=28, damage=79, push=5.0),
        600: dict(startup=8, recovery=12, damage=36),
        610: dict(startup=13, active=5, recovery=23, damage=79, fall=True),
        630: dict(startup=10, recovery=16, damage=40),
        640: dict(startup=15, active=5, recovery=24, damage=80, fall=True, dive=1.2),
    }),
}

# (destination, input) pairs. These are hit-confirm routes, not universal
# light->strong changes. A failed/blocked attack has to finish its recovery.
CHAINS = {
    'chava': {200: [(210, 'y'), (240, 'b')], 230: [(210, 'y'), (240, 'b')],
              400: [(410, 'y')], 430: [(440, 'b')], 600: [(610, 'y')], 630: [(640, 'b')]},
    'hector': {200: [(201, 'x')], 201: [(202, 'x')], 230: [(210, 'y')],
               400: [(410, 'y')], 600: [(610, 'y')]},
    'chan_kof': {200: [(210, 'y')], 400: [(410, 'y')], 430: [(440, 'b')]},
    'felix': {400: [(210, 'y')], 200: [(240, 'b')], 630: [(610, 'y')]},
    'alejandro': {200: [(210, 'y')], 430: [(210, 'y')], 600: [(640, 'b')]},
    'daniela': {200: [(230, 'a')], 230: [(210, 'y')], 400: [(410, 'y')], 600: [(610, 'y')]},
    'gameros': {200: [(230, 'a')], 230: [(210, 'y')], 210: [(240, 'b')],
                400: [(430, 'a')], 430: [(410, 'y')], 600: [(630, 'a')], 630: [(640, 'b')]},
    'armando': {200: [(240, 'b')], 400: [(410, 'y')], 600: [(610, 'y')], 630: [(640, 'b')]},
    'vladimir': {200: [(210, 'y')]},
    'jaime': {230: [(240, 'b')], 430: [(410, 'y')], 600: [(640, 'b')], 630: [(610, 'y')]},
    'leonardo': {230: [(240, 'b')], 400: [(430, 'a')], 430: [(240, 'b')],
                 600: [(630, 'a')], 630: [(640, 'b')]},
    'cesar': {400: [(210, 'y')]},
}


def _control(n, title, kind, trigger, params):
    return f'\n[State {n}, {title}]\ntype = {kind}\n{trigger}\n{params}\n'


def _state(n, move, id):
    posture = 'A' if n >= 600 else 'C' if n >= 400 else 'S'
    heavy = n in (210, 240, 410, 440, 610, 640, 202)
    anim = str(n)
    alternate = {200: (20, 201), 210: (21, 211), 400: (22, 401), 600: (23, 601)}
    if id == 'chava' and n in alternate:
        var, second = alternate[n]
        anim = f'ifelse(var({var}),{second},{n})'
    out = (f'\n[Statedef {n}]\ntype = {posture}\nmovetype = A\nphysics = {posture}\n'
           f'anim = {anim}\nctrl = 0\npoweradd = 0\njuggle = {4 if heavy else 1}\n'
           'sprpriority = 2\n')
    if posture != 'A':
        out += 'velset = 0,0\n'
    out += f'; {move.name}: startup {move.startup}, active {move.active}, recovery {move.recovery}.\n'
    out += _control(n, 'Reset normal buffer', 'VarSet', 'trigger1 = Time = 0', 'v = 28\nvalue = 0')
    if id == 'chava' and n in alternate:
        var, _ = alternate[n]
        out += _control(n, 'Alternate original pose', 'VarSet', 'trigger1 = Time = 0', f'v = {var}\nvalue = 1-var({var})')
    if move.step:
        out += _control(n, 'Own approach', 'VelSet',
                        f'trigger1 = Time = [2,{move.startup + move.active - 1}]', f'x = {move.step}')
        out += _control(n, 'Approach recovery', 'VelSet',
                        f'trigger1 = Time = {move.startup + move.active}', 'x = 0')
    if move.retreat:
        out += _control(n, 'Own retreat', 'VelSet',
                        f'trigger1 = AnimElemTime({7 if move.multi > 1 else 6}) >= 0', f'x = {move.retreat}')
    if posture == 'A' and move.air_x:
        out += _control(n, 'Own aerial line', 'VelAdd', 'trigger1 = AnimElem = 4', f'x = {move.air_x}')
    if posture == 'A' and move.dive:
        out += _control(n, 'Own descending line', 'VelSet', 'trigger1 = AnimElem = 4', f'y = max(Vel Y,{move.dive})')
    out += _control(n, 'Swing', 'PlaySnd', 'trigger1 = AnimElem = 3', f'value = 0,{4 if heavy else 0}')
    for contact in range(move.multi):
        final = contact == move.multi-1
        low = move.low
        guard = 'HA' if posture == 'A' else 'L' if low else 'MA'
        launch = move.launch if final else 0
        fall = (move.fall or bool(launch)) and final
        push = move.push if final else min(0.8, move.push)
        out += _control(n, f'Physical contact {contact+1}', 'HitDef',
                        f'trigger1 = AnimElem = {4+contact*2}',
                        f'attr = {posture},NA\ndamage = {move.damage},0\n'
                        f'animtype = {"Heavy" if heavy else "Light"}\n'
                        f'guardflag = {guard}\nhitflag = MAF\npriority = {4 if heavy else 3},Hit\n'
                        f'pausetime = {8 if heavy else 5},{10 if heavy else 7}\n'
                        f'sparkno = {2 if heavy else 0}\nsparkxy = -7,{(move.band[0]+move.band[1])//2}\n'
                        f'hitsound = 5,{2 if heavy else 0}\nguardsound = 6,0\n'
                        f'ground.type = {"Low" if low else "High"}\n'
                        f'ground.slidetime = {max(8, move.stun-5)}\nground.hittime = {move.stun}\n'
                        f'ground.velocity = {-push}' + (f',{launch}' if launch else '') + '\n'
                        f'air.velocity = {-max(1.5,push)},{launch or -3.5}\nair.hittime = 22\n'
                        f'fall = {int(fall)}\nfall.recover = {0 if fall else 1}\n'
                        f'getpower = {30 if heavy else 15},8\ngivepower = 15,8')
    for target, button in CHAINS[id].get(n, []):
        out += _control(n, f'Queue {button} chain', 'VarSet',
                        f'triggerall = AILevel = 0\ntriggerall = Time >= 5\n'
                        f'triggerall = AnimElemTime({8 if move.multi > 1 else 7}) < 0\ntrigger1 = command = "{button}"',
                        f'v = 28\nvalue = {target}\nignorehitpause = 1')
    if CHAINS[id].get(n):
        out += _control(n, 'Own confirmed chain', 'ChangeState',
                        'triggerall = var(28) > 0\ntriggerall = MoveHit\n'
                        f'trigger1 = AnimElemTime({7 if move.multi > 1 else 5}) >= 0', 'value = var(28)\nctrl = 0')
    # Chava keeps the original manually authored left/right repeat on whiff.
    if id == 'chava' and n in alternate:
        button = BUTTONS[n]
        out += _control(n, 'Queue alternate repeat', 'VarSet',
                        f'triggerall = AILevel = 0\ntriggerall = Time >= 5\n'
                        f'trigger1 = command = "{button}"', f'v = 28\nvalue = {n}\nignorehitpause = 1')
        out += _control(n, 'Buffered alternate repeat', 'ChangeState',
                        f'trigger1 = var(28) = {n} && AnimElemTime(6) >= 0', f'value = {n}\nctrl = 0')
    if posture == 'A':
        out += _control(n, 'Land safely', 'ChangeState',
                        'trigger1 = Pos Y >= 0 && Vel Y > 0', 'value = 52\nctrl = 0')
    end = 50 if posture == 'A' else 11 if posture == 'C' else 0
    out += _control(n, 'Finish normal', 'ChangeState', 'trigger1 = AnimTime = 0', f'value = {end}\nctrl = 1')
    return out


def apply_cns(text, id):
    """Replace existing normal states only; safe on Hector's split files."""
    if id not in KITS:
        return text
    moves = dict(KITS[id])
    if id == 'hector':
        moves[201] = replace(moves[200], name='Segundo Ping', damage=24, step=1.0)
        moves[202] = replace(moves[200], name='Pong de cierre', damage=46, startup=6,
                             recovery=17, push=5.8, stun=24)
    for n, move in moves.items():
        pattern = rf'(?ims)^\[Statedef {n}\].*?(?=^\[Statedef |\Z)'
        text = re.sub(pattern, lambda m, n=n, move=move: _state(n, move, id).lstrip(), text)
    return text


@lru_cache(maxsize=24)
def _sff(path, mtime):
    blob = Path(path).read_bytes()
    off, count = struct.unpack_from('<II', blob, 36)
    ldata = struct.unpack_from('<I', blob, 52)[0]
    entries = {}
    ordered = []
    for i in range(count):
        e = struct.unpack_from('<HHHHhhHBBIIHH', blob, off+i*28)
        ordered.append(e)
        entries[e[:2]] = e
    return blob, ldata, entries, ordered


def _sprite(id, group, index):
    path = ROOT / 'chars' / id / f'{id}.sff'
    if not path.exists():
        return None
    blob, ldata, entries, ordered = _sff(str(path), path.stat().st_mtime_ns)
    e = entries.get((group, index))
    if e is None:
        return None
    ax, ay = e[4:6]
    while not e[10] and e[6] < len(ordered):
        linked = ordered[e[6]]
        if linked == e:
            return None
        e = linked
    if e[7] not in (11, 12):
        return None
    image = Image.open(BytesIO(blob[ldata+e[9]+4:ldata+e[9]+e[10]])).convert('RGBA')
    return image, ax, ay


def _has_group(id, group):
    return _sprite(id, group, 3) is not None


def _pose(id, n):
    multi = n in KITS[id] and KITS[id][n].multi > 1
    if id not in {'chava', 'hector'}:
        new = 8770 if n == 210 else 8771 if n in (400, 410) else 8772 if n in (600, 610) else 8773 if n in (630, 640) else None
        if new and _has_group(id, new):
            if id == 'jaime' and new in (8772, 8773):
                # His aerial atlas extends on sprite2 and folds back on 3.
                # Sprite5 contains another kick, so recovery ends on 4.
                return new, (0, 1, 1, 2, 1, 2, 3, 4) if multi else (0, 1, 1, 2, 2, 3, 4)
            # Visual review of the authored atlas places the full extension
            # at sprite3. Sprite2 is still windup. A second contact visibly
            # retracts to sprite1 before striking again at AIR element6.
            return new, (0, 1, 2, 3, 1, 3, 4, 5) if multi else (0, 1, 2, 3, 3, 4, 5)
    group = n
    # Their first importer incorrectly packed the punch row into group230.
    # Group240 contains the authored six-phase standing kick, at native axes.
    if id in {'chan_kof', 'felix'} and n == 230:
        group = 240
    if id == 'hector' and n == 440:
        group = 430
    if id == 'hector' and n == 610:
        group = 600
    if id not in {'chava', 'hector'} and n in (400, 410):
        group = 440  # temporary fallback before the genuine crouch art exists
    return group, (0, 1, 2, 3, 1, 3, 4, 5) if multi else (0, 1, 2, 3, 4, 5, 5)


def _contact_box(id, group, index, move, n):
    pose = _sprite(id, group, index)
    if pose is None:
        return (6, move.band[0], min(move.max_reach, 62), move.band[1])
    image, ax, ay = pose
    alpha = image.getchannel('A')
    top, bottom = move.band
    # Register the extended limb/weapon, including its inner segment. Using
    # only its outer tip made long kicks and cable strikes pass through a
    # nearby opponent. Keep the visible outer reach and exclude the torso.
    x1 = min(image.width, max(0, ax+3))
    x2 = min(image.width, max(x1, ax+move.max_reach))
    y1 = min(image.height, max(0, ay+top))
    y2 = min(image.height, max(y1, ay+bottom))
    region = alpha.crop((x1, y1, x2, y2))
    region_top = y1-ay
    bbox = region.getbbox()
    if not bbox:
        # A raised/new pose can move the limb outside its nominal old band.
        region = alpha.crop((x1, 0, x2, image.height))
        bbox = region.getbbox()
        region_top = -ay
    if not bbox:
        raise ValueError(f'{id} normal {n}: no visible contact extremity in {group},{index}')
    right = min(move.max_reach, x1-ax+bbox[2]+1)
    left = max(3, min(16, right-30))
    y1 = max(-ay, region_top+bbox[1]-1)
    y2 = min(image.height-ay, region_top+bbox[3]+1)
    return left, y1, right, y2


def _hurt_boxes(id, group, index, n):
    pose = _sprite(id, group, index)
    crouch = 400 <= n < 600
    if pose:
        image, ax, ay = pose
        bbox = image.getchannel('A').getbbox()
        top, bottom = bbox[1]-ay, bbox[3]-ay
        # Exclude extended weapons/feet from the torso rectangle while keeping
        # a vulnerable limb box on active frames in _action below.
        width = 20 if id != 'hector' else 25
        mid = top + round((bottom-top)*.55)
        return [(-width, top+2, width, mid), (-width-3, mid, width+3, bottom)]
    return [(-21, -65 if crouch else -103, 21, -28 if crouch else -48),
            (-24, -28 if crouch else -48, 24, 0)]


def _durations(move):
    a = max(1, move.startup//3)
    b = max(1, (move.startup-a)//2)
    c = move.startup-a-b
    r1 = max(1, move.recovery//2)
    if move.multi > 1:
        return (a, b, c, move.active, 2, move.active, r1, move.recovery-r1)
    return (a, b, c, move.active, move.active if move.multi > 1 else 2,
            r1, move.recovery-r1)


def _action(id, n, move, sprite_state=None):
    group, indices = _pose(id, sprite_state or n)
    out = f'\n[Begin Action {n}]\n; {move.name}; individual original normal.\n'
    for elem, (index, ticks) in enumerate(zip(indices, _durations(move)), 1):
        boxes = _hurt_boxes(id, group, index, n)
        active = elem == 4 or (elem == 6 and move.multi > 1)
        attack = _contact_box(id, group, index, move, n) if active else None
        if active:
            boxes.append(attack)
        out += f'Clsn2: {len(boxes)}\n'
        out += ''.join(f'Clsn2[{i}] = {",".join(map(str, box))}\n' for i, box in enumerate(boxes))
        out += 'Clsn1: 1\nClsn1[0] = '+','.join(map(str, attack))+'\n' if active else 'Clsn1: 0\n'
        out += f'{group},{index}, 0,0, {ticks}\n'
    return out+'\n'


def apply_air(text, id):
    """Register dedicated poses and visible attack boxes without resizing art."""
    if id not in KITS:
        return text
    moves = dict(KITS[id])
    sources = {}
    if id == 'chava':
        for n, original in [(201, 200), (211, 210), (401, 400), (601, 600)]:
            moves[n] = moves[original]
            sources[n] = n
    elif id == 'hector':
        moves[201] = replace(moves[200], name='Segundo Ping', damage=24)
        moves[202] = replace(moves[200], name='Pong de cierre', damage=46, startup=6, recovery=17)
    for n, move in moves.items():
        block = _action(id, n, move, sources.get(n))
        pattern = rf'(?ims)^\[Begin Action {n}\].*?(?=^\[Begin Action |\Z)'
        if re.search(pattern, text):
            text = re.sub(pattern, lambda _: block.lstrip(), text)
        else:
            text = text.rstrip()+'\n\n'+block.lstrip()
    return text.rstrip()+'\n'


def apply_cmd(text, id):
    """Keep controls; remove the inherited universal normal-cancel routes."""
    if id not in KITS:
        return text
    pattern = r'(?ims)^\[State -1,[^\]]*\].*?(?=^\[State |\Z)'
    def edit(match):
        block = match[0]
        target = re.search(r'(?im)^value\s*=\s*(\d+)\s*$', block)
        if not target or int(target[1]) not in NORMAL_STATES:
            return block
        if not re.search(r'(?im)^type\s*=\s*ChangeState\s*$', block):
            return block
        # CTRL entry is preserved. The new normal states own confirmed chains.
        return re.sub(r'(?m)^trigger[2-9]\s*=.*\n?', '', block)
    return re.sub(pattern, edit, text)


def describe(id):
    """Serializable design and test information for move lists/QA."""
    moves = {}
    for n, move in KITS[id].items():
        data = asdict(move)
        group, indices = _pose(id, n)
        data.update(state=n, button=BUTTONS[n], group=group, indices=indices,
                    durations=_durations(move), total=sum(_durations(move)),
                    contact_box=_contact_box(id, group, indices[3], move, n),
                    contact_elements=[4, 6] if move.multi > 1 else [4],
                    chains=CHAINS[id].get(n, []))
        moves[str(n)] = data
    return dict(character=id, moves=moves, normal_buffer=28,
                contacts=[4, 6], art_scale='native', controls='KOF x/a/y/b')


def apply(cns, air, cmd, id):
    return apply_cns(cns, id), apply_air(air, id), apply_cmd(cmd, id)


def update_movelist(text, id):
    """Keep a readable catalogue of the actual four-button physical attacks."""
    title = '<#63ded7>:Golpes propios:</>'
    text = re.sub(r'(?ms)\n'+re.escape(title)+r'.*?(?=\n<#|\Z)', '', text)
    out = '\n\n'+title+'\n'
    for label, states in [('De pie', (200, 230, 210, 240)),
                          ('Agachado', (400, 430, 410, 440)),
                          ('En el aire', (600, 630, 610, 640))]:
        out += label+':\n'
        for n in states:
            move = KITS[id][n]
            command = '^'+BUTTONS[n].upper()
            out += f'{move.name:<36} {command}\n'
    out += '\nCadenas propias: conecta antes de continuar.\n'
    for source, routes in CHAINS[id].items():
        name = 'Segundo Ping' if source == 201 else KITS[id][source].name
        for target, button in routes:
            target_name = 'Segundo Ping' if target == 201 else 'Pong de cierre' if target == 202 else KITS[id][target].name
            out += f'{name} > {target_name} (^{button.upper()})\n'
    out += 'Si el rival bloquea o esquiva, termina la recuperacion.\n'
    if id == 'chava':
        out += 'Chava conserva repeticion alternada con el mismo boton.\n'
    return text.rstrip()+out


def write_catalog():
    """Compact source-facing catalogue, useful for QA and future balancing."""
    catalog = {}
    for id in KITS:
        catalog[id] = {'buffer_variable': 28, 'moves': {}}
        for n, move in KITS[id].items():
            catalog[id]['moves'][str(n)] = dict(
                name=move.name, button=BUTTONS[n], startup=move.startup,
                active=move.active, recovery=move.recovery, damage=move.damage,
                contacts=move.multi, contact_elements=[4, 6] if move.multi > 1 else [4],
                animation_durations=_durations(move), step=move.step, retreat=move.retreat,
                launch=move.launch, fall=move.fall, air_x=move.air_x, dive=move.dive,
                chains=CHAINS[id].get(n, []))
    path = ROOT / 'data/teacher-normal-kits.json'
    content = json.dumps(catalog, ensure_ascii=False, indent=2)+'\n'
    if not path.exists() or path.read_text(encoding='utf-8') != content:
        path.write_text(content, encoding='utf-8')
    return path


def install(id, check=False):
    folder = ROOT / 'chars' / id
    changed = []
    files = [(folder / f'{id}.cns', apply_cns),
             (folder / 'kof-extra.cns', apply_cns),
             (folder / f'{id}.air', apply_air),
             (folder / f'{id}.cmd', apply_cmd),
             (folder / f'{id}-movelist.dat', update_movelist),
             (folder / 'art/normal-v3/moves.json',
              lambda text, id: json.dumps(describe(id), ensure_ascii=False, indent=2))]
    for path, transform in files:
        if not path.exists():
            continue
        before = path.read_text(encoding='utf-8')
        after = transform(before, id)
        if before == after:
            continue
        changed.append(str(path.relative_to(ROOT)))
        if not check:
            path.write_text(after, encoding='utf-8')
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='*', metavar='CHARACTER',
                        help='Character IDs; omit to process all twelve.')
    parser.add_argument('--check', action='store_true', help='Check generated files without writing.')
    parser.add_argument('--describe', action='store_true', help='Print the physical move catalogue without writing.')
    args = parser.parse_args()
    unknown = sorted(set(args.characters)-KITS.keys())
    if unknown:
        parser.error('unknown character(s): '+', '.join(unknown)+
                     '; choose from '+', '.join(sorted(KITS)))
    ids = args.characters or list(KITS)
    if args.describe:
        print(json.dumps({id: describe(id) for id in ids}, ensure_ascii=False, indent=2))
        return
    changed = []
    for id in ids:
        updated = install(id, check=args.check)
        changed.extend(updated)
        print(f'{id}: {len(updated)} files '+('need rebuilding' if args.check else 'updated'))
    if not args.check:
        write_catalog()
    elif changed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
