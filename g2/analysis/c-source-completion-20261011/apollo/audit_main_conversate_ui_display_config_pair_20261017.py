#!/usr/bin/env python3
"""Bind Conversate display-config route and its list-button setter."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261017"
PRIOR = BASE / "main-conversate-ui-child-style-clear-5b3340/candidate.o"
ROUTE = BASE / "main-conversate-ui-display-config-5b3398"
SETTER = BASE / "main-conversate-ui-slot-fade-5b1072"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def validate(here, status, cases, native_body, source):
    record = json.loads((here / "oracle-receipt.json").read_text())
    if (record["status"] != status or record["cases"] != cases or
            record["native_body"] != native_body or
            record["source_sha256"] != sha(source) or
            record["oracle_elf_sha256"] != sha(ROOT / record["oracle_elf"]) or
            record["source_complete"] or record["flashable"] or record["hardware_proof"]):
        raise RuntimeError(f"oracle changed: {here}")
    return record


def main():
    route_source = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_display_config_5b3398.c"
    setter_source = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_slot_fade_5b1072.c"
    validate(ROUTE, "PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_CONFIG_5B3398_C",
             160, "0x5b3398..0x5b349b", route_source)
    validate(SETTER, "PASS_DIRECT_MAIN_CONVERSATE_SLOT_FADE_5B1072_C",
             64, "0x5b1072..0x5b114f", setter_source)
    before, middle, after = [imports(path) for path in
                             (PRIOR, ROUTE / "candidate.o", SETTER / "candidate.o")]
    if (len(before) != 119 or len(middle) != 119 or len(after) != 118 or
            before-middle != {"audio_conversate_ui_route_5b3398"} or
            middle-before != {"audio_conversate_ui_slot_fade_5b1072"} or
            middle-after != {"audio_conversate_ui_slot_fade_5b1072"} or
            after-middle):
        raise RuntimeError("Main display-config provider frontier changed")
    defined = subprocess.check_output(["arm-none-eabi-nm", "--defined-only",
                                       str(SETTER / "candidate.o")], text=True)
    for name in ("audio_conversate_ui_route_5b3398", "audio_conversate_ui_slot_fade_5b1072"):
        if f" T {name}\n" not in defined:
            raise RuntimeError(f"missing provider {name}")
    record = {"status": "PASS_MAIN_CONVERSATE_DISPLAY_CONFIG_PAIR_INTEGRATION",
              "prior_candidate": ref(PRIOR), "route_candidate": ref(ROUTE / "candidate.o"),
              "candidate_object": ref(SETTER / "candidate.o"),
              "route_source": ref(route_source), "setter_source": ref(setter_source),
              "route_oracle": ref(ROUTE / "oracle-receipt.json"),
              "setter_oracle": ref(SETTER / "oracle-receipt.json"),
              "route_cases": 160, "setter_cases": 64,
              "unresolved_before": 119, "unresolved_after": 118,
              "removed_imports": ["audio_conversate_ui_route_5b3398"],
              "new_imports": [], "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports, exact final placement, whole-image source and hardware behavior remain open."}
    receipt = SETTER / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
