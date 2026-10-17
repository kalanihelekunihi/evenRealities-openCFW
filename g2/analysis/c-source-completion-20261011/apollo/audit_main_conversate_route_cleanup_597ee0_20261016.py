#!/usr/bin/env python3
"""Pin source-linked Conversate release cleanup and remaining frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-route-cleanup-597ee0"
PRIOR = BASE / "main-conversate-route-get-release-pair-597f82/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_route_cleanup_597ee0.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_conversate_release_animimage_aliases_20261016.py"
PROVIDER = G2 / "components/audio/uart_thread_source_candidate/display_lv_animimage_597ea6.c"
UPSTREAM = BASE / "main-lv-animimage-597ea6/receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_route_cleanup_597ee0"}
    if (len(before), len(after)) != (146, 145) or before-after != removed or after-before:
        raise RuntimeError("Conversate cleanup frontier changed")
    oracle = json.loads((HERE / "oracle-receipt.json").read_text())
    if (oracle["status"] != "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_CLEANUP_597EE0_C" or
            oracle["cases"] != 20 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["provider_source_sha256"] != sha(PROVIDER) or
            oracle["oracle_elf_sha256"] != sha(ROOT / oracle["oracle_elf"])):
        raise RuntimeError("Conversate cleanup oracle changed")
    upstream = json.loads(UPSTREAM.read_text())
    if (upstream["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIMIMAGE_C" or
            upstream["source_sha256"] != sha(PROVIDER) or
            upstream["oracle_receipt_sha256"] != sha(ROOT / upstream["oracle_receipt"]) or
            "audio_lv_label_style_call_597ee0" not in upstream["imports_resolved"]):
        raise RuntimeError("Existing animimage source provider changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_route_cleanup_597ee0\n" not in defined:
        raise RuntimeError("Conversate cleanup body missing")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_CLEANUP_597EE0_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "verifier": ref(VERIFY),
              "provider_source": ref(PROVIDER), "provider_receipt": ref(UPSTREAM),
              "oracle_receipt": ref(HERE / "oracle-receipt.json"),
              "native_body": oracle["native_body"], "oracle_cases": 20,
              "unresolved_before": 146, "unresolved_after": 145,
              "removed_imports": sorted(removed), "new_imports": [],
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Existing source-owned animimage provider is bound; full display behavior and final placement remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
