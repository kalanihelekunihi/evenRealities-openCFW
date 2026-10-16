#!/usr/bin/env python3
"""Build the bounded M33 MSPI source overlay and a separate M55 object."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/bootloader/platform_control/power_domains.c"
OUT = ROOT / "g2/build/c-firmware/20261016/boot-mspi-m33-overlay"
OUT.mkdir(parents=True, exist_ok=True)
M33_OBJECT = OUT / "power_domains.o"
M55_OBJECT = OUT / "power_domains_m55.o"
ELF = OUT / "mspi.elf"
BINDINGS = {
    "opencfw_boot_control_query_descriptor_copy": 0x080246a5,
    "opencfw_boot_control_critical_save": 0x0802426d,
    "clock_request": 0x080026ad,
    "clock_release": 0x08002749,
    "opencfw_hal_status_poll": 0x08019df1,
    "opencfw_boot_power_special_mode": 0x0801c8dd,
    "opencfw_bl_clock_release_all": 0x080027e9,
    "opencfw_boot_control_delay_status_change": 0x0801ce25,
    "opencfw_hal_delay_us": 0x0801e901,
}
for cpu, output in (("cortex-m33", M33_OBJECT), ("cortex-m55", M55_OBJECT)):
    subprocess.run(["clang", "--target=arm-none-eabi", f"-mcpu={cpu}", "-mthumb", "-O2",
                    "-ffunction-sections", "-fdata-sections", "-c", str(SOURCE), "-o", str(output)], check=True)
subprocess.run(["arm-none-eabi-ld", "-Ttext=0x437000",
                *(f"--defsym={name}={address:#x}" for name, address in BINDINGS.items()),
                str(M33_OBJECT), "-o", str(ELF)], check=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {"status": "PASS_M33_MSPI_SOURCE_OVERLAY_LINKED", "builder_sha256": sha(Path(__file__)),
          "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
          "m33_object_sha256": sha(M33_OBJECT), "m55_object_sha256": sha(M55_OBJECT),
          "elf": str(ELF.relative_to(ROOT)), "elf_sha256": sha(ELF),
          "bindings": {name: hex(address) for name, address in BINDINGS.items()},
          "limits": ["The M33 overlay runs only in comparison fixtures; M55 compilation is an object check, not a full image link.",
                     "External query, clock, power, delay and poll providers remain selected or controlled by the oracle."]}
(OUT / "build-receipt.json").write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["elf_sha256"])
