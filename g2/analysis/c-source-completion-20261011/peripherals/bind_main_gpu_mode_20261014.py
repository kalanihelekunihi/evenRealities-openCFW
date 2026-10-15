#!/usr/bin/env python3
"""Build three native-checked Apollo GPU mode C bodies into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-nema-float-bound.o"
PRIOR = OUT / "nema-float-translate-current-receipt.json"
SOURCE = G2 / "components/main/ambiq_gpu_mode_candidate_20261014/gpu_mode.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ambiq_gpu_mode_native_20261014.py"
RESULT = ORACLE.with_name("ambiq-gpu-mode-native-results.json")
OBJECT = OUT / "gpu-mode-current.o"
BOUND = OUT / "apollo-main-gpu-mode-bound.o"
RECEIPT = OUT / "gpu-mode-current-receipt.json"
PROVIDERS = {"display_driver_gpu_mode_lower_4b06c0",
             "display_driver_gpu_mode_4b0730",
             "display_driver_gpu_enable_4b0748"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_NEMA_FLOAT_TRANSLATE_C"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 569 and PROVIDERS <= before
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_AMBIQ_GPU_MODE_NATIVE 408"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_AMBIQ_GPU_MODE_NATIVE"
    assert oracle["cases"] == 408 and oracle["source_sha256"] == sha(SOURCE)
    assert set(oracle["native_bodies"]) == PROVIDERS
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(OBJECT)],
                   cwd=ROOT, check=True)
    assert nm(OBJECT, "--defined-only") == PROVIDERS
    assert nm(OBJECT, "-u") <= nm(BASE, "--defined-only") | before
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert after == before - PROVIDERS and len(after) == 566
    receipt = {
        "status": "PASS_CURRENT_MAIN_GPU_MODE_C",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "native_bodies": oracle["native_bodies"],
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "result": str(RESULT.relative_to(ROOT)), "result_sha256": sha(RESULT),
                           "cases": oracle["cases"]},
        "providers": sorted(PROVIDERS),
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_added": sorted(after - before),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Default-unit and Nema mode children are entry-cut in bounded native comparison",
                   "Wrapper return registers are not part of their C caller contracts",
                   "Concurrent GPU state mutation, final placement, and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
