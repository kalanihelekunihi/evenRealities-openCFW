#!/usr/bin/env python3
"""Bind two native-backed Apollo Main byte cells into the C replay."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/onboarding_imu_cells.c"
USERS = [G2 / "components/audio/uart_thread_source_candidate/service_prepare5.c",
         G2 / "components/audio/uart_thread_source_candidate/imu_aid_status.c"]
BASE = G2 / "build/c-firmware/20261014/main-case-status/apollo-main-case-status.o"
OUT = G2 / "build/c-firmware/20261014/main-onboarding-imu-cells"
CELLS = {
    "g2_onboarding_flag": (0x20000040, 0x4a789c),
    "g2_imu_aid_enabled_cell": (0x20074fd8, 0x4a537c),
}
ORACLES = (
    G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_uart_service_prepare5.py",
    G2 / "analysis/c-source-completion-20261011/peripherals/verify_imu_aid_status.py",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        native = ELFFile(stream)
        segment = next(item for item in native.iter_segments() if item["p_type"] == "PT_LOAD")
        for name, (address, literal) in CELLS.items():
            offset = literal - segment["p_vaddr"]
            found = struct.unpack_from("<I", segment.data(), offset)[0]
            if found != address:
                raise RuntimeError(f"native RAM pointer changed: {name} {found:#x}")
    text = SOURCE.read_text()
    for name, (address, _) in CELLS.items():
        if name not in text or f".g2_ram_{address:08x}" not in text:
            raise RuntimeError(f"C cell contract changed: {name}")
        if not any(name in user.read_text() for user in USERS):
            raise RuntimeError(f"C consumer changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "onboarding_imu_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        actual = {section.name: section["sh_size"] for section in elf.iter_sections()
                  if section.name.startswith(".g2_ram_")}
    expected = {f".g2_ram_{address:08x}": 1 for address, _ in CELLS.values()}
    if actual != expected or names(obj, "-g", "--defined-only") != set(CELLS) or names(obj, "-u"):
        raise RuntimeError("compiled one-byte C cell set changed")
    before = names(BASE, "-u")
    if not set(CELLS) <= before:
        raise RuntimeError("Main cell imports changed")
    linked = OUT / "apollo-main-onboarding-imu-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CELLS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    oracle_output = {}
    for script in ORACLES:
        result = subprocess.run([sys.executable, str(script)], check=True,
                                capture_output=True, text=True)
        oracle_output[str(script.relative_to(ROOT))] = {
            "sha256": sha(script), "output": result.stdout.strip()}
    if "PASS_AUDIO_UART_SERVICE_PREPARE5 15" not in oracle_output[str(ORACLES[0].relative_to(ROOT))]["output"]:
        raise RuntimeError("onboarding consumer oracle changed")
    if oracle_output[str(ORACLES[1].relative_to(ROOT))]["output"].count("PASS IMU AID byte") != 5:
        raise RuntimeError("IMU AID consumer oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_ONBOARDING_IMU_CELLS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literal": hex(literal), "bytes": 1}
                       for name, (address, literal) in CELLS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(user.relative_to(ROOT)): sha(user) for user in USERS},
        "consumer_oracles": oracle_output,
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Startup values and final RAM placement for both cells remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
