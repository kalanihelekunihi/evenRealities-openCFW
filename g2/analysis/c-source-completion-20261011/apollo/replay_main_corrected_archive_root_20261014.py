#!/usr/bin/env python3
"""Replay remaining source-refresh root links from corrected Apollo C members."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OLD = G2 / "build/c-firmware/20261014/main-root-source-refresh2"
BASE = G2 / "build/c-firmware/20261014/main-corrected-archive-early-replay/apollo-main-corrected-smp_rows.o"
OUT = G2 / "build/c-firmware/20261014/main-corrected-archive-root-replay"
REMOVED = {"audio_uart_input_ring", "audio_uart_display_ring",
           "audio_os_message_queue_put", "audio_os_thread_flags_set",
           "audio_input_error_log"}
ADDED = {"audio_uart_sync_schedule_queue", "audio_ble_dm_stack_rows_200738dc"}
ALIASES = {
    "hciCmdRecvCmpl": "audio_ble_hci_cmd_receive_complete",
    "hciCoreNumCmplPkts": "audio_ble_hci_num_complete_packets",
    "hciCoreCisByHandle": "audio_ble_hci_cis_by_handle",
    "hciCoreCisClose": "audio_ble_hci_cis_close",
    "hciCoreCisOpen": "audio_ble_hci_cis_open",
    "hciCoreConnClose": "audio_ble_hci_conn_close",
    "hciCoreConnOpen": "audio_ble_hci_conn_open",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def checked(name, expected):
    path = ROOT / name
    if sha(path) != expected:
        raise RuntimeError(f"upstream object changed: {name}")
    return path


def link(label, base, objects, *options):
    target = OUT / f"apollo-main-corrected-{label}.o"
    subprocess.run(["arm-none-eabi-ld", "-r", *options, str(base),
                    *(str(p) for p in objects), "-o", str(target)], check=True)
    return target


def checked_stage(label, receipt_name, base, objects, *options):
    receipt_path = OLD / receipt_name
    receipt = json.loads(receipt_path.read_text())
    old = checked(receipt["linked_object"], receipt["linked_object_sha256"])
    new = link(label, base, objects, *options)
    old_u, new_u = names(old, "-u"), names(new, "-u")
    if old_u - new_u != REMOVED or new_u - old_u != ADDED:
        raise RuntimeError(f"unexpected import delta at {label}: {old_u-new_u}, {new_u-old_u}")
    if names(old, "-g", "--defined-only") != names(new, "-g", "--defined-only"):
        raise RuntimeError(f"provider set changed at {label}")
    row = {"stage": label, "upstream_receipt": str(receipt_path.relative_to(ROOT)),
           "upstream_receipt_sha256": sha(receipt_path),
           "old_object": receipt["linked_object"], "old_sha256": sha(old),
           "new_object": str(new.relative_to(ROOT)), "new_sha256": sha(new),
           "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
           "link_options": list(options), "old_unresolved": len(old_u),
           "new_unresolved": len(new_u)}
    return new, row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    smp = json.loads((OLD / "main-smp-closure-receipt.json").read_text())
    smp_objects = [checked(p, h) for p, h in smp["table_action_objects"].items()]
    smp_objects += [checked(p, h) for p, h in smp["ecc_objects"].items()]
    smp_objects.append(checked(smp["bda_copy_object"], smp["bda_copy_object_sha256"]))
    smp_objects.append(checked("g2/build/c-firmware/20261014/main-root-source-refresh2/apollo_main/refresh-memcmp.o",
                               "cd6a36378a67d2dd895bbda6dd2d525fe71f7680fff36156bd3af623de4af29e"))
    current, row = checked_stage("smp_closure", "main-smp-closure-receipt.json", BASE, smp_objects)
    records.append(row)
    for label, receipt_name in (
        ("rom_runtime", "main-rom-runtime-receipt.json"),
        ("file_runtime", "main-file-runtime-receipt.json"),
        ("tlsf_runtime", "main-tlsf-runtime-receipt.json"),
    ):
        receipt = json.loads((OLD / receipt_name).read_text())
        objects = [checked(p, h) for p, h in receipt["objects"].items()]
        current, row = checked_stage(label, receipt_name, current, objects)
        records.append(row)
    hci = json.loads((OLD / "main-hci-decoder-composition-receipt.json").read_text())
    hci_objects = {Path(p).name: checked(p, h) for p, h in hci["objects"].items()}
    decoder = link("hci_decoder", current, [hci_objects["refresh-hci-decoders.o"]])
    joins = link("hci_joins", decoder, [],
                 *(f"--defsym={alias}={provider}" for alias, provider in ALIASES.items()))
    vendor = link("hci_vendor", joins, [hci_objects["refresh-hci-vendor-complete.o"]])
    current, row = checked_stage("hci_composed", "main-hci-decoder-composition-receipt.json",
                                 vendor, [hci_objects["refresh-hci-cb.o"]])
    row["intermediate_objects"] = {str(p.relative_to(ROOT)): sha(p) for p in (decoder, joins, vendor)}
    row["hci_aliases"] = ALIASES
    records.append(row)
    scheduler = json.loads((OLD / "main-scheduler-event-group-receipt.json").read_text())
    objects = [checked(p, h) for p, h in scheduler["objects"].items()]
    current, row = checked_stage("scheduler", "main-scheduler-event-group-receipt.json",
                                 current, objects)
    records.append(row)
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_ROOT_REPLAY_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "stages": records,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": records[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Source-refresh root replay only; later Apollo link waves remain to replay.",
                   "Provider parity and import delta do not prove final placement or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], records[-1]["old_unresolved"], records[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
