#!/usr/bin/env python3
"""Bind stock-addressed Apollo LittleFS context using pinned lfs_t size."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/file_lfs_context_20071ac8.c"
LINKER = SOURCE.with_suffix(".ld")
UPSTREAM = ROOT / "third-party/upstream/littlefs"
FREESTANDING = G2 / "components/bootloader/filesystem/freestanding_include"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_RECEIPT = G2 / "build/c-firmware/20261014/main-littlefs-provider-closure/receipt.json"
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-combined-ram-current-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-file-lfs-context-20071ac8"
NAME = "audio_file_lfs_context"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def cell(path):
    rows = [line.split() for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
        if line.endswith(" " + NAME)]
    if len(rows) != 1:
        raise RuntimeError("LittleFS context missing or duplicated")
    return int(rows[0][0], 16), int(rows[0][1], 16), rows[0][2]


def main():
    commit = subprocess.check_output(["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"],
                                     text=True).strip()
    if commit != UPSTREAM_COMMIT:
        raise RuntimeError("pinned LittleFS submodule changed")
    upstream = json.loads(UPSTREAM_RECEIPT.read_text())
    if upstream["upstream_littlefs_sha256"] != sha(UPSTREAM / "lfs.c"):
        raise RuntimeError("Main LittleFS provider source changed")
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Apollo payload changed")
    literals = (0x473668, 0x474e44, 0x476474, 0x57b41c,
                0x57f3c0, 0x57fc94, 0x5800a4, 0x5a5714)
    if any(int.from_bytes(payload[addr - 0x438000:addr - 0x438000 + 4],
                          "little") != 0x20071ac8 for addr in literals):
        raise RuntimeError("stock LittleFS context literals changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_CURRENT_REPLAY_C" or \
            base["unresolved_after"] != 164:
        raise RuntimeError("combined Main frontier changed")
    original = ROOT / base["linked_object"]
    if sha(original) != base["linked_sha256"] or NAME not in imports(original):
        raise RuntimeError("Main LittleFS context import changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "file-lfs-context.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-DLFS_NO_MALLOC", "-DLFS_NO_ASSERT",
                    "-DLFS_NO_DEBUG", "-DLFS_NO_WARN", "-DLFS_NO_ERROR",
                    "-I" + str(UPSTREAM), "-I" + str(FREESTANDING),
                    "-c", str(SOURCE), "-o", str(obj)], check=True)
    if cell(obj) != (0, 0x80, "B"):
        raise RuntimeError("ARM LittleFS context size changed")
    placed = OUT / "file-lfs-context-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if cell(placed) != (0x20071ac8, 0x80, "B"):
        raise RuntimeError("isolated LittleFS RAM placement changed")
    linked = OUT / "apollo-main-file-lfs-context-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    before, after = imports(original), imports(linked)
    if before - after != {NAME} or after - before or len(after) != 163:
        raise RuntimeError("unexpected Main LittleFS import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_LFS_CONTEXT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "upstream_commit": commit,
               "upstream_header": str((UPSTREAM / "lfs.h").relative_to(ROOT)),
               "upstream_header_sha256": sha(UPSTREAM / "lfs.h"),
               "upstream_provider_receipt": str(UPSTREAM_RECEIPT.relative_to(ROOT)),
               "upstream_provider_receipt_sha256": sha(UPSTREAM_RECEIPT),
               "payload_sha256": PAYLOAD_SHA,
               "stock_literal_addresses": [hex(addr) for addr in literals],
               "stock_ram_address": "0x20071ac8", "context_bytes": 128,
               "next_source_owned_ram_address": "0x20071cc8",
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [NAME], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The pinned LittleFS lfs_t establishes a 128-byte C reservation; exact firmware configuration and startup contents remain open.",
                          "The isolated stock placement does not prove the complete Apollo RAM map or whole-image behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
