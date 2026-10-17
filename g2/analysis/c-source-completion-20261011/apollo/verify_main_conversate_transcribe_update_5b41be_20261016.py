#!/usr/bin/env python3
"""Bounded stock/C replay of transcribe ring and concatenated output."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_transcribe_update_5b41be.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-transcribe-update-5b41be"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_log_flags": (0x101010, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101020, 0x43d574, "extended"),
          "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
          "audio_uart_buffer_zero": (0x101040, 0x43c0e4, "zero"),
          "audio_queue_copy_bytes": (0x101050, 0x439be4, "copy")}
RAM = {"audio_conversate_prep_note_ram_200d7630": 0x200d7630,
       "audio_conversate_transcribe_output_200e2ae4": 0x200e2ae4,
       "audio_conversate_transcribe_length_2007439c": 0x2007439c,
       "audio_conversate_transcribe_flag_20074fa2": 0x20074fa2}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-transcribe.o", OUT / "oracle-transcribe.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_transcribe_update_5b41be",
                    *[f"--defsym={name}=0x{address:x}" for name, address in RAM.items()],
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, index, flag, size, final, prior, flags):
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
        initial = bytearray(0xb4b1)
        ring_offset = 0x88
        initial[ring_offset+0x1008] = index
        for k in range(4):
            off = ring_offset+k*0x402
            struct.pack_into("<H", initial, off, prior if k != index else 3)
            initial[off+2:off+2+(prior if k != index else 3)] = bytes([65+k])*(prior if k != index else 3)
        cpu.mem_write(0x200d7630, bytes(initial))
        cpu.mem_write(0x20074fa2, bytes([flag]))
        cpu.mem_write(0x2007439c, (999).to_bytes(4, "little"))
        cpu.mem_write(0x200e2ae4, bytes([0x5a])*0x1008)
        packet = bytearray(0x408)
        struct.pack_into("<H", packet, 0, size)
        packet[2:2+size] = bytes((i*9+7)&255 for i in range(size))
        struct.pack_into("<I", packet, 0x404, final)
        cpu.mem_write(0x20022000, bytes(packet))
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
            kind = ({v[1]: v[2] for v in LOWERS.values()} if native else
                    {v[0]: v[2] for v in LOWERS.values()}).get(pc)
            if kind is None:
                return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "zero":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2]&255])*r[1])
            elif kind == "copy":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2])))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b41be if native else symbols["audio_conversate_transcribe_update_5b41be"]) | 1,
                      0, count=1500)
        if not done[0]:
            raise RuntimeError("Transcribe update did not return")
        return {"events": events,
                "ring_sha256": hashlib.sha256(bytes(cpu.mem_read(0x200d76b8, 0x1009))).hexdigest(),
                "output_sha256": hashlib.sha256(bytes(cpu.mem_read(0x200e2ae4, 0x1008))).hexdigest(),
                "length": word(0x2007439c),
                "flag": bytes(cpu.mem_read(0x20074fa2, 1)).hex()}

    cases = [(False, 0, 0, 0, 0, 0, 0),
             (False, 3, 1, 7, 1, 4, 7)]
    cases += [(True, index, flag, size, final, prior, 0)
              for index in range(4) for flag in (0, 1)
              for size, final, prior in ((0, 0, 0), (5, 1, 3), (1024, 0, 2))]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Transcribe update mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_TRANSCRIBE_UPDATE_5B41BE_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Zero, copy and logging are controlled lower contracts.",
                         "Input sizes are bounded to the observed slot capacity; wider caller validation remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
