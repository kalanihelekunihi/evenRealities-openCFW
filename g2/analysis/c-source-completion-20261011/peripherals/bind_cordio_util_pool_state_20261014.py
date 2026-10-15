#!/usr/bin/env python3
"""Link pinned Cordio string and 128-bit utilities into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-bda-current-receipt.json"
CORDIO = ROOT / "third-party/upstream/cordio"
WSTR = CORDIO / "wsf/sources/util/wstr.c"
CALC = CORDIO / "wsf/sources/util/calc128.c"
WSTR_CHECK = G2 / "build/c-firmware/cordio-wstr-native-round1013/receipt.json"
CALC_CHECK = G2 / "build/c-firmware/cordio-calc128-native-round1015/receipt.json"
BOUND = OUT / "apollo-main-pool-state-cordio-util-bound.o"
RECEIPT = OUT / "pool-state-cordio-util-current-receipt.json"
PIN = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    wstr_check = json.loads(WSTR_CHECK.read_text())
    calc_check = json.loads(CALC_CHECK.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_CORDIO_BDA_SOURCE_C"
    assert wstr_check["status"] == "PASS_PINNED_CORDIO_WSTR_NATIVE"
    assert calc_check["status"] == "PASS_PINNED_CORDIO_CALC128_NATIVE"
    assert wstr_check["source_sha256"] == sha(WSTR)
    assert calc_check["source_sha256"] == sha(CALC)
    assert wstr_check["sizes"] == [0, 1, 6, 16, 31]
    assert set(calc_check["native_entries"]) == {"Calc128Cpy", "Calc128Cpy64"}
    assert subprocess.check_output(["git", "-C", str(CORDIO), "rev-parse", "HEAD"],
                                   text=True).strip() == PIN
    objects = []
    for source, label in ((WSTR, "wstr"), (CALC, "calc128")):
        obj = OUT / f"cordio-{label}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                        "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-I" + str(G2 / "config-recovered/cordio/g2-compat-include"),
                        "-I" + str(CORDIO / "wsf/include"),
                        "-I" + str(CORDIO / "platform/include"),
                        "-c", str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    defined = names(original, "-g", "--defined-only")
    new_defined = set().union(*(names(obj, "-g", "--defined-only") for obj in objects))
    assert not new_defined & defined
    resolved = new_defined & before
    assert resolved == {"WStrReverse", "WStrReverseCpy", "Calc128Cpy",
                        "Calc128Cpy64", "calc128Zeros"}
    assert set().union(*(names(obj, "-u") for obj in objects)) <= defined
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), *map(str, objects),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - resolved
    receipt = {
        "status": "PASS_POOLED_MAIN_PINNED_CORDIO_UTIL_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "upstream_commit": PIN,
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (WSTR, CALC)},
        "native_check_receipts": {str(p.relative_to(ROOT)): sha(p) for p in
                                  (WSTR_CHECK, CALC_CHECK)},
        "pool_abi_objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "imports_resolved": sorted(resolved),
        "imports_added": [],
        "additional_definitions_without_native_match": sorted(new_defined - resolved),
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Native checks cover listed reverse/copy cases, not all utility functions or input domains.",
                  "Other Main imports, final placement and device execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
