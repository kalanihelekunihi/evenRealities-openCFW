#!/usr/bin/env python3
"""Build native-checked GPU position and Nema select C bodies into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-gpu-mode-bound.o"
PRIOR = OUT / "gpu-mode-current-receipt.json"
DIR = G2 / "components/main/ambiq_gpu_position_candidate_20261014"
STEMS = ("position", "nema_select")
OBJECTS = OUT / "gpu-position-current"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ambiq_gpu_position_native_20261014.py"
RESULT = ORACLE.with_name("ambiq-gpu-position-native-results.json")
BOUND = OUT / "apollo-main-gpu-position-bound.o"
RECEIPT = OUT / "gpu-position-current-receipt.json"
PROVIDERS = {"display_driver_gpu_position_4b1b48", "display_driver_nema_select_522a16"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_GPU_MODE_C"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 566 and PROVIDERS <= before
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_AMBIQ_GPU_POSITION_NATIVE 198"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_AMBIQ_GPU_POSITION_NATIVE" and oracle["cases"] == 198
    assert set(oracle["native_bodies"]) == PROVIDERS
    OBJECTS.mkdir(parents=True, exist_ok=True)
    rows = []
    objects = []
    definitions = set()
    for stem in STEMS:
        source = DIR / (stem + ".c")
        assert sha(source) == oracle["source_sha256"][source.name]
        obj = OBJECTS / (stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        names = nm(obj, "--defined-only")
        assert len(names) == 1 and not names & definitions
        definitions |= names
        objects.append(obj)
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                     "defined": sorted(names)})
    assert definitions == PROVIDERS
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert after == before - PROVIDERS and len(after) == 564
    receipt = {
        "status": "PASS_CURRENT_MAIN_GPU_POSITION_C",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows, "native_bodies": oracle["native_bodies"],
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "result": str(RESULT.relative_to(ROOT)), "result_sha256": sha(RESULT),
                           "cases": oracle["cases"]},
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Float translation, rectangle, and Nema register child effects are entry-cut",
                   "Product-state initialization, final placement, and hardware GPU behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
