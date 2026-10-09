"""Register an original falling/getting-up pair with one body calibration.

The legacy reaction sheets drew the introduction larger than the fall/getup
rows. Calibrating those rows against the introduction made the fighter shrink
when knocked down. Their final standing getup pose is a meaningful reference;
the entire pair uses that one uniform scale, including horizontal KO poses.
"""
import json

from teacher_motion import extract_atlas, read_sff, standing_height

LEGACY = ('alejandro', 'daniela', 'gameros', 'armando', 'vladimir', 'jaime',
          'leonardo', 'cesar')


def legacy_reaction_sprites(root, name, existing=None):
    if name not in LEGACY:
        return {}
    folder = root/'chars'/name
    source = folder/'art/reactions.png'
    if not source.exists():
        source = folder/'art'/f'{name}-intro-fall-getup-win.png'
    if not source.exists():
        return {}
    existing = existing or read_sff(folder/f'{name}.sff')
    frames, metrics = extract_atlas(source, 4, standing_height(existing), reference=(2, 5))
    # In the engine's standard sprite contract 5050,4 is the resting KO.
    # Source row1 finishes flat in cell5; cell4 is still bracing on an elbow.
    fall_order = (0, 1, 2, 3, 5, 4)
    output = {}
    keys = {(group, index) for group, index in existing if group in (5050, 5120)}
    keys.update((group, index) for group in (5050, 5120) for index in range(6))
    for group, index in sorted(keys):
        source_index = min(index, 5)
        output[group, index] = frames[1][fall_order[source_index]] if group == 5050 else frames[2][source_index]
    metrics.update(reference=[2, 5], purpose='one uniform scale for falling and getting up',
                   installed_groups=[5050, 5120], fall_order=list(fall_order))
    (source.parent/'reaction-registration.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return output
