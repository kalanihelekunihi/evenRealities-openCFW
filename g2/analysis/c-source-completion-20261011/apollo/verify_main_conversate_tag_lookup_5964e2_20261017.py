#!/usr/bin/env python3
"""Direct stock/C comparison of Conversate tag lookup and list traversal."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_get_by_index_5964e2.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-tag-lookup-5964e2"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "g2_log_module_length": (0x44a43c, "strlen"),
    "audio_log_flags": (0x43d0ce, "flags"),
    "audio_log_extended": (0x43d574, "extended"),
    "compressed_log_output": (0x43ce9e, "compressed"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "tag-lookup.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_tag_get_by_index_5964e2",
                    "--defsym=audio_conversate_tag_storage_state_200e3af4=0x200e3af4",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, initialized, count, index, topology, kind, text_mode, flags):
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
        nodes = (0x200e4000, 0x200e4100, 0x200e4200)
        head = nodes[0] if topology != "none" else 0
        cpu.mem_write(0x200e3af4, struct.pack("<I", head))
        cpu.mem_write(0x200e3af4 + 8, struct.pack("<H", count))
        cpu.mem_write(0x200e3af4 + 10, bytes([initialized]))
        cpu.mem_write(0x200e5000, b"valid tag\0")
        cpu.mem_write(0x200e5100, b"\0")
        link = {
            "none": (0, 0, 0),
            "self": (nodes[0], 0, 0),
            "null": (0, 0, 0),
            "chain": (nodes[1], nodes[2], nodes[0]),
            "short": (nodes[1], 0, 0),
        }[topology]
        for i, node in enumerate(nodes):
            pointer = {"valid": 0x200e5000, "empty": 0x200e5100,
                       "null": 0}[text_mode]
            cpu.mem_write(node, struct.pack("<I", kind))
            cpu.mem_write(node + 4, struct.pack("<I", pointer))
            cpu.mem_write(node + 0x14, struct.pack("<I", link[i]))
        cpu.reg_write(A.UC_ARM_REG_R0, index)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def cstr(address):
            out = bytearray()
            for i in range(180):
                byte = cpu.mem_read(address + i, 1)[0]
                if byte == 0:
                    return out.decode("utf-8", "replace")
                out.append(byte)
            raise RuntimeError("unterminated string")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            name = kinds.get(pc)
            if name is None:
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if name == "strlen":
                value = cstr(r0)
                events.append((name, value))
                machine.reg_write(A.UC_ARM_REG_R0, len(value.encode()))
            elif name == "flags":
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif name == "extended":
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                extras = {
                    0x105: (), 0x10b: (8, 12), 0x115: (8,),
                    0x11b: (8,), 0x120: (8,), 0x125: (8,),
                }[line]
                values = [struct.unpack("<I", machine.mem_read(sp + offset, 4))[0]
                          for offset in extras]
                if line == 0x125:
                    values = [cstr(values[0])]
                events.append((name, r0, cstr(r1), cstr(r2), cstr(r3), line,
                               cstr(fmt), *values))
            else:
                if r0 == 0x04000000:
                    values = ()
                elif r0 == 0x10800000:
                    values = (r3, struct.unpack("<I", machine.mem_read(sp, 4))[0])
                elif r0 == 0x04400000:
                    values = (r3,)
                    if "Invalid tag text" in cstr(r1):
                        values = (cstr(r3),)
                else:
                    values = (r3,)
                events.append((name, r0, cstr(r1), cstr(r2), *values))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5964e2 if native else symbols["audio_conversate_tag_get_by_index_5964e2"]
        cpu.emu_start(entry | 1, 0, count=900)
        if not done[0]:
            raise RuntimeError("tag lookup did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = [(initialized, count, index, topology, kind, text_mode, flags)
             for initialized, count, index, topology, kind, text_mode in
             ((0, 1, 0, "self", 1, "valid"),
              (1, 0, 0, "self", 1, "valid"),
              (1, 1, 0, "none", 1, "valid"),
              (1, 1, 0, "self", 1, "valid"),
              (1, 3, 1, "self", 1, "valid"),
              (1, 3, 2, "self", 1, "valid"),
              (1, 3, 1, "null", 1, "valid"),
              (1, 3, 1, "short", 1, "valid"),
              (1, 3, 2, "chain", 1, "valid"),
              (1, 3, 0, "self", 0, "valid"),
              (1, 3, 0, "self", 5, "valid"),
              (1, 3, 0, "self", 1, "null"),
              (1, 3, 0, "self", 1, "empty"),
              (1, 3, 0x10000, "self", 1, "valid"))
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"tag lookup mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TAG_LOOKUP_5964E2_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5964e2..0x59674d",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["String length and logging calls are controlled lower boundaries; list fixtures cover selected finite topologies."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
