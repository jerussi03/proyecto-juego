"""Compatibility entry point for the Alex sprite build.

The former builder blended isolated AI illustrations and produced disconnected
body parts between frames. Keep this filename for existing workflows, but
delegate all builds to the hand-authored pose renderer.
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("build_alex_sprites.py")), run_name="__main__")
