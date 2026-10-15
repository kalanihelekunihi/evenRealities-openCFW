#!/usr/bin/env python3
"""Bind native-checked page layer callback to the current Main graph."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "freetype-gzip-current-receipt.json"
BASE = OUT / "apollo-main-freetype-gzip-bound.o"
SOURCE = G2 / "components/main/page_layer_candidate_20261014/page_layer.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_page_layer_native_20261014.py"
RESULT = ORACLE.with_name("page-layer-native-results.json")
OBJECT = OUT / "page-layer-current.o"
BOUND = OUT / "apollo-main-page-layer-bound.o"
RECEIPT = OUT / "page-layer-current-receipt.json"
PROVIDER = "audio_uart_page_44e3ca"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_FREETYPE_GZIP_C_LINK"
    assert sha(BASE) == prior["output_sha256"]
    before = names(BASE, "-u")
    assert len(before) == 558 and PROVIDER in before
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_PAGE_LAYER_NATIVE 210"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_PAGE_LAYER_NATIVE" and oracle["cases"] == 210
    assert sha(SOURCE) == oracle["source_sha256"]
    assert oracle["native_body_start"] == "0x44e3ca"
    assert oracle["native_body_end_inclusive"] == "0x44e3f7"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(OBJECT)],
                   cwd=ROOT, check=True)
    assert names(OBJECT, "-g", "--defined-only") == {PROVIDER}
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = names(BOUND, "-u")
    assert after == before - {PROVIDER} and len(after) == 557
    receipt = {
        "status": "PASS_CURRENT_MAIN_PAGE_LAYER_C",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "native_body_start": oracle["native_body_start"],
        "native_body_end_inclusive": oracle["native_body_end_inclusive"],
        "native_body_sha256": oracle["native_body_sha256"],
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
