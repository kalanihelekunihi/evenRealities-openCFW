#!/usr/bin/env python3
"""Compile and bind four pinned Cordio SMP state-machine source tables."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-vendor-complete-current-receipt.json"
TABLES = G2 / "analysis/c-source-completion-20261011/peripherals/smp_tables"
VERIFY = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ble_smp_tables.py"
CORDIO = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
NAMES = ("smpi_sm", "smpi_sc_sm", "smpr_sm", "smpr_sc_sm")
SYMBOLS = ("audio_ble_smpi_legacy_table", "audio_ble_smpi_sc_table",
           "audio_ble_smpr_legacy_table", "audio_ble_smpr_sc_table")
BOUND = OUT / "apollo-main-pool-state-smp-tables-bound.o"
RECEIPT = OUT / "pool-state-smp-tables-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def global_defs(p):
    return {parts[2] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(p)], text=True).splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def main():
    base = json.loads(BASE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_VENDOR_EVENT_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    native = subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout.strip()
    assert re.fullmatch(r"PASS_BLE_SMP_TABLES_NAMED 107 rows 158 actions 4 common tables", native)
    include = [CORDIO / p for p in ("ble-host/include", "ble-host/sources/stack/smp",
                                   "ble-host/sources/stack/cfg", "wsf/include", "wsf/sources",
                                   "wsf/sources/port/freertos", "ble-host/sources/stack/dm")]
    include += [G2 / "components/bootloader/filesystem/freestanding_include"]
    objects = []
    sources = []
    all_defs = global_defs(prior)
    for name, symbol in zip(NAMES, SYMBOLS):
        source = TABLES / f"candidate_{name}.c"
        obj = OUT / f"smp-{name}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Wno-unused-parameter",
                        *(f"-I{x}" for x in include), "-c", str(source), "-o", str(obj)], check=True)
        definitions = global_defs(obj)
        assert symbol in definitions and not (definitions & all_defs), (name, definitions & all_defs)
        all_defs |= definitions
        objects.append(obj)
        sources.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                        "global_definitions": len(definitions)})
    before = symbols(["-u"], prior)
    assert set(SYMBOLS) <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    removed = sorted(before - after)
    added = sorted(after - before)
    assert set(SYMBOLS) <= set(removed)
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_SMP_TABLES_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "native_verifier": str(VERIFY.relative_to(ROOT)), "native_verifier_sha256": sha(VERIFY),
               "native_verifier_output": native, "source_units": sources,
               "imports_resolved": removed, "imports_added": added,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Native comparison covers state row bytes and action names, not action body behavior or whole pairing runtime.",
                         "New SMP action/runtime dependencies remain unresolved; source table addresses and final image layout are not established."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), len(removed), len(added), sha(RECEIPT))


if __name__ == "__main__":
    main()
