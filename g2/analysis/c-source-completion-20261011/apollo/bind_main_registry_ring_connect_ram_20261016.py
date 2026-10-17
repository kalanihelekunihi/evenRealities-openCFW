#!/usr/bin/env python3
"""Bind the stock-literal ring-connect RAM interval to C-owned storage."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/registry_ring_connect_ram_2010f4cc.c"
STATE_SOURCE = G2 / "components/audio/uart_thread_source_candidate/registry_ring_connect_state.c"
LINKER = SOURCE.with_suffix(".ld")
BASE = G2 / "build/c-firmware/20261016/main-terminal-rx-frame-5ce990/apollo-main-rx-frame-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-registry-ring-connect-ram"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ADDRESSES = {"audio_registry_ring_connect_buffer": (0x2010F4CC, 0x850),
             "audio_registry_ring_connect_state": (0x2010FD1C, 1)}
PRIOR_ARCHIVE = G2 / "build/c-firmware/20261016/main-terminal-state-cluster/libaudio-terminal-state-cluster.a"
MAIN_ARCHIVE = G2 / "build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
INPUT_BASE = G2 / "build/c-firmware/20261014/main-input-archive-member-refresh/candidate-input-corrected.o"
MANIFEST = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main/audio/compile-results.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def providers(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(path)],
        text=True).splitlines() if line.strip()}


def symbols(path):
    result = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-S", str(path)],
                                        text=True).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[3] in ADDRESSES:
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    return result


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Apollo payload changed")
    literals = [int.from_bytes(payload[address - 0x438000:address - 0x438000 + 4],
                               "little") for address in (0x5e4794, 0x5e4798)]
    if literals != [0x2010F4CC, 0x2010FD1C]:
        raise RuntimeError("stock ring-connect RAM literals changed")
    if imports(BASE) & set(ADDRESSES) != {"audio_registry_ring_connect_buffer"}:
        raise RuntimeError("Main ring-connect import frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "registry-ring-connect-ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    state_obj = OUT / "registry-ring-connect-state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(STATE_SOURCE),
                    "-o", str(state_obj)], check=True)
    if symbols(obj) != {"audio_registry_ring_connect_buffer": (0, 0x850)} or \
            symbols(state_obj) != {"audio_registry_ring_connect_state": (0, 1)}:
        raise RuntimeError("C storage extents changed")
    placed = OUT / "registry-ring-connect-ram-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER), str(obj), str(state_obj),
                    "-o", str(placed)], check=True)
    if symbols(placed) != ADDRESSES:
        raise RuntimeError("isolated stock placement changed")
    before = imports(BASE)
    linked = OUT / "apollo-main-ring-connect-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != {"audio_registry_ring_connect_buffer"} or after - before or len(after) != 165:
        raise RuntimeError("unexpected Main import delta")
    rows = [row for row in json.loads(MANIFEST.read_text())["rows"]
            if Path(row["source"]).name == STATE_SOURCE.name]
    if len(rows) != 1:
        raise RuntimeError("state archive member missing or duplicated")
    member = Path(rows[0]["object_path"]).name
    replacement = OUT / member
    command = list(rows[0]["command"])
    command[command.index("-MF") + 1] = str(OUT / (member + ".d"))
    command[command.index("-o") + 1] = str(replacement)
    subprocess.run(command, check=True)
    if symbols(replacement) != {"audio_registry_ring_connect_state": (0, 1)}:
        raise RuntimeError("rebuilt state member changed")
    archive = OUT / "libaudio-terminal-and-ring-ram.a"
    shutil.copyfile(PRIOR_ARCHIVE, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive), str(replacement),
                    str(obj)], check=True)
    combined = OUT / "candidate-input-terminal-and-ring-ram.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(MAIN_ARCHIVE), "--no-whole-archive", "-o", str(combined)],
                   check=True)
    if imports(INPUT_BASE) - imports(combined) != {"audio_registry_ring_connect_buffer"} or \
            imports(combined) - imports(INPUT_BASE) or \
            providers(combined) - providers(INPUT_BASE) != {
                "audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"} or \
            providers(INPUT_BASE) - providers(combined):
        raise RuntimeError("combined from-stage provider/import delta changed")
    combined_symbols = symbols(combined)
    if len(combined_symbols) != 2 or \
            combined_symbols["audio_registry_ring_connect_buffer"][1] != 0x850 or \
            combined_symbols["audio_registry_ring_connect_state"][1] != 1:
        raise RuntimeError("combined from-stage RAM extent changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_AND_RING_RAM_C_ARCHIVE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "state_source": str(STATE_SOURCE.relative_to(ROOT)),
        "state_source_sha256": sha(STATE_SOURCE),
        "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PAYLOAD_SHA, "stock_literal_addresses": ["0x5e4794", "0x5e4798"],
        "stock_ram_addresses": [hex(value) for value in literals],
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "state_object": str(state_obj.relative_to(ROOT)), "state_object_sha256": sha(state_obj),
        "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "combined_prior_archive": str(PRIOR_ARCHIVE.relative_to(ROOT)),
        "combined_prior_archive_sha256": sha(PRIOR_ARCHIVE),
        "combined_archive": str(archive.relative_to(ROOT)),
        "combined_archive_sha256": sha(archive),
        "combined_linked_object": str(combined.relative_to(ROOT)),
        "combined_linked_sha256": sha(combined),
        "combined_rebuilt_state_member": member,
        "combined_rebuilt_state_member_sha256": sha(replacement),
        "combined_input_imports_removed": ["audio_registry_ring_connect_buffer"],
        "combined_input_providers_added": ["audio_registry_ring_connect_buffer",
                                           "audio_terminal_ui_state_base"],
        "combined_input_provider_removals": [],
        "combined_archive_duplicate_field_definitions": False,
        "imports_resolved": ["audio_registry_ring_connect_buffer"], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": [
            "The 0x850-byte buffer reservation is the observed buffer-to-state interval; actual decoded-message extent is not independently established.",
            "The current Main candidate still contains the prior state-byte archive member; final state placement needs an archive rebuild.",
            "Final full RAM-map placement, initialization, whole-image linkage and G2 behavior remain open.",
            "The combined from-stage archive is experimental; downstream Main replay and final RAM-map proof remain open.",
        ],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
