#!/usr/bin/env python3
"""Bounded stock/C replay of prep-note line offsets and count."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_layout_parse_5b4000.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-layout-parse-5b4000"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
          "audio_log_flags": (0x101020, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101030, 0x43d574, "extended"),
          "audio_log_simple": (0x101040, 0x43ce9e, "simple"),
          "audio_conversate_prep_note_measure_line_5b3f94": (0x101050, 0x5b3f94, "measure")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-layout.o", OUT / "oracle-layout.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_prep_note_layout_parse_5b4000",
                    "--defsym=audio_conversate_prep_note_ram_200d7630=0x200d7630",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, length, step, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        initial = bytes((i*7+11)&255 for i in range(0xb4b1))
        cpu.mem_write(0x200d7630, initial)
        cpu.mem_write(0x20022000, bytes((i*13+3)&255 for i in range(14000)))
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20022000 if present else 0)
        cpu.reg_write(A.UC_ARM_REG_R1, length)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = ({v[1]: v[2] for v in LOWERS.values()} if native else
                    {v[0]: v[2] for v in LOWERS.values()}).get(pc)
            if kind is None:
                return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "zero":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2]&255])*r[1])
            elif kind == "flags":
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "measure":
                events.append((kind, r[0], r[1], r[2]))
                machine.reg_write(A.UC_ARM_REG_R0, step)
            elif kind == "extended":
                fmt = string(word(sp+4))
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt,
                               tuple(word(sp+8+i*4) for i in range(fmt.count("%")))))
            elif kind == "simple":
                fmt = string(r[1])
                events.append((kind, r[0], fmt, string(r[2]),
                               tuple(([r[3]]+[word(sp+i*4) for i in range(5)])[:fmt.count("%")])) )
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b4000 if native else symbols["audio_conversate_prep_note_layout_parse_5b4000"]) | 1,
                      0, count=1200)
        if not done[0]:
            raise RuntimeError("Prep-note layout parse did not return")
        return {"events": events,
                "state_sha256": hashlib.sha256(bytes(cpu.mem_read(0x200d7630, 0xb4b1))).hexdigest(),
                "metadata": bytes(cpu.mem_read(0x200d86c4, 28)).hex()}

    fixtures = [(p, n, s, f) for p, n, s in
                ((False, 0, 0), (False, 3, 1), (True, 0, 0), (True, 1, 0),
                 (True, 1, 1), (True, 7, 2), (True, 7, 3),
                 (True, 7, 10), (True, 14000, 10000))
                for f in (0, 1, 2, 4, 7)]
    for fixture in fixtures:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Prep-note layout mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_LAYOUT_PARSE_5B4000_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(fixtures), "fixtures": fixtures,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Line measurement, zeroing and logging are controlled lower contracts.",
                         "The wider prep-note and Main image behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(fixtures), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
