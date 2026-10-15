#!/usr/bin/env python3
"""Refresh corrected input members in a copy of the Apollo audio archive."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OLD = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main"
AUDIO = OLD / "audio/libaudio-source-candidates.a"
MAIN = G2 / "build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
COMBINED = OLD / "candidate.o"
MANIFEST = OLD / "audio/compile-results.json"
CORRECTION = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_input_cell_identity_correction_20261014.py"
MSG_ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_input_msg_record_corrected_20261014.py"
RING_ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ring_sync_native_20261014.py"
DM_ROW_RECEIPT = G2 / "build/c-firmware/20261014/main-dm-row-relink/receipt.json"
OUT = G2 / "build/c-firmware/20261014/main-input-archive-member-refresh"
SOURCES = (
    G2 / "components/audio/uart_thread_source_candidate/display_input_event_send.c",
    G2 / "components/audio/uart_thread_source_candidate/display_thread.c",
    G2 / "components/audio/uart_thread_source_candidate/input_event.c",
    G2 / "components/audio/uart_thread_source_candidate/input_msg_send_record.c",
    G2 / "components/audio/uart_thread_source_candidate/display_ble_stack_lowers.c",
    G2 / "components/audio/uart_thread_source_candidate/ring_sync.c",
)
OWNERS = ("audio_uart_input_event_send_464d1c", "audio_uart_display_thread",
          "audio_uart_input_event", "audio_input_message_send_record",
          "audio_ble_dm_stack_state_init", "audio_ble_stack_lower_5369ea",
          "audio_uart_ring_sync_active", "audio_uart_ring_sync_idle")


def output(*args):
    return subprocess.check_output(args, text=True)


def main():
    subprocess.run([sys.executable, str(CORRECTION)], check=True)
    subprocess.run([sys.executable, str(MSG_ORACLE)], check=True)
    subprocess.run([sys.executable, str(RING_ORACLE)], check=True)
    dm_evidence = json.loads(DM_ROW_RECEIPT.read_text())
    if dm_evidence["source_sha256"] != sha(SOURCES[-2]):
        raise RuntimeError("corrected DM row source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    rows = {str((ROOT / r["source"]).resolve()): r for r in manifest["rows"]}
    old_members = output("arm-none-eabi-ar", "t", str(AUDIO)).splitlines()
    if len(old_members) != len(set(old_members)):
        raise RuntimeError("original audio archive has duplicate member names")
    archive = OUT / "libaudio-input-corrected.a"
    shutil.copyfile(AUDIO, archive)
    refreshed = []
    for source in SOURCES:
        row = rows[str(source.resolve())]
        member = Path(row["object_path"]).name
        if old_members.count(member) != 1:
            raise RuntimeError(f"archive member missing/duplicated: {member}")
        obj = OUT / member
        command = list(row["command"])
        command[command.index("-MF") + 1] = str(OUT / (member + ".d"))
        command[command.index("-o") + 1] = str(obj)
        subprocess.run(command, check=True)
        refreshed.append((source, obj, member, command))
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive),
                    *(str(row[1]) for row in refreshed)], check=True)
    new_members = output("arm-none-eabi-ar", "t", str(archive)).splitlines()
    if new_members != old_members:
        raise RuntimeError("archive member order/count changed after targeted replacement")
    linked = OUT / "candidate-input-corrected.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive), str(MAIN),
                    "--no-whole-archive", "-o", str(linked)], check=True)
    old_u, new_u = names(COMBINED, "-u"), names(linked, "-u")
    removed = {"audio_uart_input_ring", "audio_uart_display_ring",
               "audio_os_message_queue_put", "audio_os_thread_flags_set",
               "audio_input_error_log"}
    added = {"audio_uart_sync_schedule_queue", "audio_ble_dm_stack_rows_200738dc"}
    if old_u - new_u != removed or new_u - old_u != added:
        raise RuntimeError(f"unexpected archive import delta: removed={old_u-new_u}, added={new_u-old_u}")
    old_defined, new_defined = names(COMBINED, "-g", "--defined-only"), names(linked, "-g", "--defined-only")
    if old_defined != new_defined or not set(OWNERS) <= new_defined:
        raise RuntimeError("targeted archive refresh changed provider set")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_INPUT_ARCHIVE_MEMBER_REFRESH_C",
               "original_audio_archive": str(AUDIO.relative_to(ROOT)), "original_audio_sha256": sha(AUDIO),
               "main_archive": str(MAIN.relative_to(ROOT)), "main_archive_sha256": sha(MAIN),
               "compile_manifest": str(MANIFEST.relative_to(ROOT)), "compile_manifest_sha256": sha(MANIFEST),
               "refreshed_members": [{"source": str(source.relative_to(ROOT)),
                                      "source_sha256": sha(source), "member": member,
                                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                                      "command": command}
                                     for source, obj, member, command in refreshed],
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "original_combined": str(COMBINED.relative_to(ROOT)), "original_combined_sha256": sha(COMBINED),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "archive_members": len(new_members),
               "unresolved_before": len(old_u), "unresolved_after": len(new_u),
               "imports_resolved": sorted(removed), "imports_added": sorted(added),
               "provider_set_preserved": True,
               "input_message_oracle": str((G2 / "build/c-firmware/20261014/main-input-msg-record-corrected/receipt.json").relative_to(ROOT)),
               "input_message_oracle_sha256": sha(G2 / "build/c-firmware/20261014/main-input-msg-record-corrected/receipt.json"),
               "dm_row_source_receipt": str(DM_ROW_RECEIPT.relative_to(ROOT)),
               "dm_row_source_receipt_sha256": sha(DM_ROW_RECEIPT),
               "ring_sync_oracle": str((G2 / "build/c-firmware/20261014/ring-sync-correction/receipt.json").relative_to(ROOT)),
               "ring_sync_oracle_sha256": sha(G2 / "build/c-firmware/20261014/ring-sync-correction/receipt.json"),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["This refresh covers six corrected members of the earlier audio archive; subsequent Apollo link waves must be replayed from it.",
                          "DM row source is compiled directly; its native runtime coverage, final placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(old_u), len(new_u), sha(path))


if __name__ == "__main__":
    main()
