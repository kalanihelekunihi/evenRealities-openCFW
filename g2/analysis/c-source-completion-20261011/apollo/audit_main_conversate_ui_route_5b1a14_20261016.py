#!/usr/bin/env python3
"""Pin source-linked saved/network-error UI route and sender frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-route-5b1a14"
PRIOR = BASE / "main-conversate-ui-route-5b5b96/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_route_5b1a14.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_ui_route_5b1a14_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_route_5b1a14"}
    added = {"audio_conversate_ui_message_send_58bfb2"}
    if (len(before), len(after)) != (141, 141) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate saved/network-error route frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B1A14_C" or
            oracle["cases"] != 180 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate saved/network-error route oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_route_5b1a14\n" not in defined:
        raise RuntimeError("Conversate saved/network-error route body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B1A14_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 180,
              "unresolved_before": 141, "unresolved_after": 141,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Message sender 0x58bfb2 and other UI routes remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
