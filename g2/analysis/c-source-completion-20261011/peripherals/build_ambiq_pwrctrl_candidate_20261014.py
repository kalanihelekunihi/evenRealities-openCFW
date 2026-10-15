#!/usr/bin/env python3
"""Compile pinned Ambiq power-control source and inventory its rooted imports."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
UP = G2 / "analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510"
SDK = UP / "ambiqhal"
SOURCE = SDK / "mcu/apollo510/hal/am_hal_pwrctrl.c"
COMPAT = G2 / "components/main/ambiq_pwrctrl_candidate_20261014/mcu/am_hal_sysctrl_clk_mux_reset.h"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-interrupt-mask-current-receipt.json"
OBJECT = OUT / "ambiq-pwrctrl-full-source-candidate.o"
TRIM = OUT / "ambiq-pwrctrl-two-entry-candidate.o"
RECEIPT = OUT / "ambiq-pwrctrl-candidate-receipt.json"
ROOTS = ("am_hal_pwrctrl_periph_enable", "am_hal_pwrctrl_periph_disable")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(args, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *args, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_EXACT_AMBIQ_INTERRUPT_MASK_C"
    current = ROOT / base["linked_object"]
    assert sha(current) == base["linked_sha256"]
    assert set(ROOTS) <= symbols(["-u"], current)
    include = [COMPAT.parent.parent, SDK, SDK / "mcu/apollo510",
               SDK / "CMSIS/AmbiqMicro/Include", UP / "cmsis-5-590/CMSIS/Core/Include"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-ffunction-sections", "-fdata-sections", "-Wno-parentheses-equality",
                    *(f"-I{x}" for x in include), "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections",
                    *(f"--undefined={name}" for name in ROOTS), str(OBJECT), "-o", str(TRIM)], check=True)
    imports = symbols(["-u"], TRIM)
    definitions = symbols(["--defined-only"], TRIM)
    assert set(ROOTS) <= definitions
    new_imports = imports - symbols(["-u"], current)
    receipt = {"status": "PASS_UNSELECTED_AMBIQ_PWRCTRL_C_COMPILES",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "compat_header": str(COMPAT.relative_to(ROOT)), "compat_header_sha256": sha(COMPAT),
               "full_object": str(OBJECT.relative_to(ROOT)), "full_object_sha256": sha(OBJECT),
               "rooted_object": str(TRIM.relative_to(ROOT)), "rooted_object_sha256": sha(TRIM),
               "root_symbols": ROOTS, "rooted_imports": sorted(imports),
               "imports_not_in_current_pool": sorted(new_imports),
               "current_pool_receipt": str(BASE.relative_to(ROOT)), "current_pool_receipt_sha256": sha(BASE),
               "selected_into_main_pool": False, "stock_behavior_equivalence": False,
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["The missing private header supplies only a declaration; the callee body remains unresolved.",
                         "Rooted upstream power-control code introduces additional HAL imports and needs stock behavior and ABI qualification before selection.",
                         "Whole Main root coverage, placement and physical power behavior remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(imports), len(new_imports), sha(RECEIPT))


if __name__ == "__main__":
    main()
