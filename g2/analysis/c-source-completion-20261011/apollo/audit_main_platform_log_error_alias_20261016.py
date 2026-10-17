#!/usr/bin/env python3
"""Pin UART detailed-log ABI alias to the selected extended logger."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-combined-ram-scratch/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-platform-log-error-alias"
OBJ = OUT / "candidate.o"
SOURCE = G2 / "components/audio/uart_instance_offline/instance.c"
LINK = G2 / "analysis/c-source-completion-20261011/apollo/main_platform_log_error_alias_43d574.ld"
PRIOR = G2 / "analysis/audio-uart-instance-closure-2026-10-09"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    expected_literals = {0x7846d0: b"sync.module.uart", 0x7846e4: b"uart_instance_init",
                         0x75c1c8: b"Failed to create uart sync thread"}
    for address, value in expected_literals.items():
        if payload[address-0x438000:address-0x438000+len(value)+1] != value+b"\0":
            raise RuntimeError(f"UART diagnostic literal changed: {address:#x}")
    prior_receipt = PRIOR / "reproduction-receipt.json"
    prior_results = PRIOR / "results.json"
    reproduction = json.loads(prior_receipt.read_text())
    results = json.loads(prior_results.read_text())
    if (reproduction["sources"][str(SOURCE.relative_to(ROOT))] != sha(SOURCE) or
            "platform_log_error = 0x43D575" not in reproduction["link_script"] or
            results["status"] != "PASS" or results["cases"] != 16 or results["differences"]):
        raise RuntimeError("prior original/source UART wrapper evidence changed")
    symbols = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", str(OBJ)], text=True).splitlines():
        fields = line.split()
        if fields and fields[-1] in ("audio_log_extended", "platform_log_error"):
            symbols[fields[-1]] = fields[0]
    if (set(symbols) != {"audio_log_extended", "platform_log_error"} or
            symbols["audio_log_extended"] != symbols["platform_log_error"] or
            undefined(BASE) - undefined(OBJ) != {"platform_log_error"} or
            undefined(OBJ) - undefined(BASE) or
            len(undefined(BASE)) != 123 or len(undefined(OBJ)) != 122):
        raise RuntimeError("UART detailed logger alias or import reduction changed")
    with OBJ.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in ((".g2_print_buffer_2006b930", 0x2006b930, 1024),
                                    (".g2_pdm_clock_pin_words", 0x2007421c, 8),
                                    (".g2_ram_200742f0", 0x200742f0, 4)):
            section = elf.get_section_by_name(name)
            if section is None or section["sh_addr"] != address or section["sh_size"] != size:
                raise RuntimeError(f"combined RAM placement lost: {name}")
    record = {
        "status": "PASS_BOUNDED_MAIN_UART_DETAILED_LOGGER_ALIAS",
        "stock_payload_sha256": PAYLOAD_SHA, "native_logger_entry": "0x43d574",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "prior_reproduction": str(prior_receipt.relative_to(ROOT)), "prior_reproduction_sha256": sha(prior_receipt),
        "prior_results": str(prior_results.relative_to(ROOT)), "prior_results_sha256": sha(prior_results),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "reused_original_source_cases": 16, "unresolved_before": 123, "unresolved_after": 122,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The 16 original/source UART wrapper cases are prior saved evidence, not new executions.",
                   "The detailed logger body itself retains product state, formatter and output gates.",
                   "The source prototype names its fourth and sixth parameters misleadingly; observed literal values and ARM positional call ABI identify function then format."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
