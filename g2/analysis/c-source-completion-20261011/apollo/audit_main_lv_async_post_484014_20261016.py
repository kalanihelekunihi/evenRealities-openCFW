#!/usr/bin/env python3
"""Pin source-linked LVGL async queue and repeat setter."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-lv-async-post-484014"
PRIOR = BASE / "main-lv-object-delete-async-44d90e/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_async_post_484014.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_lv_async_post_484014_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_uart_lv_async_post_484014"}
    if (len(before), len(after)) != (139, 138) or before-after != removed or after-before:
        raise RuntimeError("LVGL async queue frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_LV_ASYNC_POST_484014_C" or
            oracle["cases"] != 19 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("LVGL async queue oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_uart_lv_async_post_484014", "audio_uart_lv_timer_repeat_count_4645ac"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError("LVGL async queue body missing: " + symbol)
    record = {"status": "PASS_DIRECT_MAIN_LV_ASYNC_POST_484014_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": oracle["native_bodies"], "oracle_cases": 19,
              "unresolved_before": 139, "unresolved_after": 138,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Conversate expand scheduler 0x5b7704 and remaining Main imports remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
