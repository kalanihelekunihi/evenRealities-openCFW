#!/usr/bin/env python3
"""Bind the eight legacy advertising message actions and dispatcher to C."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_adv_msg_4ba6ac.c"
BASE = G2 / "build/c-firmware/20261015/main-dm-adv-reset-4ba45c/apollo-main-dm-adv-reset-4ba45c.o"
OUT = G2 / "build/c-firmware/20261015/main-dm-adv-msg-4ba6ac"
OWNED = {
    "audio_ble_dm_adv_config_4b9ac0", "audio_ble_dm_adv_set_data_4b9d24",
    "audio_ble_dm_adv_start_4b9e88", "audio_ble_dm_adv_stop_4ba0f4",
    "audio_ble_dm_adv_remove_set_4ba33c", "audio_ble_dm_adv_clear_sets_4ba33e",
    "audio_ble_dm_adv_set_rand_addr_4ba340", "audio_ble_dm_adv_timeout_4ba342",
    "audio_ble_dm_adv_actions_75f550", "audio_ble_dm_adv_msg_handler_4ba6ac",
}
CHILDREN = {"audio_ble_dm_adv_config_lower_4b9a80", "HciLeSetAdvDataCmd",
            "HciLeSetScanRespDataCmd", "HciLeSetAdvEnableCmd"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def verify(script, status):
    output = subprocess.check_output([sys.executable, str(HERE / script)], text=True)
    receipt = json.loads(output)
    if receipt["status"] != status:
        raise RuntimeError(f"{script} changed")
    return receipt


def main():
    bounded = verify("verify_main_dm_adv_msg_4ba6ac_20261015.py", "PASS_BOUNDED_ADV_MSG_C")
    native = verify("verify_main_dm_adv_stop_timeout_native_20261015.py", "PASS_NATIVE_DM_ADV_ACTIONS")
    if bounded["source_sha256"] != sha(SOURCE) or bounded["event_byte_cases"] != 256 or \
            bounded["action_state_cases"] != 280 or native["cases"] != 280:
        raise RuntimeError("advertising action oracle scope changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_dm_adv_msg_4ba6ac.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if OWNED & (before | defined) or CHILDREN & defined or \
            "audio_ble_dm_adv_control" not in defined or \
            symbols(obj, "--defined-only") != OWNED or \
            symbols(obj, "-u") != CHILDREN | {"audio_ble_dm_adv_control"}:
        raise RuntimeError("advertising message C symbol frontier changed")
    linked = OUT / "apollo-main-dm-adv-msg-4ba6ac.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 192 or len(after) != 196 or after - before != CHILDREN or before - after:
        raise RuntimeError("advertising message import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_ADV_MSG_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "bounded_oracle": bounded, "native_oracle": native,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [], "imports_added": sorted(CHILDREN),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Five nonempty action bodies are checked with logging disabled; native diagnostic branches remain open.",
                          "The advertising HCI interface, four exposed child calls, final image placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
