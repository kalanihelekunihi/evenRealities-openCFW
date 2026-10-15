#!/usr/bin/env python3
"""Bind native-matched radio GPIO callback to the Apollo Main WSF provider."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/radio_gpio_callback_bridge.c"
FOUNDATION = G2 / "components/foundation/radio_gpio/radio_gpio.c"
WSF = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_driver_children.c"
BASE = G2 / "build/c-firmware/20261014/main-ring-status-pointer/apollo-main-ring-status-pointer.o"
OUT = G2 / "build/c-firmware/20261014/main-radio-gpio-callback"
ORACLE = Path(__file__).with_name("verify_main_radio_gpio_callback_oracle_20261014.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        elf = ELFFile(stream)
        segment = next(item for item in elf.iter_segments() if item["p_type"] == "PT_LOAD")
        image = segment.data()
        base = segment["p_vaddr"]
        expected = {0x4b4d94: 0x20074640, 0x4b4da4: 0x20074fcb}
        for literal, address in expected.items():
            if struct.unpack_from("<I", image, literal-base)[0] != address:
                raise RuntimeError(f"radio callback RAM pointer changed: {literal:#x}")
        native_body = image[0x4b4a98-base:0x4b4ab2-base]
        if len(native_body) != 26 or native_body[:2] != bytes.fromhex("80b5"):
            raise RuntimeError("native radio callback body changed")
    if "opencfw_radio_gpio_callback" not in FOUNDATION.read_text() or "audio_ble_wsf_set_event" not in WSF.read_text():
        raise RuntimeError("radio GPIO or WSF source provenance changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "radio_gpio_callback_bridge.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"opencfw_radio_gpio_callback"} or names(obj, "-u") != {"audio_ble_wsf_set_event"}:
        raise RuntimeError("compiled radio callback provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if "opencfw_radio_gpio_callback" not in before or "audio_ble_wsf_set_event" not in providers:
        raise RuntimeError("Main radio GPIO consumer or scheduler provider changed")
    linked = OUT / "apollo-main-radio-gpio-callback.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"opencfw_radio_gpio_callback"} or after-before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_RADIO_GPIO_CALLBACK_ORACLE" or oracle["cases"] != 32:
        raise RuntimeError("native radio callback oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_RADIO_GPIO_CALLBACK_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": "0x4b4a98", "native_body_sha256": hashlib.sha256(native_body).hexdigest(),
        "native_ram_literals": {hex(literal): hex(address) for literal, address in expected.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "foundation_source": str(FOUNDATION.relative_to(ROOT)), "foundation_source_sha256": sha(FOUNDATION),
        "wsf_source": str(WSF.relative_to(ROOT)), "wsf_source_sha256": sha(WSF),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["The oracle intercepts scheduler submission; async GPIO/NVIC, full image and hardware remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
