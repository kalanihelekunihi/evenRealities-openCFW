#!/usr/bin/env python3
"""Build six pinned Cordio SMP action source units into pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-smp-tables-current-receipt.json"
TABLES = G2 / "analysis/c-source-completion-20261011/peripherals/smp_tables"
CORDIO = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
NAMES = ("smp_act", "smp_sc_act", "smpi_act", "smpi_sc_act", "smpr_act", "smpr_sc_act")
BOUND = OUT / "apollo-main-pool-state-smp-actions-bound.o"
RECEIPT = OUT / "pool-state-smp-actions-current-receipt.json"


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
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_SMP_TABLES_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    include = [CORDIO / p for p in ("ble-host/include", "ble-host/sources/stack/smp",
                                   "ble-host/sources/stack/cfg", "wsf/include", "wsf/sources",
                                   "wsf/sources/port/freertos", "ble-host/sources/stack/dm")]
    include += [G2 / "components/bootloader/filesystem/freestanding_include"]
    objects, units = [], []
    all_defs = global_defs(prior)
    for name in NAMES:
        source = TABLES / f"candidate_{name}.c"
        upstream = CORDIO / f"ble-host/sources/stack/smp/{name}.c"
        assert upstream.is_file()
        obj = OUT / f"smp-{name}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Wno-unused-parameter",
                        *(f"-I{x}" for x in include), "-c", str(source), "-o", str(obj)], check=True)
        definitions = global_defs(obj)
        assert definitions and not (definitions & all_defs), (name, definitions & all_defs)
        all_defs |= definitions
        objects.append(obj)
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                      "pinned_upstream": str(upstream.relative_to(ROOT)), "pinned_upstream_sha256": sha(upstream),
                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                      "global_definitions": len(definitions)})
    before = symbols(["-u"], prior)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    removed = sorted(before - after)
    added = sorted(after - before)
    assert len(removed) >= 80
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_SMP_ACTIONS_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "source_units": units, "imports_resolved": removed, "imports_added": added,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned Cordio SMP action bodies compile and link, but stock action body and full pairing behavior equivalence remain unproved.",
                         "Remaining SMP child dependencies, product state, final placement and hardware operation remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), len(removed), len(added), sha(RECEIPT))


if __name__ == "__main__":
    main()
