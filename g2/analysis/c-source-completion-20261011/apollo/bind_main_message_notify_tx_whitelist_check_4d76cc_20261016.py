#!/usr/bin/env python3
"""Bind stock-compared MessageNotify whitelist-whitelist-check response encoder."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_tx_whitelist_check_4d76cc.c"
COMMON = G2 / "components/audio/uart_thread_source_candidate/message_notify_tx_common_4d7038.c"
BASE = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-ctrl/apollo-main-message-notify-tx-whitelist-ctrl-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-check"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, flag):
    return {line.split()[-1] for line in
            subprocess.check_output(["arm-none-eabi-nm", "-g", flag, str(path)],
                                    text=True).splitlines()}


def main():
    oracle_path = OUT / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_TX_WHITELIST_CHECK_C_ORACLE"
            or oracle["cases"] != 960 or oracle["source_sha256"] != sha(SOURCE)
            or oracle["shared_source_sha256"] != sha(COMMON)):
        raise RuntimeError("MessageNotify whitelist-check response oracle changed")
    obj = OUT / "message_notify_tx_whitelist_check_4d76cc.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    provider = "audio_message_notify_tx_whitelist_check_4d76cc"
    defined = {provider, "audio_message_notify_cached_crc_get_4d6a20",
               "audio_message_notify_crc_valid_2007501b",
               "audio_message_notify_cached_crc_200749a4"}
    if names(obj, "--defined-only") != defined:
        raise RuntimeError("MessageNotify whitelist-check response providers changed")
    before = names(BASE, "-u")
    if len(before) != 169 or provider not in before:
        raise RuntimeError("MessageNotify whitelist-check response base changed")
    linked = OUT / "apollo-main-message-notify-tx-whitelist-check-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {provider} or after - before or len(after) != 168:
        raise RuntimeError(f"MessageNotify whitelist-check response frontier changed: {before-after}, {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_TX_WHITELIST_CHECK_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(oracle_path.relative_to(ROOT)),
              "oracle_receipt_sha256": sha(oracle_path),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 169, "unresolved_after": 168,
              "imports_resolved": [provider], "imports_added": [],
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["All exposed MessageNotify encoder imports are C-bound.",
                         "Packet/state final RAM placement and BLE side effects remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(before), len(after), sha(receipt))


if __name__ == "__main__":
    main()
