#!/usr/bin/env python3
"""Bind two source names for the single native AppDb table at 0x20067a30."""
import json
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261014/main-pair-record-flags/apollo-main-pair-record-flags.o"
OUT = G2 / "build/c-firmware/20261014/main-privacy-rows-alias"
TABLE_SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_runtime_bindings.c"
ALIAS_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_app_db_bonded.c"
TABLE = "audio_ble_dm_conn_state_table_20067a30"
ALIAS = "audio_ble_privacy_rows"


def main():
    if f"uint8_t {TABLE}[10u * 200u]" not in TABLE_SOURCE.read_text() or \
       f"extern uint8_t {ALIAS}[10u*200u]; /* native RAM 0x20067a30 */" not in ALIAS_USER.read_text():
        raise RuntimeError("source table geometry or native RAM annotation changed")
    before = names(BASE, "-u")
    defined = names(BASE, "-g", "--defined-only")
    if ALIAS not in before or TABLE not in defined or ALIAS in defined:
        raise RuntimeError("Apollo Main privacy table source contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "apollo-main-privacy-rows-alias.o"
    subprocess.run(["arm-none-eabi-ld", "-r", f"--defsym={ALIAS}={TABLE}",
                    str(BASE), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    symbol_lines = subprocess.check_output(["arm-none-eabi-nm", "-g", str(linked)], text=True)
    addresses = {parts[-1]: (parts[0], parts[1])
                 for line in symbol_lines.splitlines()
                 if len(parts := line.split()) == 3 and parts[-1] in {TABLE, ALIAS}}
    if before - after != {ALIAS} or after - before or \
       addresses.get(TABLE) != addresses.get(ALIAS):
        raise RuntimeError("privacy alias did not share the C table storage")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PRIVACY_ROWS_ALIAS",
               "table_source": str(TABLE_SOURCE.relative_to(ROOT)),
               "table_source_sha256": sha(TABLE_SOURCE),
               "alias_user_source": str(ALIAS_USER.relative_to(ROOT)),
               "alias_user_source_sha256": sha(ALIAS_USER),
               "native_table_origin": "0x20067a30", "table_rows": 10,
               "table_stride_bytes": 200, "table_bytes": 2000,
               "linker_alias": f"{ALIAS}={TABLE}",
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The two C names share storage in the relocatable object.",
                          "Absolute RAM placement at 0x20067a30 remains a final linker gate.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
