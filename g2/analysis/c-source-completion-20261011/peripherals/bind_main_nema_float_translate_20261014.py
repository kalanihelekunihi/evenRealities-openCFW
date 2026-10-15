#!/usr/bin/env python3
"""Build native-checked Nema float translation C into current Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-nema-rectangle-bound.o"
PRIOR = OUT / "nema-rectangle-alias-receipt.json"
SOURCE = G2 / "components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_translate.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_nema_float_translate_native_20261014.py"
RESULT = ORACLE.with_name("nema-float-translate-native-results.json")
OBJECT = OUT / "nema-float-translate-current.o"
BOUND = OUT / "apollo-main-nema-float-bound.o"
RECEIPT = OUT / "nema-float-translate-current-receipt.json"
SYMBOL = "display_driver_nema_float_translate_5228b0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_NEMA_RECTANGLE_ALIAS"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 570 and SYMBOL in before
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_NEMA_FLOAT_TRANSLATE_NATIVE 512"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_NEMA_FLOAT_TRANSLATE_NATIVE"
    assert oracle["cases"] == 512 and oracle["source_sha256"] == sha(SOURCE)
    assert oracle["native_body_start"] == "0x5228b0"
    assert oracle["native_body_end_inclusive"] == "0x522915"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(OBJECT)],
                   cwd=ROOT, check=True)
    assert nm(OBJECT, "--defined-only") == {SYMBOL}
    assert nm(OBJECT, "-u") <= nm(BASE, "--defined-only")
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert after == before - {SYMBOL} and len(after) == 569
    receipt = {
        "status": "PASS_CURRENT_MAIN_NEMA_FLOAT_TRANSLATE_C",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "native_body_start": oracle["native_body_start"],
        "native_body_end_inclusive": oracle["native_body_end_inclusive"],
        "native_body_sha256": oracle["native_body_sha256"],
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "result": str(RESULT.relative_to(ROOT)), "result_sha256": sha(RESULT),
                           "cases": oracle["cases"]},
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_added": sorted(after - before),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Command allocator and Nema child call are entry-cut in the 512-case oracle",
                   "Hardware command-buffer ownership, final placement, and device behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
