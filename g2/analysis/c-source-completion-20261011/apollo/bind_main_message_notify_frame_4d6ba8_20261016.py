#!/usr/bin/env python3
"""Bind stock-compared MessageNotify frame decoder to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_frame_4d6ba8.c"
BASE = G2 / "build/c-firmware/20261016/main-message-notify-common/apollo-main-message-notify-common-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-frame"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, flag):
    return {line.split()[-1] for line in
            subprocess.check_output(["arm-none-eabi-nm", "-g", flag, str(path)],
                                    text=True).splitlines()}


def main():
    oracle_path = OUT / "oracle-receipt.json"
    oracle = json.loads(oracle_path.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_FRAME_C_ORACLE"
            or oracle["cases"] != 432 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("MessageNotify frame oracle changed")
    obj = OUT / "message_notify_frame_4d6ba8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {"audio_message_notify_frame_process_4d6ba8"}:
        raise RuntimeError("MessageNotify frame provider changed")
    before = names(BASE, "-u")
    if len(before) != 169 or "audio_message_notify_frame_process_4d6ba8" not in before:
        raise RuntimeError("MessageNotify frame base changed")
    linked = OUT / "apollo-main-message-notify-frame-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = names(linked, "-u")
    resolved = {"audio_message_notify_frame_process_4d6ba8"}
    added = {"audio_message_notify_rx_ctrl_4d6db0",
             "audio_message_notify_tx_ctrl_4d6ea2",
             "audio_message_notify_rx_whitelist_ctrl_4d73d6",
             "audio_message_notify_tx_whitelist_ctrl_4d749a",
             "audio_message_notify_rx_whitelist_check_4d7624",
             "audio_message_notify_tx_whitelist_check_4d76cc",
             "audio_message_notify_tx_common_response_4d7038"}
    if before - after != resolved or after - before != added or len(after) != 175:
        raise RuntimeError(f"MessageNotify frame frontier changed: {before-after}, {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_FRAME_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(oracle_path.relative_to(ROOT)),
              "oracle_receipt_sha256": sha(oracle_path),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 169, "unresolved_after": 175,
              "imports_resolved": sorted(resolved), "imports_added": sorted(added),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Seven MessageNotify validators/encoders remain imports.",
                         "Enabled logging, real nanopb effects, final layout and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(before), len(after), sha(receipt))


if __name__ == "__main__":
    main()
