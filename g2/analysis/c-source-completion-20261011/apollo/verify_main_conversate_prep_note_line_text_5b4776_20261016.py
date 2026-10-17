#!/usr/bin/env python3
"""Direct stock/C comparison of the indexed prep-note line-text routine."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_line_text_5b4776.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-line-text-5b4776"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_conversate_prep_note_utf8_prefix_5b3ef8": (0x101010, 0x5b3ef8, "utf"),
          "audio_queue_copy_bytes": (0x101020, 0x439be4, "copy")}
META = 0x200d86c4
TEXT = 0x200df430
DEST = 0x20005000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_prep_note_line_text_5b4776",
                    "--defsym=audio_conversate_prep_note_ram_200d7630=0x200d7630",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, index, capacity, layout, missing_dest):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        meta = bytearray(64)
        content = b"Alpha\r\nBeta\nSnow\xe2\x98\x83\r\n"
        meta[4:8] = struct.pack("<HH", len(content), 3)
        offsets = {"valid": (0, 7, 12, 19),
                   "reverse": (7, 0, 12, 19),
                   "overflow": (0, 7, 12, 40)}[layout]
        for n, offset in enumerate(offsets):
            meta[10 + n * 2:12 + n * 2] = struct.pack("<H", offset)
        cpu.mem_write(META, bytes(meta))
        cpu.mem_write(TEXT, content)
        cpu.mem_write(DEST, b"Z" * 64)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, index)
        cpu.reg_write(A.UC_ARM_REG_R1, 0 if missing_dest else DEST)
        cpu.reg_write(A.UC_ARM_REG_R2, capacity)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            if kind == "utf":
                events.append((kind, r[0] - TEXT, r[1]))
                value = r[1]
            else:
                chunk = bytes(machine.mem_read(r[1], r[2]))
                events.append((kind, r[0] - DEST, r[1] - TEXT, chunk))
                machine.mem_write(r[0], chunk)
                value = r[0]
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b4776 if native else symbols["audio_conversate_prep_note_line_text_5b4776"]
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]:
            raise RuntimeError("prep-note line text did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(DEST, 32))

    cases = [(index, capacity, layout, missing)
             for index in (0, 1, 2, 3, 0x10000)
             for capacity in (0, 1, 3, 6, 9, 129)
             for layout in ("valid", "reverse", "overflow")
             for missing in (False, True)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"prep-note line text mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_LINE_TEXT_5B4776_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b4776..0x5b4845",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["UTF-8 prefix counting and byte copying remain controlled lower boundaries.",
                         "Indexed metadata bounds, trim, copy length and output bytes are compared directly."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
