#!/usr/bin/env python3
"""Bounded native/C replay of Conversate prep-note data update."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_data_update_5b43ee.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-update-5b43ee"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_log_flags": (0x101010, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101020, 0x43d574, "extended"),
          "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
          "audio_queue_copy_bytes": (0x101040, 0x439be4, "copy"),
          "audio_uart_buffer_zero": (0x101050, 0x43c0e4, "zero")}
NATIVE = {v[1]: v[2] for v in LOWERS.values()}
COMPILED = {v[0]: v[2] for v in LOWERS.values()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-update.o", OUT / "oracle-update.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_prep_note_update_5b43ee",
                    "--defsym=audio_conversate_prep_note_ram_200d7630=0x200d7630",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, title_size, packets, flags):
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
        initial = bytes((i * 17 + 3) & 255 for i in range(0xb4b1))
        cpu.mem_write(0x200d7630, initial)
        data = bytearray((i * 7 + 11) & 255 for i in range(136))
        data[0:2] = struct.pack("<H", title_size)
        data[0x84:0x88] = struct.pack("<I", packets)
        cpu.mem_write(0x20022000, bytes(data))
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20022000 if present else 0)
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
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None:
                return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "copy":
                events.append((kind, r[0] == 0x200d7630, r[1] == 0x20022000, r[2]))
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
            elif kind == "zero":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes((r[2] & 255,)) * r[1])
            elif kind == "extended":
                fmt = string(word(sp + 4))
                vals = tuple(word(sp + 8 + i * 4) for i in range(fmt.count("%u")))
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, vals))
            elif kind == "simple":
                fmt = string(r[1])
                vals = tuple(([r[3]] if "%u" in fmt else []) +
                             [word(sp + i * 4) for i in range(max(0, fmt.count("%u") - 1))])
                events.append((kind, r[0], fmt, string(r[2]), vals))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b43ee if native else symbols["audio_conversate_prep_note_update_5b43ee"]) | 1,
                      0, count=700)
        if not done[0]:
            raise RuntimeError("Prep-note update did not return")
        output = bytes(cpu.mem_read(0x200d7630, 0xb4b1))
        return {"events": events, "state_sha256": hashlib.sha256(output).hexdigest(),
                "header": output[:136].hex(),
                "overlap": output[0x7dfc:0x7e08].hex()}

    bases = [(False, 0, 0), (True, 0, 0), (True, 1, 17),
             (True, 127, 0x12345678), (True, 128, 65536),
             (True, 255, 0xffffffff), (True, 65535, 0xabcd)]
    cases = [(present, title, packets, flags) for flags in (0, 1, 2, 4, 7)
             for present, title, packets in bases]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Prep-note mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_PREP_NOTE_UPDATE_5B43EE_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Copy, zero and log helpers are controlled lower contracts.",
                         "The overlapping RAM region is source-owned but startup initialization is not proven."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
