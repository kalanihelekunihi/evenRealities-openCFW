#!/usr/bin/env python3
"""Build the pinned, recovered-config nanopb runtime for Apollo main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
UPSTREAM = ROOT / "third-party/upstream/nanopb"
COMMIT = "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
OUT = G2 / "build/c-firmware/20261016/main-nanopb-pinned"
assert subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"],
                               text=True).strip() == COMMIT
assert (UPSTREAM / "pb_decode.c").is_file()
OUT.mkdir(parents=True, exist_ok=True)

flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
         "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
         '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
         "-I", str(CONFIG), "-I", str(UPSTREAM)]
objects = []
for stem in ("pb_common", "pb_decode", "pb_encode"):
    target = OUT / f"{stem}.o"
    subprocess.run(["clang", *flags, "-c", str(UPSTREAM / f"{stem}.c"),
                    "-o", str(target)], check=True)
    objects.append(target)
archive = OUT / "libg2_nanopb.a"
subprocess.run(["arm-none-eabi-ar", "rcs", str(archive),
                *(str(p) for p in objects)], check=True)
symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only",
                                   str(archive)], text=True)
for required in ("pb_decode", "pb_decode_ex", "pb_encode", "pb_field_iter_begin"):
    assert any(line.rstrip().endswith(" " + required) for line in symbols.splitlines()), required

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

receipt = {"status": "PASS_COMPILED_MAIN_NANOPB_PINNED_C",
           "upstream_commit": COMMIT,
           "upstream_sources": {str((UPSTREAM / f"{stem}.c").relative_to(ROOT)):
                                digest(UPSTREAM / f"{stem}.c")
                                for stem in ("pb_common", "pb_decode", "pb_encode")},
           "config": {str(p.relative_to(ROOT)): digest(p)
                      for p in (CONFIG / "pb_g2_options.h", CONFIG / "pb_g2_system.h")},
           "objects": {str(p.relative_to(ROOT)): digest(p) for p in objects},
           "archive": str(archive.relative_to(ROOT)),
           "archive_sha256": digest(archive),
           "limits": "Cortex-M4 archive build only; generated descriptors and stock behavior not validated"}
output = OUT / "receipt.json"
output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print(receipt["status"], len(objects), digest(output))
