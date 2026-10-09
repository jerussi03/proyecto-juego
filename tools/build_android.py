#!/usr/bin/env python3
"""Build the self-contained UTC APK from pinned native libraries and game assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
WORK = ROOT / "scratch/android"
DIST = ROOT / "dist"
VERSION = "1.0.0"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args: list[str | Path], *, env=None) -> None:
    subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env, check=True)


def download(url: str, destination: Path, expected: str) -> None:
    if destination.exists() and sha256(destination) == expected:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    print("Downloading pinned Android engine:", url, flush=True)
    request = urllib.request.Request(url, headers={"User-Agent": "TheKingOfUTc-build"})
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as out:
        shutil.copyfileobj(response, out)
    actual = sha256(temporary)
    if actual != expected:
        temporary.unlink()
        raise RuntimeError(f"Engine checksum mismatch: expected {expected}, received {actual}")
    temporary.replace(destination)


def native_libraries(lock: dict, engine_apk: Path | None, native_archive: Path | None) -> None:
    target = WORK / "native-libs/arm64-v8a"
    expected = lock["libraries"]
    unexpected = {path.relative_to(WORK / "native-libs").as_posix()
                  for path in (WORK / "native-libs").rglob("*.so")
                  if path.relative_to(WORK / "native-libs").as_posix()
                  not in {"arm64-v8a/" + name for name in expected}}
    if unexpected:
        raise RuntimeError("Unexpected staged native libraries: " + ", ".join(sorted(unexpected)))
    if all((target / name).is_file() and sha256(target / name) == digest
           for name, digest in expected.items()):
        return
    if native_archive:
        source = native_archive
        prefix = "arm64-v8a/"
    elif engine_apk:
        source = engine_apk
        prefix = "lib/arm64-v8a/"
    else:
        source = ROOT / "downloads/android/engine-android-arm64.zip"
        download(lock["native_archive_url"], source, lock["native_archive_sha256"])
        prefix = "arm64-v8a/"
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        for name, digest in expected.items():
            content = archive.read(prefix + name)
            if hashlib.sha256(content).hexdigest() != digest:
                raise RuntimeError("Unexpected native library: " + name)
            (target / name).write_bytes(content)


def bundle_native(lock: dict) -> Path:
    """Publish exactly the linked libraries and license, without an SDK or caches."""
    destination = DIST / "engine-android-arm64.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        sources = [(WORK / "native-libs/arm64-v8a" / name, "arm64-v8a/" + name)
                   for name in sorted(lock["libraries"])]
        sources += [(ANDROID / "ENGINE-LICENSES.txt", "ENGINE-LICENSES.txt")]
        for source, name in sources:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return destination


def verify_apk_content(apk: Path, lock: dict) -> None:
    """Check the actual packaged bytes, not only the pre-build staging directory."""
    assets = ROOT / "scratch/android-game-assets"
    manifest = json.loads((assets / "asset-manifest.json").read_text(encoding="utf-8"))
    expected_assets = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    expected_assets.update({name: sha256(assets / name)
                            for name in ("asset-manifest.json", "content-version.txt")})
    with zipfile.ZipFile(apk) as archive:
        actual_assets = {name.removeprefix("assets/") for name in archive.namelist()
                         if name.startswith("assets/") and not name.endswith("/")}
        if actual_assets != set(expected_assets):
            raise RuntimeError("The APK's assets differ from the permitted game files")
        for name, digest in expected_assets.items():
            if hashlib.sha256(archive.read("assets/" + name)).hexdigest() != digest:
                raise RuntimeError("APK asset checksum mismatch: " + name)
        actual_libraries = {name for name in archive.namelist()
                            if name.startswith("lib/") and not name.endswith("/")}
        if actual_libraries != {"lib/arm64-v8a/" + name for name in lock["libraries"]}:
            raise RuntimeError("The APK contains unexpected native libraries or ABIs")
        for name, digest in lock["libraries"].items():
            if hashlib.sha256(archive.read("lib/arm64-v8a/" + name)).hexdigest() != digest:
                raise RuntimeError("APK native checksum mismatch: " + name)
    print(f"APK verified: {len(expected_assets)} assets and {len(lock['libraries'])} pinned ARM64 libraries")


def signing_key(java_bin: Path, env: dict) -> tuple[Path, dict]:
    key_dir = ANDROID / ".signing"
    key_dir.mkdir(parents=True, exist_ok=True)
    key = key_dir / "utc-release.p12"
    password_file = key_dir / "password.txt"
    if key.exists() and not password_file.exists():
        raise RuntimeError("Signing key exists but its password is missing; restore the private password.")
    if not password_file.exists():
        password_file.write_text(secrets.token_urlsafe(36), encoding="ascii")
    env = dict(env, UTC_SIGNING_PASSWORD=password_file.read_text(encoding="ascii").strip())
    if not key.exists():
        run([java_bin / "keytool.exe", "-genkeypair", "-keystore", key,
             "-storetype", "PKCS12", "-storepass:env", "UTC_SIGNING_PASSWORD",
             "-alias", "utc", "-keyalg", "RSA", "-keysize", "3072", "-validity", "10000",
             "-dname", "CN=The King of UTc, O=UTC, C=MX"], env=env)
    return key, env


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-apk", type=Path, help="Use the pinned libraries in an existing official/game APK")
    parser.add_argument("--native-archive", type=Path, help="Use the release's engine-android-arm64.zip offline")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare and verify inputs without Gradle")
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(exist_ok=True)
    lock = json.loads((ANDROID / "engine.lock.json").read_text(encoding="utf-8"))
    native_libraries(lock, args.engine_apk, args.native_archive)
    native_zip = bundle_native(lock)
    if sha256(native_zip) != lock["native_archive_sha256"]:
        raise RuntimeError("Native archive is not reproducible with the locked inputs")
    run([sys.executable, ROOT / "tools/package_android_assets.py", "--output", ROOT / "scratch/android-game-assets"])
    if args.prepare_only:
        return
    env = dict(os.environ)
    sdk = Path(env.get("ANDROID_HOME", env.get("ANDROID_SDK_ROOT", "")))
    if not (sdk / "platforms/android-36").is_dir():
        raise RuntimeError("Set ANDROID_HOME to an SDK with platform android-36 and build-tools 36.1.0")
    java = shutil.which("java")
    java_bin = Path(env["JAVA_HOME"]) / "bin" if env.get("JAVA_HOME") else Path(java or "").resolve().parent
    env["JAVA_HOME"] = str(java_bin.parent)
    env["ANDROID_HOME"] = str(sdk)
    run([ANDROID / "gradlew.bat", "--no-daemon", "--console=plain", "-p", ANDROID, "assembleRelease"], env=env)
    unsigned = ANDROID / "app/build/outputs/apk/release/app-release-unsigned.apk"
    verify_apk_content(unsigned, lock)
    signed = DIST / f"TheKingOfUTc-Android-v{VERSION}.apk"
    key, signing_env = signing_key(java_bin, env)
    build_tools = sdk / "build-tools/36.1.0"
    run([build_tools / "apksigner.bat", "sign", "--ks", key, "--ks-key-alias", "utc",
         "--ks-pass", "env:UTC_SIGNING_PASSWORD", "--out", signed, unsigned], env=signing_env)
    run([build_tools / "apksigner.bat", "verify", "--verbose", "--print-certs", signed], env=env)
    run([build_tools / "zipalign.exe", "-c", "-P", "16", "4", signed], env=env)
    report = {
        "version": VERSION, "apk": signed.name, "apk_bytes": signed.stat().st_size,
        "apk_sha256": sha256(signed), "native_archive_sha256": sha256(native_zip),
        "engine_commit": lock["engine_commit"], "min_android_api": 34, "abi": "arm64-v8a",
        "content_version": (ROOT / "scratch/android-game-assets/content-version.txt").read_text().strip(),
    }
    (DIST / "android-build.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (DIST / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in (signed, native_zip)
                + ((DIST / "src_ffmpeg.tar.gz",) if (DIST / "src_ffmpeg.tar.gz").exists() else ())),
        encoding="ascii")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
