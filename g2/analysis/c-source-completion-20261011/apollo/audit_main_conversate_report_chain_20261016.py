#!/usr/bin/env python3
"""Pin report and UI event-name C bodies with their exact remaining table gate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-event-name-5b16fc"
PRIOR = BASE / "main-conversate-ui-cleanup-commit-5b3a88/candidate.o"
REPORT = BASE / "main-conversate-report-5b02e4/candidate.o"
CANDIDATE = HERE / "candidate.o"
REPORT_SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_report_5b02e4.c"
NAME_SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_event_name_5b16fc.c"
REPORT_VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_report_5b02e4_20261016.py"
NAME_VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_event_name_5b16fc_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, middle, after = imports(PRIOR), imports(REPORT), imports(CANDIDATE)
    if (len(before), len(middle), len(after)) != (120, 120, 120):
        raise RuntimeError("Conversate report frontier count changed")
    if (before-middle != {"audio_conversate_report_5b02e4"} or
            middle-before != {"audio_conversate_ui_event_name_5b16fc"} or
            middle-after != {"audio_conversate_ui_event_name_5b16fc"} or
            after-middle != {"audio_conversate_ui_event_names_20000560"}):
        raise RuntimeError("Conversate report frontier names changed")
    report_oracle_path = BASE / "main-conversate-report-5b02e4/oracle-receipt.json"
    name_oracle_path = HERE / "oracle-receipt.json"
    report_oracle = json.loads(report_oracle_path.read_text())
    name_oracle = json.loads(name_oracle_path.read_text())
    for oracle, status, cases, source in (
        (report_oracle, "PASS_DIRECT_MAIN_CONVERSATE_REPORT_C", 900, REPORT_SOURCE),
        (name_oracle, "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_NAME_C", 261, NAME_SOURCE),
    ):
        if (oracle["status"] != status or oracle["cases"] != cases or
                oracle["source_sha256"] != sha(source) or
                oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
            raise RuntimeError(f"Conversate oracle changed: {status}")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in ("audio_conversate_report_5b02e4", "audio_conversate_ui_event_name_5b16fc"):
        if f" {symbol}\n" not in defined:
            raise RuntimeError(f"Conversate body missing: {symbol}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_REPORT_CHAIN_INTEGRATION",
              "prior_candidate": ref(PRIOR), "report_candidate": ref(REPORT),
              "candidate_object": ref(CANDIDATE),
              "sources": [ref(REPORT_SOURCE), ref(NAME_SOURCE)],
              "verifiers": [ref(REPORT_VERIFY), ref(NAME_VERIFY)],
              "oracle_receipts": [ref(report_oracle_path), ref(name_oracle_path)],
              "native_bodies": ["0x5b02e4..0x5b03c1", "0x5b16fc..0x5b1715"],
              "oracle_cases": [900, 261],
              "unresolved_before": 120, "unresolved_after": 120,
              "removed_imports": ["audio_conversate_report_5b02e4"],
              "new_imports": ["audio_conversate_ui_event_names_20000560"],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "UI event-name RAM table content and startup initializer at 0x20000560 remain unauthenticated."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
