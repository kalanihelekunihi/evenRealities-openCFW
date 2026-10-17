#!/usr/bin/env python3
"""Compare stock/C LVGL list insertion before head, middle and tail."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_list_insert_before_482b56.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-lv-list-insert-before-482b56"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LIST, NEW = 0x20010000, 0x20011000
NODES = [0x20012000, 0x20012100, 0x20012200]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "list-insert-before.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_list_insert_before_482b56",
                    "--defsym=audio_uart_lv_list_first=0x482cd8",
                    "--defsym=audio_uart_lv_list_prepend_482b12=0x482b12",
                    "--defsym=audio_uart_lv_malloc=0x44f718",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, count, index, allocation):
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
        cpu.mem_write(LIST, struct.pack("<III", 16, NODES[0] if count else 0,
                                         NODES[count - 1] if count else 0))
        cpu.mem_write(NEW, bytes([0xa5]) * 24)
        for i, node in enumerate(NODES):
            cpu.mem_write(node, bytes([0xa5]) * 24)
            cpu.mem_write(node + 16, struct.pack("<II",
                NODES[i - 1] if 0 < i < (count or 0) else 0,
                NODES[i + 1] if i + 1 < (count or 0) else 0))
        target = NODES[index] if index is not None else 0
        args = ((A.UC_ARM_REG_R0, LIST if count is not None else 0),
                (A.UC_ARM_REG_R1, target), (A.UC_ARM_REG_SP, 0x200ff000),
                (A.UC_ARM_REG_LR, 0x101f01))
        for reg, value in args:
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x44f718:
                events.append(("malloc", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, NEW if allocation else 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x482b56 if native else symbols["audio_uart_lv_list_insert_before_482b56"]
        cpu.emu_start(entry | 1, 0, count=3000)
        if not done[0]:
            raise RuntimeError(f"list insertion did not return: {native} {count} {index}")
        return (cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(LIST, 12)),
                bytes(cpu.mem_read(NEW, 24)),
                tuple(bytes(cpu.mem_read(node, 24)) for node in NODES), events)

    cases = [(None, None, True), (0, None, True)]
    cases += [(count, index, allocation)
              for count in (1, 2, 3) for index in range(count)
              for allocation in (False, True)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"list insertion mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_LV_LIST_INSERT_BEFORE_482B56_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x482b56..0x482bc8", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Allocator is a controlled callee; stock list prepend and first-node helpers execute from payload.",
                         "Valid one-to-three-node lists, null inputs and allocation failure are covered."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()
