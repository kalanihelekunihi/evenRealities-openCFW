#!/usr/bin/env python3
"""Bind pinned Cordio ECC and uECC C providers to pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-smp-actions-current-receipt.json"
PROVIDER = G2 / "analysis/c-source-completion-20261011/peripherals/root-cordio-ecc-round422/ecc-source-receipt.json"
CORDIO = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
UECC = CORDIO.parent / "uecc/uECC.c"
SEC = CORDIO / "ble-host/sources/sec/uecc/sec_ecc.c"
BOUND = OUT / "apollo-main-pool-state-cordio-ecc-bound.o"
RECEIPT = OUT / "pool-state-cordio-ecc-current-receipt.json"
NAME = "SecEccGenSharedSecret"


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
    provider = json.loads(PROVIDER.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_SMP_ACTIONS_C"
    assert provider["removed_imports"] == [NAME]
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(["-u"], prior)
    assert NAME in before
    inc = [G2 / "analysis/c-source-completion-20261011/peripherals/root-cordio-ecc-round422/freestanding_include",
           G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"]
    inc += [CORDIO / p for p in ("ble-host/include", "ble-host/sources/sec/common",
                                  "ble-host/sources/sec/uecc", "ble-host/sources/stack/smp",
                                  "ble-host/sources/stack/cfg", "ble-host/sources/stack/dm",
                                  "wsf/include", "wsf/sources", "wsf/sources/util",
                                  "wsf/sources/port/freertos")]
    inc += [CORDIO.parent / "uecc"]
    objects, units = [], []
    all_defs = global_defs(prior)
    for name, source in (("sec-ecc", SEC), ("uecc", UECC)):
        obj = OUT / f"{name}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Wno-unused-parameter", *(f"-I{x}" for x in inc),
                        "-c", str(source), "-o", str(obj)], check=True)
        definitions = global_defs(obj)
        assert definitions and not (definitions & all_defs), (name, definitions & all_defs)
        all_defs |= definitions
        objects.append(obj)
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                      "global_definitions": len(definitions)})
    assert NAME in all_defs
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - {NAME}
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_ECC_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "provider_receipt": str(PROVIDER.relative_to(ROOT)), "provider_receipt_sha256": sha(PROVIDER),
               "source_units": units, "imports_resolved": [NAME], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned Cordio and uECC source compiles, but the stock ECC variant, key generation, RNG callback and runtime behavior remain unverified.",
                         "Other Main source and placement gates remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
