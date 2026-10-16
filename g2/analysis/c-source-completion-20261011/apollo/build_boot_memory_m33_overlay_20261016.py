#!/usr/bin/env python3
"""Build the bounded M33 memory-source overlay used by stock/C oracles."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/bootloader/initializer_callbacks/startup_memory_config.c"
ENTRY = ROOT / "g2/components/bootloader/initializer_callbacks/startup_mcu_memory_entry.S"
OUT = ROOT / "g2/build/c-firmware/20261016/boot-memory-m33-overlay"
OUT.mkdir(parents=True, exist_ok=True)
OBJECT = OUT / "startup_memory_config.o"
M55_OBJECT = OUT / "startup_memory_config_m55.o"
ENTRY_OBJECT = OUT / "startup_mcu_memory_entry.o"
ELF = OUT / "memory.elf"
subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m33", "-mthumb", "-O2",
                "-ffunction-sections", "-fdata-sections", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-O2",
                "-ffunction-sections", "-fdata-sections", "-c", str(SOURCE), "-o", str(M55_OBJECT)], check=True)
subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m33", "-mthumb", "-c",
                str(ENTRY), "-o", str(ENTRY_OBJECT)], check=True)
subprocess.run(["arm-none-eabi-ld", "-Ttext=0x436000",
                "--defsym=opencfw_hal_status_poll=0x08019df1",
                "--defsym=opencfw_boot_power_callback=0x0801c349",
                str(OBJECT), str(ENTRY_OBJECT), "-o", str(ELF)], check=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {"status": "PASS_M33_MEMORY_SOURCE_OVERLAY_LINKED", "source": str(SOURCE.relative_to(ROOT)),
          "source_sha256": sha(SOURCE), "builder_sha256": sha(Path(__file__)), "entry": str(ENTRY.relative_to(ROOT)),
          "entry_sha256": sha(ENTRY), "elf": str(ELF.relative_to(ROOT)), "elf_sha256": sha(ELF),
          "m55_object": str(M55_OBJECT.relative_to(ROOT)), "m55_object_sha256": sha(M55_OBJECT),
          "bindings": {"opencfw_hal_status_poll": "0x08019df1",
                       "opencfw_boot_power_callback": "0x0801c349"},
          "limits": ["M33 comparison-only overlay at 0x436000; neither the production M55 link nor a flashable image.",
                     "The two external power/status providers remain controlled by each oracle."]}
(OUT / "build-receipt.json").write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["elf_sha256"])
