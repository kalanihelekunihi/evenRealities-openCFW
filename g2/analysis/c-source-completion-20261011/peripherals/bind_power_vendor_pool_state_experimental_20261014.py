#!/usr/bin/env python3
"""Build source-owned Apollo power projection into pooled Main."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-smp-sc-rows-current-receipt.json"
POWER = G2 / "components/audio/power_vendor_candidate"
NAMES = ("power.c", "power_descriptor_native.c", "power_product_native.c",
         "power_callbacks_native.c", "power_gpu_transition_native.c")
VERIFY_DIR = G2 / "analysis/c-source-completion-20261011/peripherals"
CHECKS = {"verify_power_descriptor_native.py": "PASS_POWER_DESCRIPTOR_NATIVE_C 78",
          "verify_power_enable_connected.py": "PASS_POWER_ENABLE_CONNECTED 56",
          "verify_power_disable_wait_entry.py": "PASS_POWER_DISABLE_WAIT_ENTRY 14",
          "verify_power_gpu_transition_effects.py": "PASS_POWER_GPU_TRANSITION_EFFECTS 18"}
BOUND = OUT / "apollo-main-pool-state-power-vendor-bound.o"
RECEIPT = OUT / "pool-state-power-vendor-current-receipt.json"
RESOLVED = {"am_hal_pwrctrl_periph_disable", "am_hal_pwrctrl_periph_enable",
            "audio_power_peripheral_off", "audio_power_peripheral_on",
            "stock_disable", "stock_enable", "stock_peripheral_enable"}


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
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_SMP_SC_ROW_STORAGE_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    checks = []
    for name, expected in CHECKS.items():
        script = VERIFY_DIR / name
        run = subprocess.run([sys.executable, str(script)], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        line = run.stdout.strip().splitlines()[-1]
        assert line == expected, (name, line)
        checks.append({"script": str(script.relative_to(ROOT)), "script_sha256": sha(script),
                       "output": line})
    objects, units = [], []
    definitions = global_defs(prior)
    for name in NAMES:
        source = POWER / name
        obj = OUT / f"power-{source.stem}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        current = global_defs(obj)
        assert current and not (current & definitions), (name, current & definitions)
        definitions |= current
        objects.append(obj)
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                      "global_definitions": len(current)})
    assert RESOLVED <= definitions
    before = symbols(["-u"], prior)
    assert RESOLVED <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - RESOLVED
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_APOLLO_POWER_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "source_units": units, "bounded_native_checks": checks,
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Bounded checks cover descriptor/enable/disable/GPU branches, not the entire native power function or all product states.",
                         "MMIO timing, IRQ/clock interleaving, final placement and physical power transitions remain unverified."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
