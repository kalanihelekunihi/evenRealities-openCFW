#!/usr/bin/env python3
"""Bind synthetic legacy advertising connection completion to C."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_adv_gen_conn_4b310a.c"
BASE = G2 / "build/c-firmware/20261015/main-dm-adv-hci-4ba4b0/apollo-main-dm-adv-hci-4ba4b0.o"
OUT = G2 / "build/c-firmware/20261015/main-dm-adv-gen-conn-4b310a"
OWNED = {"audio_ble_dm_adv_gen_conn_complete_4b310a"}
ADDED = {"audio_ble_dm_dev_pass_hci_conn_4d29c2"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def oracle(script, status):
    receipt = json.loads(subprocess.check_output([sys.executable, str(HERE / script)], text=True))
    if receipt["status"] != status or receipt["cases"] != 8:
        raise RuntimeError(f"{script} changed")
    return receipt


def main():
    native = oracle("verify_main_dm_adv_gen_conn_native_20261015.py", "PASS_NATIVE_DM_ADV_GEN_CONN")
    bounded = oracle("verify_main_dm_adv_gen_conn_c_20261015.py", "PASS_BOUNDED_DM_ADV_GEN_CONN_C")
    if bounded["source_sha256"] != sha(SOURCE):
        raise RuntimeError("advertising completion source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_dm_adv_gen_conn_4b310a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    size_lines = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(BASE)], text=True)
    if not any((parts := line.split())[-1:] == ["audio_ble_dm_adv_control"] and
               len(parts) == 4 and int(parts[1], 16) >= 0x34 for line in size_lines.splitlines()):
        raise RuntimeError("advertising control C span is too small for peer completion")
    if OWNED != before & OWNED or OWNED & defined or \
            "audio_ble_dm_adv_control" not in defined or \
            symbols(obj, "--defined-only") != OWNED or \
            symbols(obj, "-u") != {"audio_ble_dm_adv_control", "__aeabi_memclr4"} | ADDED or \
            "__aeabi_memclr4" not in defined:
        raise RuntimeError("advertising completion symbol frontier changed")
    linked = OUT / "apollo-main-dm-adv-gen-conn-4b310a.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 192 or len(after) != 192 or before - after != OWNED or after - before != ADDED:
        raise RuntimeError("advertising completion import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_ADV_GEN_CONN_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "native_oracle": native, "c_oracle": bounded,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(OWNED), "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Compared default and second advertising handle records; arbitrary handle bounds remain open.",
                          "Connection callback dispatch, final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
