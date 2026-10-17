#!/usr/bin/env python3
"""Pin source-linked Conversate release-pair getter and remaining frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-route-get-release-pair-597f82"
PRIOR = BASE / "main-conversate-route-before-release-58c836/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_route_get_release_pair_597f82.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_route_get_release_pair_597f82_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_route_get_release_pair_597f82"}
    if (len(before), len(after)) != (147, 146) or before-after != removed or after-before:
        raise RuntimeError("Conversate release-pair getter frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_GET_RELEASE_PAIR_597F82_C" or
            oracle["cases"] != 20 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate release-pair getter oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_route_get_release_pair_597f82\n" not in defined:
        raise RuntimeError("Conversate release-pair getter body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_GET_RELEASE_PAIR_597F82_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 20,
              "unresolved_before": 147, "unresolved_after": 146,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Getter strings are source-owned; runtime logger backend and final placement remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
