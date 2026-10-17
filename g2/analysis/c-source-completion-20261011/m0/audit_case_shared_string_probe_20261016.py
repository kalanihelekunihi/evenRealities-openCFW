#!/usr/bin/env python3
"""Pin the isolated CASE clear-LED string reuse size experiment."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261015/case-gc-size-frontier/mixed-oz-receipt.json"
OUT = G2 / "build/c-firmware/20261016/case-shared-string-probe"
SOURCE = G2 / "components/case/size_candidate_20261016/binary_56_exit_shared_string.c"
SOURCE_V2 = G2 / "components/case/size_candidate_20261016/binary_56_exit_shared_strings_v2.c"
V2 = G2 / "build/c-firmware/20261016/case-shared-strings-v2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        load = max(seg["p_vaddr"] + seg["p_filesz"] for seg in elf.iter_segments()
                   if seg["p_type"] == "PT_LOAD") - 0x08000000
        vector = elf.get_section_by_name(".isr_vector").data()
        symbols = {sym.name: sym["st_value"] for sym in elf.get_section_by_name(".symtab").iter_symbols()}
        return elf["e_entry"], load, vector, symbols


def main():
    base = json.loads(BASE.read_text())
    original = ROOT / base["elf"]
    candidate = OUT / "candidate.elf"
    combined = OUT / "combined.o"
    command = OUT / "command.o"
    startup = ROOT / base["startup_object"]
    receipt = json.loads(Path(str(command) + ".receipt.json").read_text())
    if (base["status"] != "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER"
            or sha(original) != base["elf_sha256"]
            or sha(startup) != base["startup_object_sha256"]
            or receipt["status"] != "ISOLATED_SIZE_EXPERIMENT"
            or receipt["output_sha256"] != sha(command)
            or receipt["override_sources"] != ["binary_56_exit_candidate.c=" + str(SOURCE.relative_to(ROOT))]
            or receipt["undefined_symbols"] or
            not any(row["compiled_sha256"] == sha(SOURCE)
                    and row["compiled_source"] == str(SOURCE)
                    for row in receipt["sources"])):
        raise RuntimeError("shared-string source or baseline changed")
    stock = STOCK.read_bytes()[32:]
    string = b"clear led status.\x00"
    if stock[0x131c:0x131c+len(string)] != string:
        raise RuntimeError("native clear-LED string changed")
    # Thumb ADR at 0x08001306 uses Align(PC,4) + imm8*4.
    adr = int.from_bytes(stock[0x1306:0x1308], "little")
    native_pointer = ((0x08001306 + 4) & ~3) + (adr & 0xff) * 4
    if adr != 0xa005 or native_pointer != 0x0800131c:
        raise RuntimeError("native clear-LED format pointer changed")
    adr2 = int.from_bytes(stock[0x130c:0x130e], "little")
    native_pointer2 = ((0x0800130c + 4) & ~3) + (adr2 & 0xff) * 4
    if (adr2 != 0xa008 or native_pointer2 != 0x08001330 or
            stock[0x1330:0x1333] != b"\r\n\x00"):
        raise RuntimeError("native CRLF format pointer changed")
    entry, load, vector, symbols = inspect(candidate)
    _, old_load, _, _ = inspect(original)
    matches = [i for i in range(46) if vector[i*4:i*4+4] == stock[i*4:i*4+4]]
    if (old_load != 63603 or load != 63585 or entry != 0x08000145
            or len(matches) != 13 or
            "case_binary_56_exit" not in symbols or
            "case_string_0800131c" not in symbols):
        raise RuntimeError("shared-string size/vector frontier changed")
    if subprocess.check_output(["arm-none-eabi-nm", "-u", str(candidate)], text=True).strip():
        raise RuntimeError("shared-string candidate has undefined symbols")
    v2_candidate = V2 / "candidate.elf"
    v2_command = V2 / "command.o"
    v2_receipt_path = Path(str(v2_command) + ".receipt.json")
    v2_receipt = json.loads(v2_receipt_path.read_text())
    _, v2_load, v2_vector, v2_symbols = inspect(v2_candidate)
    if (v2_receipt["output_sha256"] != sha(v2_command) or
            v2_receipt["override_sources"] !=
            ["binary_56_exit_candidate.c=" + str(SOURCE_V2.relative_to(ROOT))] or
            not any(row["compiled_sha256"] == sha(SOURCE_V2)
                    for row in v2_receipt["sources"]) or
            v2_load != load or v2_vector != vector or
            "case_string_08001330" not in v2_symbols or
            subprocess.check_output(["arm-none-eabi-nm", "-u", str(v2_candidate)], text=True).strip()):
        raise RuntimeError("shared-strings v2 frontier changed")
    result = {
        "status": "PASS_EXPERIMENTAL_CASE_SHARED_STRING_SIZE_REDUCTION",
        "baseline_receipt": str(BASE.relative_to(ROOT)), "baseline_receipt_sha256": sha(BASE),
        "candidate_source": str(SOURCE.relative_to(ROOT)), "candidate_source_sha256": sha(SOURCE),
        "stock_package_sha256": sha(STOCK), "native_string_address": "0x0800131c",
        "native_adr_address": "0x08001306", "native_adr_halfword": hex(adr),
        "native_crlf_adr_address": "0x0800130c", "native_crlf_adr_halfword": hex(adr2),
        "native_crlf_string_address": "0x08001330",
        "native_string_hex": string.hex(),
        "command_object": str(command.relative_to(ROOT)), "command_object_sha256": sha(command),
        "command_receipt_sha256": sha(Path(str(command) + ".receipt.json")),
        "startup_object": base["startup_object"], "startup_object_sha256": sha(startup),
        "combined_object": str(combined.relative_to(ROOT)), "combined_object_sha256": sha(combined),
        "candidate_elf": str(candidate.relative_to(ROOT)), "candidate_elf_sha256": sha(candidate),
        "v2_candidate_source": str(SOURCE_V2.relative_to(ROOT)),
        "v2_candidate_source_sha256": sha(SOURCE_V2),
        "v2_command_receipt_sha256": sha(v2_receipt_path),
        "v2_candidate_elf": str(v2_candidate.relative_to(ROOT)),
        "v2_candidate_elf_sha256": sha(v2_candidate),
        "v2_load_bytes": v2_load, "v2_additional_bytes_saved": load - v2_load,
        "baseline_load_bytes": old_load, "candidate_load_bytes": load,
        "bytes_saved": old_load - load, "stock_payload_bytes": len(stock),
        "remaining_overflow_bytes": load - len(stock), "entry": hex(entry),
        "matching_vector_words": matches,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The 18-byte saving is an isolated compiler/linker result, not final image admission.",
                   "Stock ADR selects the same string bytes; relocated candidate address and full runtime behavior remain unproved.",
                   "CASE still exceeds stock capacity and has 33 differing vector words."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], result["bytes_saved"], sha(path))


if __name__ == "__main__":
    main()
