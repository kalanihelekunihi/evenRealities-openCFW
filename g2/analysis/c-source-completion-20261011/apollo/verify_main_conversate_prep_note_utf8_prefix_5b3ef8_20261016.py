#!/usr/bin/env python3
"""Direct stock/C replay of bounded UTF-8 prefix counting."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_utf8_prefix_5b3ef8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-utf8-prefix-5b3ef8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-utf8.o", OUT / "oracle-utf8.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_prep_note_utf8_prefix_5b3ef8",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, data, length):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, raw in segments:
                if raw:
                    cpu.mem_write(address, raw)
        cpu.mem_write(0x20022000, data + bytes(8))
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20022000)
        cpu.reg_write(A.UC_ARM_REG_R1, length)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b3ef8 if native else symbols["audio_conversate_prep_note_utf8_prefix_5b3ef8"]) | 1,
                      0, count=400)
        if not done[0]:
            raise RuntimeError("UTF-8 prefix did not return")
        return cpu.reg_read(A.UC_ARM_REG_R0)

    strings = [b"", b"hello", b"a\xc2\xa2b", b"\xe2\x82\xac",
               b"\xf0\x9f\x98\x80", b"\xc2x", b"\xe2\x82x",
               b"\xf0\x9fx", b"\x80\xbf\xff", b"\xc0\x80",
               b"\xf8\x80", b"\xe2", b"\xf0\x9f\x98"]
    cases = [(raw.hex(), n) for raw in strings
             for n in (0, 1, 2, 3, 4, len(raw), len(raw)+1, 65536, 65537)]
    for encoded, length in cases:
        data = bytes.fromhex(encoded)
        a, b = run(True, data, length), run(False, data, length)
        if a != b:
            raise RuntimeError(f"UTF-8 prefix mismatch {(encoded, length)}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_UTF8_PREFIX_5B3EF8_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Direct function replay covers selected valid and malformed byte strings.",
                         "The wider prep-note and Main image behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
