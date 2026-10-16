#!/usr/bin/env python3
"""Extend the existing tracepoint ready byte to the stock word extent."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/tracepoint_file_list_ready_extent_20074ae4.c"
BASE = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-check/apollo-main-message-notify-tx-whitelist-check-bound.o"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-tracepoint-ready-word"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in
            subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)],
                                    text=True).splitlines()}


def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    stock = {"request_store_5ee438": "0860", "merge_load_5eed06": "2868",
             "merge_clear_5eee68": "2860"}
    for name, expected in stock.items():
        address = int(name.rsplit("_", 1)[1], 16)
        actual = payload[address-0x438000:address-0x438000+2].hex()
        if actual != expected:
            raise RuntimeError(f"stock word-access instruction changed: {name} {actual}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "tracepoint_ready_word_tail.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-tracepoint-ready-word-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    before, after = imports(BASE), imports(linked)
    if before != after or len(after) != 168:
        raise RuntimeError("tracepoint ready-word frontier changed")
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(linked)], text=True)
    addresses = {}
    for line in nm.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[3] in {
                "audio_tracepoint_local_file_list_ready",
                "audio_tracepoint_file_list_ready_extent_tail_20074ae5"}:
            addresses[parts[3]] = (int(parts[0], 16), int(parts[1], 16))
    if addresses != {"audio_tracepoint_local_file_list_ready": (0, 1),
                      "audio_tracepoint_file_list_ready_extent_tail_20074ae5": (1, 3)}:
        raise RuntimeError(f"tracepoint ready-word symbol extent changed: {addresses}")
    sections = subprocess.check_output(["arm-none-eabi-objdump", "-h", str(linked)], text=True)
    section = re.search(r"\.bss\.opencfw\.tracepoint\.file_list_ready\s+([0-9a-fA-F]+)", sections)
    if not section or int(section.group(1), 16) != 4:
        raise RuntimeError("tracepoint ready-word section is not four bytes")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_READY_WORD_EXTENT_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "stock_word_instructions": stock,
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "section_bytes": 4, "symbols": addresses,
              "unresolved_before": 168, "unresolved_after": 168,
              "imports_resolved": [], "imports_added": [],
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["The original one-byte declaration must be rebuilt as a word from its stage.",
                         "Final RAM placement, startup value and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
