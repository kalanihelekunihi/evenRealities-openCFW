#!/usr/bin/env python3
"""Pin two source-linked UI action handlers and their direct child frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-route-5b34a0-5b34b4"
PRIOR = BASE / "main-conversate-ui-action-matrix-686920/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_route_5b34a0_5b34b4.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_route_5b34a0_5b34b4_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b34a0", "audio_conversate_ui_route_5b34b4"}
    added = {"audio_conversate_route_scroll_5b22fa", "audio_conversate_route_release_58c84e"}
    if (len(before), len(after)) != (145, 145) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate route wrapper frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B34A0_5B34B4_C" or
            oracle["cases"] != 256 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate route wrapper oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    for symbol in removed:
        if f" {symbol}\n" not in defined:
            raise RuntimeError(f"Conversate route body missing: {symbol}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B34A0_5B34B4_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_bodies": oracle["native_bodies"], "oracle_cases": 256,
              "unresolved_before": 145, "unresolved_after": 145,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Two UI route wrappers are source-linked; their scroll/release child bodies and 24 other route handlers remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
