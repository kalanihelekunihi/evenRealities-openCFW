#!/usr/bin/env python3
"""Bind the native-checked Nema mode encoder to the current Main graph."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "nema-cache-current-receipt.json"
BASE = OUT / "apollo-main-nema-cache-bound.o"
SOURCE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/nema_mode.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ambiq_nema_mode_native_20261014.py"
RESULT = ORACLE.with_name("ambiq-nema-mode-native-results.json")
OBJECT = OUT / "nema-mode-current.o"
BOUND = OUT / "apollo-main-nema-mode-bound.o"
RECEIPT = OUT / "nema-mode-current-receipt.json"
PROVIDER = "display_driver_nema_mode_513924"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_NEMA_CACHE_C"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 563 and PROVIDER in before
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_AMBIQ_NEMA_MODE_NATIVE 2420"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_AMBIQ_NEMA_MODE_NATIVE" and oracle["cases"] == 2420
    assert sha(SOURCE) == oracle["source_sha256"]
    assert oracle["native_body_sha256"] == "e79ac2b12d6efcbb7291339da418ec904f2b1819fae4727a0c959477896014fc"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(OBJECT)],
                   cwd=ROOT, check=True)
    exports = subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(OBJECT)], text=True)
    assert {line.split()[-1] for line in exports.splitlines() if line.split()} == {PROVIDER}
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert after == before - {PROVIDER} and len(after) == 562
    receipt = {
        "status": "PASS_CURRENT_MAIN_NEMA_MODE_C",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "native_body_start": oracle["native_body_start"],
        "native_body_end_inclusive": oracle["native_body_end_inclusive"],
        "native_body_sha256": oracle["native_body_sha256"],
        "stock_sha256": oracle["stock_sha256"],
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "result": str(RESULT.relative_to(ROOT)), "result_sha256": sha(RESULT),
                           "cases": oracle["cases"]},
        "imports_resolved": [PROVIDER], "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": oracle["limits"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
