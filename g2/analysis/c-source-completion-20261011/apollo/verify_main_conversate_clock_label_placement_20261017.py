#!/usr/bin/env python3
"""Link-check the exact 20-byte Conversate clock-label RAM slot."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_elapsed_label_5b22fa.c"
SCRIPT = G2 / "components/audio/uart_thread_source_candidate/conversate_clock_label_20073cac.ld"
OBJECT = G2 / "build/c-firmware/20261017/main-conversate-elapsed-label-5b22fa/elapsed-0.o"
OUT = G2 / "build/c-firmware/20261017/main-conversate-elapsed-label-5b22fa"
SYMBOL = "audio_conversate_clock_label_buffer_20073cac"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    probe = OUT / "placement-probe.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(SCRIPT),
                    str(OBJECT), "-o", str(probe)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(probe)], text=True)
    match = re.search(r"^([0-9a-f]+) ([0-9a-f]+) B " + SYMBOL + r"$", nm, re.M)
    if not match or (int(match[1], 16), int(match[2], 16)) != (0x20073cac, 20):
        raise RuntimeError("Conversate clock label address or extent changed")
    sections = subprocess.check_output(["arm-none-eabi-readelf", "-SW", str(probe)], text=True)
    if not re.search(r"\.bss\.opencfw\.conversate\.clock_label\s+NOBITS\s+20073cac\s+\S+\s+000014\b", sections):
        raise RuntimeError("Conversate clock label is not a 20-byte NOLOAD section")
    assert 0x20073c98 + 20 == 0x20073cac
    assert 0x20073cac + 20 == 0x20073cc0
    record = {
        "status": "PASS_MAIN_CONVERSATE_CLOCK_LABEL_PLACEMENT",
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": sha(SOURCE)},
        "linker_script": {"path": str(SCRIPT.relative_to(ROOT)), "sha256": sha(SCRIPT)},
        "placement_probe": {"path": str(probe.relative_to(ROOT)), "sha256": sha(probe)},
        "symbol": SYMBOL, "address": "0x20073cac", "size": 20,
        "section_type": "NOBITS", "adjacent_before_end": "0x20073cac",
        "adjacent_after_start": "0x20073cc0",
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "The isolated NOLOAD slot is exact; whole-image linker integration, other Main imports and hardware behavior remain open.",
    }
    receipt = OUT / "placement-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], sha(receipt))


if __name__ == "__main__":
    main()
