#!/usr/bin/env python3
"""Check C-owned stdio scratch and all composed fixed Main RAM spans."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-tx-packet/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-scratch"
OBJ = OUT / "candidate.o"
SOURCE = G2 / "components/main/flashdb_print_wrapper_candidates_20261010/print_buffer_2006b930.c"
SDK_H = G2 / "analysis/coverage-audit-parallel-2026-10-09/sdk-runtime-link-review-2026-10-10/am_util_stdio.h"
SDK_C = G2 / "analysis/coverage-audit-parallel-2026-10-09/sdk-runtime-link-review-2026-10-10/am_util_stdio.c"
LINK = G2 / "analysis/c-source-completion-20261011/apollo/main_combined_ram_scratch_20261016.ld"
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
    for value in (0x2006b930, 0x2006bd30):
        if value.to_bytes(4, "little") not in payload:
            raise RuntimeError(f"stock RAM address absent: {value:#x}")
    if ("#define AM_PRINTF_BUFSIZE       1024" not in SDK_H.read_text() or
            "static char g_prfbuf[AM_PRINTF_BUFSIZE];" not in SDK_C.read_text() or
            "g2_flashdb_print_buffer[1024]" not in SOURCE.read_text()):
        raise RuntimeError("attributable stdio buffer evidence changed")
    spans = {
        ".g2_print_buffer_2006b930": (0x2006b930, 1024),
        ".g2_ram_2006bd30": (0x2006bd30, 1024),
        ".g2_transaction_transport_2007397c": (0x2007397c, 30),
        ".g2_tx_packet_2007399c": (0x2007399c, 30),
        ".g2_pdm_clock_pin_words": (0x2007421c, 8),
        ".g2_ram_200742f0": (0x200742f0, 4),
    }
    with OBJ.open("rb") as stream:
        elf = ELFFile(stream)
        for name, (address, size) in spans.items():
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"fixed RAM span lost: {name}")
    ordered = sorted((address, address + size, name) for name, (address, size) in spans.items())
    if any(end > ordered[index+1][0] for index, (_, end, _) in enumerate(ordered[:-1])):
        raise RuntimeError("fixed RAM span collision")
    symbols = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", str(OBJ)], text=True).splitlines():
        fields = line.split()
        if fields and fields[-1] in ("g2_flashdb_print_buffer", "g2_audio_dump_buffer",
                "g2_audio_transaction_transport", "g2_audio_tx_packet", "g2_pdm_clock_pin_50",
                "g2_pdm_clock_pin_51", "g2_flashdb_print_sink"):
            symbols[fields[-1]] = int(fields[0], 16)
    expected = {"g2_flashdb_print_buffer": 0x2006b930, "g2_audio_dump_buffer": 0x2006bd30,
                "g2_audio_transaction_transport": 0x2007397c, "g2_audio_tx_packet": 0x2007399c,
                "g2_pdm_clock_pin_50": 0x2007421c, "g2_pdm_clock_pin_51": 0x20074220,
                "g2_flashdb_print_sink": 0x200742f0}
    if symbols != expected or undefined(BASE) - undefined(OBJ) != {"g2_flashdb_print_buffer"} or \
            undefined(OBJ) - undefined(BASE) or len(undefined(BASE)) != 124 or len(undefined(OBJ)) != 123:
        raise RuntimeError("combined RAM symbols or import closure changed")
    oracle = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/main-flashdb-short-log-20261010/verify_flashdb_print.py")], text=True).strip()
    if oracle != "PASS flashdb print 96":
        raise RuntimeError("print wrapper oracle changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_COMBINED_RAM_SCRATCH_C",
        "stock_payload_sha256": PAYLOAD_SHA,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "sdk_header": str(SDK_H.relative_to(ROOT)), "sdk_header_sha256": sha(SDK_H),
        "sdk_source": str(SDK_C.relative_to(ROOT)), "sdk_source_sha256": sha(SDK_C),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "fixed_ram_sections": {name: {"address": hex(address), "bytes": size}
                               for name, (address, size) in spans.items()},
        "print_wrapper_oracle": oracle, "unresolved_before": 124, "unresolved_after": 123,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The pinned SDK default gives 1024 bytes; the exact next known dump-buffer base corroborates the span, but a production linker map is unavailable.",
                   "The formatter accepts no capacity argument, so arbitrary output may exceed this scratch span.",
                   "Six fixed sections are collision-free with one another; this does not prove all Main RAM allocations or startup initialization."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(receipt))


if __name__ == "__main__":
    main()
