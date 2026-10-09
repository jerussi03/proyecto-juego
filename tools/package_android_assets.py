#!/usr/bin/env python3
"""Build the Android game data from an explicit, validated runtime allowlist.

No desktop resources are changed. Generated assets and the reproducible manifest
live below scratch/. Java/Gradle can package that directory directly as assets.
The optional JSON overrides map INI section names to key/value dictionaries so
the Android input bridge can supply its actual controller mapping.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "scratch/android-game-assets"
FIGHTERS = (
    "chava", "hector", "chan_kof", "felix", "alejandro", "daniela",
    "gameros", "armando", "vladimir", "jaime", "leonardo", "cesar",
)
STAGES = (
    "patio", "utc_auditorio", "utc_biblioteca", "utc_cafeteria",
    "utc_entrada", "utc_gastronomia", "utc_pasillo", "utc_patio",
    "utc_vinculacion",
)
CHARACTER_FILES = (
    "{id}.def", "{id}.cmd", "{id}.cns", "{id}.air", "{id}.sff",
    "{id}.snd", "{id}-movelist.dat", "kof-extra.cns",
)
COMMON_FILES = (
    "data/action.zss", "data/common.air", "data/common.cmd",
    "data/common.const", "data/common.snd", "data/common1.cns.zss",
    "data/demo.zss", "data/dizzy.zss", "data/fight.def", "data/fight.sff",
    "data/fight.snd", "data/fightfx.air", "data/fightfx.sff",
    "data/functions.zss", "data/glyphs.sff", "data/guardbreak.zss",
    "data/score.zss", "data/select.def", "data/system.snd",
    "data/system.zss", "data/tag.zss", "data/training.zss",
    "data/gofx/gofx.def", "data/gofx/gofx.sff", "data/gofx/gofx.snd",
    "data/gofx/gofx.air", "data/ikemen1/system.def",
    "data/ikemen1/system.sff", "data/ikemen1/logo.def",
    "data/ikemen1/credits.def", "data/story/pages.lua",
    "data/story/route.lua", "data/story/story.sff", "chars/kof-system.cns",
    "external/gamecontrollerdb.txt", "external/mods/utc_story.lua",
    "external/script/default.lua", "external/script/debug.lua",
    "external/script/main.lua", "external/script/menu.lua",
    "external/script/options.lua", "external/script/start.lua",
    "external/icons/IkemenCylia_256.png", "external/icons/IkemenCylia_96.png",
    "external/icons/IkemenCylia_48.png", "video/ik_logo.webm",
    "video/ik_credits.webm", "save/config.ini", "LICENSES.txt",
)
MOTIF_FONTS = (
    "Action", "ComboCounter", "HitNum", "Menu1", "Menu2", "Menu2Small",
    "Pixel", "PixelFlat", "PowerbarNum", "Round", "Timer",
)
SYSTEM_FONT_FILES = (
    "font/default-3x5.def", "font/default-3x5.sff",
    "font/default-3x5-bold.def", "font/default-3x5-bold.sff",
    "font/f-4x6.def", "font/f-4x6.sff", "font/debug.def",
    "font/f-6x9.def", "font/f-6x9.sff",
    "font/infofont.def", "font/Open_Sans.def",
    "font/Open_Sans/OpenSans-Regular.ttf", "font/Open_Sans/OpenSans-Bold.ttf",
    "font/Open_Sans/LICENSE.txt",
)
ANDROID_DEFAULTS = {
    "Config": {"WindowTitle": "The King of UTc", "Motif": "data/ikemen1/system.def"},
    "Video": {
        "RenderMode": "OpenGL ES 3.2", "GameWidth": 1280,
        "GameHeight": 720, "Fullscreen": 1, "EnableModel": 0,
        "EnableModelShadow": 0, "ExternalShaders": "",
    },
    "Debug": {
        "AllowDebugMode": 0, "AllowDebugKeys": 0,
        "StartStage": "stages/patio.def", "DumpLuaTables": 0,
    },
    # The desktop distribution has no SoundFont; the game only uses SND audio.
    "Sound": {"SoundFont": ""},
}
# SDL can enumerate a physical controller before the touch controller. The menu
# then assigns that controller's player config to P1, so every slot needs KOF
# bindings: overlay A/B/C/D -> SDL A/B/X/Y -> MUGEN x/a/y/b.
ANDROID_JOYSTICK_BINDINGS = {
    "GUID": "", "up": "DP_U", "down": "DP_D",
    "left": "DP_L", "right": "DP_R", "x": "A", "a": "B",
    "y": "X", "b": "Y", "c": "Not used", "z": "Not used",
    "d": "Not used", "w": "Not used", "start": "START",
    "menu": "BACK", "RumbleOn": 0,
}
RESOURCE_SUFFIXES = (
    "sff", "snd", "def", "cns", "zss", "air", "cmd", "dat", "fnt",
    "ttf", "webm", "mp3", "wav", "png", "sf2", "lua", "txt",
)
RESOURCE = re.compile(
    r"([A-Za-z0-9_./' -]+\.(?:" + "|".join(RESOURCE_SUFFIXES) + r"))$",
    re.IGNORECASE,
)
LUA_FILE = re.compile(r"['\"]([^'\"\n]+\.(?:lua|sff|def))['\"]")


def allowlist() -> tuple[str, ...]:
    paths = set(COMMON_FILES) | set(SYSTEM_FONT_FILES)
    for fighter in FIGHTERS:
        paths.update(f"chars/{fighter}/{p.format(id=fighter)}" for p in CHARACTER_FILES)
    for name in MOTIF_FONTS:
        paths.update(f"data/ikemen1/fonts/{name}.{ext}" for ext in ("def", "sff"))
    for name in STAGES:
        paths.add(f"stages/{name}.def")
        paths.add(f"stages/{name}.sff" if name == "patio" else f"stages/utc-real/{name}.sff")
    return tuple(sorted(paths))


def update_ini(text: str, section: str, values: dict[str, object]) -> str:
    """Change values in one INI section, retaining all other original content."""
    pattern = re.compile(r"(?ims)^\[" + re.escape(section) + r"\][^\r\n]*\r?\n(.*?)(?=^\[|\Z)")
    match = pattern.search(text)
    if not match:
        return text.rstrip() + f"\n\n[{section}]\n" + "".join(f"{k} = {v}\n" for k, v in values.items())
    body = match[1]
    for key, value in values.items():
        value = str(value)
        if "\n" in value or "\r" in value:
            raise ValueError(f"INI override contains a newline: {section}.{key}")
        key_pattern = re.compile(r"(?im)^(\s*)" + re.escape(key) + r"\s*=[^\r\n]*")
        if key_pattern.search(body):
            body = key_pattern.sub(lambda m: f"{m[1]}{key} = {value}", body)
        else:
            body = body.rstrip() + f"\n{key} = {value}\n"
    return text[:match.start(1)] + body + text[match.end(1):]


def selection_list() -> str:
    return (
        "; Android runtime roster. Optional desktop demonstration fighters are omitted.\n"
        "[Characters]\n"
        # utc_story.lua and route.lua use these exact two selection aliases.
        + "".join(f"{fighter if fighter in ('chava', 'hector') else fighter + '/' + fighter + '.def'}, stages/patio.def\n" for fighter in FIGHTERS)
        + "randomselect\n\n[ExtraStages]\n"
        + "".join(f"stages/{name}.def\n" for name in STAGES)
        + "\n[Options]\narcade.maxmatches = 6,1,1\nteam.maxmatches = 4,1,1\n"
        "timeattack.maxmatches = 6,1,1\nsurvival.maxmatches = -1\n\n[StoryMode]\n"
    )


def resolve_reference(output: Path, source: Path, reference: str) -> str | None:
    """Use the runtime search folders, with exact case required on Android."""
    reference = reference.replace("\\", "/")
    directories = (source.parent, output, output / "data", output / "font", output / "sound", output / "video")
    for directory in directories:
        candidates = [directory / reference]
        if reference.lower() == "common1.cns":
            candidates.append(directory / "common1.cns.zss")
        for path in candidates:
            path = path.resolve()
            if not path.is_relative_to(output) or not path.is_file():
                continue
            relative = path.relative_to(output)
            # Path.is_file() on the Windows host is insensitive to case.
            current = output
            if all((current := current / part).name in {p.name for p in current.parent.iterdir()} for part in relative.parts):
                return relative.as_posix()
    return None


def resource_references(source: Path) -> list[tuple[int, str]]:
    text = source.read_text(encoding="utf-8-sig")
    refs = []
    if source.suffix.lower() == ".lua":
        for line_no, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("--"):
                continue
            for match in LUA_FILE.finditer(line):
                reference = match[1]
                if reference.startswith(("external/", "data/", "stages/")):
                    refs.append((line_no, reference))
        return refs
    if source.suffix.lower() not in (".def", ".ini"):
        return refs
    section = ""
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.split(";", 1)[0].strip()
        if line.startswith("["):
            section = line[1:].split("]", 1)[0].lower()
            continue
        if "=" not in line:
            continue
        key, value = map(str.strip, line.split("=", 1))
        if section == "characters":
            continue
        for part in value.split(","):
            part = part.strip().strip('"')
            match = RESOURCE.fullmatch(part)
            if match:
                refs.append((line_no, match[1]))
    # Character/stage selection entries have no '=' delimiter.
    if source.name == "select.def":
        section = ""
        for line_no, line in enumerate(text.splitlines(), 1):
            line = line.split(";", 1)[0].strip()
            if line.startswith("["):
                section = line[1:].split("]", 1)[0].lower()
            elif line and section in ("characters", "extrastages"):
                for index, value in enumerate(line.split(",")):
                    value = value.strip()
                    if value.endswith(".def"):
                        refs.append((line_no, "chars/" + value if section == "characters" and not value.startswith("stages/") else value))
                    elif section == "characters" and index == 0 and value in FIGHTERS:
                        refs.append((line_no, f"chars/{value}/{value}.def"))
    return refs


def validate(output: Path, paths: tuple[str, ...]) -> list[dict[str, object]]:
    dependencies = []
    failures = []
    for relative in paths:
        source = output / relative
        if source.suffix.lower() not in (".def", ".ini", ".lua"):
            continue
        for line, reference in resource_references(source):
            resolved = resolve_reference(output, source, reference)
            if resolved is None:
                failures.append(f"{relative}:{line}: missing or incorrectly cased {reference}")
            else:
                dependencies.append({"source": relative, "line": line, "reference": reference, "resolved": resolved})
    if failures:
        raise ValueError("Invalid Android asset dependencies:\n" + "\n".join(failures))
    for fighter in FIGHTERS:
        if not (output / f"chars/{fighter}/{fighter}.def").is_file():
            raise ValueError(f"Missing campaign fighter: {fighter}")
    return dependencies


def verify_manifest(output: Path) -> dict[str, object]:
    manifest_data = (output / "asset-manifest.json").read_bytes()
    expected_version = hashlib.sha256(manifest_data).hexdigest()
    actual_version = (output / "content-version.txt").read_text(encoding="utf-8").strip()
    if actual_version != expected_version:
        raise ValueError("content-version.txt does not match the asset manifest")
    manifest = json.loads(manifest_data)
    if sorted(entry["path"] for entry in manifest["files"]) != list(allowlist()):
        raise ValueError("Asset manifest differs from the runtime allowlist")
    for entry in manifest["files"]:
        data = (output / entry["path"]).read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"Asset hash mismatch: {entry['path']}")
    return manifest


def package(output: Path, overrides: dict[str, dict[str, object]], archive: bool) -> dict[str, object]:
    output = output.resolve()
    scratch = (ROOT / "scratch").resolve()
    if output == scratch or not output.is_relative_to(scratch):
        raise ValueError(f"Generated output must be a child of {scratch}; refusing to alter {output}")
    paths = allowlist()
    missing = [p for p in paths if not (ROOT / p).is_file()]
    if missing:
        raise FileNotFoundError("Missing source assets:\n" + "\n".join(missing))
    # The absolute deletion target was validated above; source data is never removed.
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for relative in paths:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)

    config = (output / "save/config.ini").read_text(encoding="utf-8-sig")
    merged = {section: dict(values) for section, values in ANDROID_DEFAULTS.items()}
    player_count = re.search(r"(?im)^Players\s*=\s*(\d+)", config)
    players = int(overrides.get("Config", {}).get("Players", player_count[1] if player_count else 4))
    for player in range(1, max(1, min(players, 8)) + 1):
        merged[f"Joystick_P{player}"] = {"Joystick": player - 1, **ANDROID_JOYSTICK_BINDINGS}
    for section, values in overrides.items():
        merged.setdefault(section, {}).update(values)
    for section, values in merged.items():
        config = update_ini(config, section, values)
    (output / "save/config.ini").write_text(config, encoding="utf-8", newline="\n")
    (output / "data/select.def").write_text(selection_list(), encoding="utf-8", newline="\n")

    pixel = output / "data/ikemen1/fonts/Pixel.def"
    pixel.write_text(re.sub(r"(?im)^(File\s*=\s*)pixel\.sff\s*$", r"\1Pixel.sff", pixel.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")

    motif = output / "data/ikemen1/system.def"
    motif_text = motif.read_text(encoding="utf-8")
    motif_text = update_ini(motif_text, "Game Over Screen", {"enabled": 0, "storyboard": ""})
    # These music filenames are absent from the desktop distribution as well.
    motif_text = update_ini(motif_text, "Music", {key: "" for key in ("title.bgm", "select.bgm", "vs.bgm", "victory.bgm", "continue.bgm")})
    motif.write_text(motif_text, encoding="utf-8", newline="\n")
    credits = output / "data/ikemen1/credits.def"
    credits.write_text(update_ini(credits.read_text(encoding="utf-8"), "Scene 0", {"bgm": ""}), encoding="utf-8", newline="\n")

    dependencies = validate(output, paths)
    entries = []
    for relative in paths:
        data = (output / relative).read_bytes()
        entries.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "format": 1,
        "generator": "tools/package_android_assets.py",
        "fighters": list(FIGHTERS),
        "stages": list(STAGES),
        "files": entries,
        "file_count": len(entries),
        "total_bytes": sum(entry["bytes"] for entry in entries),
        "android_overrides": merged,
        "dependency_count": len(dependencies),
        "dependencies": dependencies,
        "excluded": ["Windows executable and DLLs", "optional KOF bases", "art sources", "tests and screenshots", "downloads and backups", "3D demonstration stages"],
    }
    manifest_data = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (output / "asset-manifest.json").write_bytes(manifest_data)
    content_version = hashlib.sha256(manifest_data).hexdigest()
    (output / "content-version.txt").write_text(content_version + "\n", encoding="utf-8", newline="\n")
    verify_manifest(output)
    if archive:
        archive_path = output.with_suffix(".zip")
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
            for relative in (*paths, "asset-manifest.json", "content-version.txt"):
                item = zipfile.ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.external_attr = 0o644 << 16
                zipped.writestr(item, (output / relative).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
        manifest["archive_bytes"] = archive_path.stat().st_size
        manifest["archive_sha256"] = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overrides", type=Path, help="JSON object: section -> INI key -> value, e.g. Android controller mappings")
    parser.add_argument("--zip", action="store_true", help="Also create a reproducible compressed ZIP next to the asset directory")
    parser.add_argument("--validate-only", action="store_true", help="Validate an existing package without modifying it")
    args = parser.parse_args()
    try:
        overrides = json.loads(args.overrides.read_text(encoding="utf-8-sig")) if args.overrides else {}
        if not isinstance(overrides, dict) or any(not isinstance(value, dict) for value in overrides.values()):
            raise ValueError("Overrides must be a JSON object mapping INI sections to key/value objects")
        if args.validate_only:
            dependencies = validate(args.output.resolve(), allowlist())
            verify_manifest(args.output.resolve())
            print(f"Validated {len(allowlist())} assets and {len(dependencies)} runtime references")
        else:
            manifest = package(args.output, overrides, args.zip)
            print(f"Packaged {manifest['file_count']} assets, {manifest['total_bytes'] / 1_000_000:.2f} MB, {manifest['dependency_count']} validated references")
            if "archive_bytes" in manifest:
                print(f"ZIP: {manifest['archive_bytes'] / 1_000_000:.2f} MB; SHA-256 {manifest['archive_sha256']}")
            print(args.output.resolve())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
