#!/usr/bin/env python3
"""Pin the shared native fatal callback cell across logger and WSF paths."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-platform-log-error-alias/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-fatal-hook-alias"
OBJ = OUT / "candidate.o"
OWNER = G2 / "components/audio/master_dispatch_candidate_20261014/shared_fatal_hook_state.c"
LINK = G2 / "analysis/c-source-completion-20261011/apollo/main_extended_log_fatal_hook_alias_2007456c.ld"
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
    for address in (0x43daa0, 0x45fa88, 0x569af4):
        if int.from_bytes(payload[address-0x438000:address-0x438000+4], "little") != 0x2007456c:
            raise RuntimeError(f"native fatal cell literal changed: {address:#x}")
    if ("audio_ble_wsf_assert_hook" not in OWNER.read_text() or
            "audio_uart_display_fatal_handler" not in OWNER.read_text()):
        raise RuntimeError("C fatal cell owner changed")
    names = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", str(OBJ)], text=True).splitlines():
        fields = line.split()
        if fields and fields[-1] in ("audio_ble_wsf_assert_hook", "audio_uart_display_fatal_handler",
                                     "g2_extended_log_fatal_callback"):
            names[fields[-1]] = int(fields[0], 16)
    if (set(names) != {"audio_ble_wsf_assert_hook", "audio_uart_display_fatal_handler",
                       "g2_extended_log_fatal_callback"} or set(names.values()) != {0x2007456c} or
            undefined(BASE) - undefined(OBJ) != {"g2_extended_log_fatal_callback"} or
            undefined(OBJ) - undefined(BASE) or
            len(undefined(BASE)) != 122 or len(undefined(OBJ)) != 121):
        raise RuntimeError("fatal hook alias or import reduction changed")
    with OBJ.open("rb") as stream:
        elf = ELFFile(stream)
        for name, address, size in ((".g2_ram_2007456c", 0x2007456c, 4),
                                    (".g2_print_buffer_2006b930", 0x2006b930, 1024),
                                    (".g2_pdm_clock_pin_words", 0x2007421c, 8)):
            section = elf.get_section_by_name(name)
            if (section is None or section["sh_type"] != "SHT_NOBITS" or
                    section["sh_addr"] != address or section["sh_size"] != size):
                raise RuntimeError(f"fixed RAM placement lost: {name}")
    oracle = subprocess.check_output(["/tmp/opencfw-oracle-venv/bin/python",
        str(G2 / "analysis/c-source-completion-20261011/apollo/verify_main_audio_enqueue_alloc_failure_45f402_oracle_20261015.py")], text=True).strip()
    if oracle != "PASS_EXPERIMENTAL_MAIN_AUDIO_ALLOC_FAILURE_ORACLE 10":
        raise RuntimeError("audio fatal callback caller oracle changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_SHARED_FATAL_HOOK_RAM_ALIAS",
        "stock_payload_sha256": PAYLOAD_SHA, "native_fatal_cell": "0x2007456c",
        "owner_source": str(OWNER.relative_to(ROOT)), "owner_source_sha256": sha(OWNER),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "audio_alloc_failure_oracle": oracle,
        "unresolved_before": 122, "unresolved_after": 121,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The alias shares one four-byte callback cell across three C names; it does not identify the production callback installer or target.",
                   "Ten controlled audio caller cases and stock literals do not establish all fatal continuations.",
                   "Seven pinned sections remain a partial Main RAM layout, not a whole-image collision or startup proof."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
