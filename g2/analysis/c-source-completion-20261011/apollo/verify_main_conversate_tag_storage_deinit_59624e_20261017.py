#!/usr/bin/env python3
"""Compare stock/C tag-storage exit, list traversal, logging and state reset."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_storage_deinit_59624e.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-tag-storage-deinit-59624e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_tag_node_free_596188": (0x596188, "free"),
    "audio_uart_buffer_zero": (0x43c0e4, "zero"),
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
    obj, elf_path = OUT / "tag-storage-deinit.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_exit_child_59624e",
                    "--defsym=audio_conversate_tag_storage_state_200e3af4=0x200e3af4",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, initialized, count, flags):
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
        state = 0x200e3af4
        nodes = [0x200e4000 + i * 0x100 for i in range(count)]
        cpu.mem_write(state, struct.pack("<I", nodes[0] if nodes else 0) +
                      struct.pack("<I", nodes[-1] if nodes else 0) +
                      struct.pack("<HBB", count, initialized, 0x5a))
        for i, node in enumerate(nodes):
            prev = nodes[(i + 1) % count]
            next_node = nodes[(i - 1) % count]
            cpu.mem_write(node + 0x14, struct.pack("<II", prev, next_node))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def cstr(address):
            data = bytearray()
            for i in range(160):
                byte = cpu.mem_read(address + i, 1)[0]
                if byte == 0:
                    return data.decode("utf-8", "replace")
                data.append(byte)
            raise RuntimeError("unterminated log string")

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
            if name == "free":
                events.append((name, r0))
            elif name == "zero":
                events.append((name, r0, r1, r2))
                machine.mem_write(r0, bytes([r2 & 0xff]) * r1)
            elif name == "flags":
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif name == "extended":
                line, message = struct.unpack("<II", machine.mem_read(sp, 8))
                item = (name, r0, cstr(r1), cstr(r2), cstr(r3), line, cstr(message))
                if line in (0xae, 0xc0):
                    item += (struct.unpack("<I", machine.mem_read(sp + 8, 4))[0],)
                events.append(item)
            else:
                item = (name, r0, cstr(r1), cstr(r2))
                if r0 == 0x10400000:
                    item += (r3,)
                events.append(item)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x59624e if native else symbols["audio_conversate_ui_exit_child_59624e"]
        cpu.emu_start(entry | 1, 0, count=500)
        if not done[0]:
            raise RuntimeError(f"tag storage exit did not return: {native} {initialized} {count} {flags}")
        words = [struct.unpack("<II", cpu.mem_read(node + 0x14, 8)) for node in nodes]
        return cpu.mem_read(state, 12), words, events

    cases = [(initialized, count, flags)
             for initialized in (0, 1) for count in (0, 1, 3)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"tag storage exit mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TAG_STORAGE_DEINIT_59624E_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x59624e..0x59635f",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Node-free, buffer-zero and logging are controlled lower boundaries; valid circular lists of up to three nodes were replayed."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
