#!/usr/bin/env python3
"""Bounded native/C replay of Conversate protobuf-to-node conversion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_node_from_pb_595f4c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-tag-node-from-pb-595f4c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_log_flags": (0x101010, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101020, 0x43d574, "extended"),
          "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
          "codec_allocate": (0x101040, 0x474cd2, "alloc"),
          "audio_file_heap_free": (0x101050, 0x474d16, "free"),
          "audio_uart_buffer_zero": (0x101060, 0x43c0e4, "zero"),
          "audio_queue_copy_bytes": (0x101070, 0x439be4, "copy")}
NATIVE = {v[1]: v[2] for v in LOWERS.values()}
COMPILED = {v[0]: v[2] for v in LOWERS.values()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-from-pb.o", OUT / "oracle-from-pb.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_tag_node_from_pb_595f4c",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, text_length, extended_length, alloc_first, alloc_second, flags):
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
        packet = bytearray((i * 7 + 11) & 255 for i in range(0x490))
        packet[0] = 3
        packet[2:4] = struct.pack("<H", text_length)
        packet[0x84:0x86] = struct.pack("<H", extended_length)
        packet[0x488:0x48c] = struct.pack("<I", 0x12345678)
        cpu.mem_write(0x20022000, bytes(packet))
        cpu.mem_write(0x20024200, b"\xaa" * 28)
        cpu.mem_write(0x20030000, b"\xbb" * 256)
        cpu.mem_write(0x20040000, b"\xcc" * 256)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20022000)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x20024200)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done, alloc_index = [], [False], [0]

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
            elif kind == "alloc":
                index = alloc_index[0]
                alloc_index[0] += 1
                allowed = (alloc_first, alloc_second)[min(index, 1)]
                events.append((kind, index, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  (0x20030000 + index * 0x10000) if allowed else 0)
            elif kind == "zero":
                events.append((kind, r[0] == 0x20024200, r[1], r[2]))
                machine.mem_write(r[0], bytes((r[2] & 255,)) * r[1])
            elif kind == "copy":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
            elif kind == "free":
                events.append((kind, r[0]))
            elif kind == "extended":
                fmt = string(word(sp + 4))
                value = word(sp + 8) if "%d" in fmt else None
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, value))
            elif kind == "simple":
                fmt = string(r[1])
                events.append((kind, r[0], fmt, string(r[2]),
                               r[3] if "%d" in fmt else None))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x595f4c if native else symbols["audio_conversate_tag_node_from_pb_595f4c"]) | 1,
                      0, count=1200)
        if not done[0]:
            raise RuntimeError("Tag-node conversion did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events,
                "node": bytes(cpu.mem_read(0x20024200, 28)).hex(),
                "first_buffer": bytes(cpu.mem_read(0x20030000, 130)).hex(),
                "second_buffer": bytes(cpu.mem_read(0x20040000, 130)).hex()}

    bases = [(0, 0, 1, 1), (5, 0, 1, 1), (0, 4, 1, 1),
             (5, 4, 1, 1), (5, 4, 0, 1), (5, 4, 1, 0),
             (0, 4, 0, 1), (127, 1, 1, 1)]
    cases = [(text_length, extended_length, alloc_first, alloc_second, flags)
             for flags in (0, 1, 2, 4, 7)
             for text_length, extended_length, alloc_first, alloc_second in bases]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Tag conversion mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_TAG_NODE_FROM_PB_595F4C_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Allocator, copy, zero, free and logs are controlled lower contracts.",
                         "No heap capacity or physical hardware behavior is proven."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
