#!/usr/bin/env python3
"""Pin the source-linked Conversate release body and its child frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-route-release-58c84e"
PRIOR = BASE / "main-conversate-ui-route-5b34a0-5b34b4/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_route_release_58c84e.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_route_release_58c84e_20261016.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_route_release_58c84e"}
    added = {"audio_conversate_route_before_release_58c836",
             "audio_conversate_route_set_property_597f52",
             "audio_conversate_route_cleanup_597ee0"}
    if (len(before), len(after)) != (145, 147) or before-after != removed or after-before != added:
        raise RuntimeError("Conversate release frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_RELEASE_58C84E_C" or
            oracle["cases"] != 20 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate release oracle changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_route_release_58c84e\n" not in defined:
        raise RuntimeError("Conversate release body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_RELEASE_58C84E_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 20,
              "unresolved_before": 145, "unresolved_after": 147,
              "removed_imports": sorted(removed), "new_imports": sorted(added),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Release route is source-linked; its three child bodies remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
