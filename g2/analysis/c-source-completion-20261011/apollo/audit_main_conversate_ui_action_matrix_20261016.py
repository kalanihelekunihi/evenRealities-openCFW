#!/usr/bin/env python3
"""Pin exact source-owned route data and the 26 unresolved native handlers."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-ui-action-matrix-686920"
PRIOR = BASE / "main-conversate-timer-transition/candidate.o"
CANDIDATE = HERE / "candidate.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_action_matrix_686920.c"
GENERATOR = G2 / "analysis/c-source-completion-20261011/apollo/generate_main_conversate_ui_action_matrix_c_20261016.py"
EVIDENCE = G2 / "analysis/c-source-completion-20261011/apollo/main-conversate-ui-action-matrix-20261016.json"
RESOLVED = BASE / "main-conversate-ui-action-5b1724/action-matrix.elf"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    evidence = json.loads(EVIDENCE.read_text())
    addresses = sorted({int(route["handler_pointer"], 16)
                        for row in evidence["rows"] for route in row["routes"]
                        if route["handler_pointer"]})
    handlers = {f"audio_conversate_ui_route_{address & ~1:06x}" for address in addresses}
    if evidence["status"] != "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_MATRIX" or len(addresses) != 26:
        raise RuntimeError("stock matrix evidence changed")
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {"audio_conversate_ui_action_matrix_686920"}
    if (len(before), len(after)) != (120, 145) or before-after != removed or after-before != handlers:
        raise RuntimeError("UI matrix handler frontier changed")
    with RESOLVED.open("rb") as stream:
        section = ELFFile(stream).get_section_by_name(".g2_conversate_ui_action_matrix_686920")
        if section is None:
            raise RuntimeError("resolved UI matrix section missing")
        resolved = section.data()
    payload = STOCK.read_bytes()[32:]
    stock = payload[0x686920-0x438000:0x686920-0x438000+1176]
    if len(resolved) != 1176 or resolved != stock:
        raise RuntimeError("source-owned UI matrix differs from stock")
    if hashlib.sha256(stock).hexdigest() != evidence["raw_matrix_sha256"]:
        raise RuntimeError("stock matrix hash changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(CANDIDATE)], text=True)
    if " audio_conversate_ui_action_matrix_686920\n" not in defined:
        raise RuntimeError("source-owned UI matrix missing")
    record = {"status": "PASS_EXACT_MAIN_CONVERSATE_UI_ACTION_MATRIX_C_INTEGRATION",
              "prior_candidate": ref(PRIOR), "candidate_object": ref(CANDIDATE),
              "source": ref(SOURCE), "generator": ref(GENERATOR),
              "matrix_evidence": ref(EVIDENCE), "resolved_table_elf": ref(RESOLVED),
              "native_matrix_address": "0x686920", "matrix_bytes": 1176,
              "matrix_sha256": hashlib.sha256(stock).hexdigest(),
              "active_routes": 50, "distinct_native_handlers": 26,
              "unresolved_before": 120, "unresolved_after": 145,
              "removed_imports": sorted(removed), "new_imports": sorted(handlers),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "The route table is byte exact after binding to native addresses; all 26 target bodies still require source reconstruction."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
