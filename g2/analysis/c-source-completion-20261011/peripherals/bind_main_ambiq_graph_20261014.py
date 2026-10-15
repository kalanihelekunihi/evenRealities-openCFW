#!/usr/bin/env python3
"""Compile the recovered Ambiq render, watchdog, and NOR lower graph."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-logger-bound.o"
PRIOR = OUT / "logger-graph-current-receipt.json"
OBJDIR = OUT / "ambiq-current"
BOUND = OUT / "apollo-main-ambiq-graph.o"
RECEIPT = OUT / "ambiq-graph-current-receipt.json"
FOLDERS = (
    "ambiq_buffer_handlers_candidate_20261014",
    "ambiq_clip_change_candidate_20261014",
    "lv_style_removed_candidate_20261014",
    "npmx_watchdog_candidate_20261014",
    "norflash_alias_candidates_20261014",
)
ORACLES = {
    "verify_npmx_watchdog_kick_native_20261014.py": "PASS_NPMX_WATCHDOG_KICK_NATIVE 20",
    "verify_ambiq_clip_change_native_20261014.py": "PASS_AMBIQ_CLIP_CHANGE_NATIVE 72",
    "verify_ambiq_buffer_handlers_native_20261014.py": "PASS_AMBIQ_BUFFER_HANDLERS_NATIVE 74 24",
    "verify_ambiq_buffer_base_native_20261014.py": "PASS_AMBIQ_BUFFER_BASE_NATIVE 64",
    "verify_ambiq_buffer_render_native_20261014.py": "PASS_AMBIQ_BUFFER_RENDER_NATIVE 168",
    "verify_ambiq_buffer_coherency_native_20261014.py": "PASS_AMBIQ_BUFFER_COHERENCY_NATIVE 54",
    "verify_ambiq_buffer_sizes_native_20261014.py": "PASS_AMBIQ_BUFFER_SIZES_NATIVE 840",
    "verify_ambiq_buffer_blend_native_20261014.py": "PASS_AMBIQ_BUFFER_BLEND_NATIVE 84",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, option):
    output = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3
            and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_LOGGER_GRAPH_COMPILE"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 587
    # The native 0x5228b0 lower was recovered in a later wave and is linked
    # separately against this sealed 68-unit base.
    sources = sorted(source for folder in FOLDERS
                     for source in (G2 / "components/main" / folder).glob("*.c")
                     if source.name != "nema_float_translate.c")
    assert len(sources) == 68 and len({source.stem for source in sources}) == 68
    OBJDIR.mkdir(parents=True, exist_ok=True)
    objects = []
    rows = []
    seen = defined(BASE)
    for source in sources:
        obj = OBJDIR / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        names = defined(obj)
        assert names and not names & seen, (source, names & seen)
        seen |= names
        objects.append(obj)
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                     "defined": sorted(names)})
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert defined(BOUND) == seen
    assert len(before - after) == 15 and len(after - before) == 11 and len(after) == 583
    oracles = []
    for name, expected in ORACLES.items():
        path = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True, check=True)
        assert result.stdout.strip().splitlines()[-1] == expected, (name, result.stdout)
        oracles.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                        "observed": expected})
    receipt = {
        "status": "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows, "source_unit_count": len(rows),
        "bounded_oracles_rerun": oracles,
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Eleven GPU/Nema lower calls remain real source contracts",
                   "Bounded native checks do not cover all draw modes or live device behavior",
                   "Final image placement and hardware operation remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "units": len(rows),
                      "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
