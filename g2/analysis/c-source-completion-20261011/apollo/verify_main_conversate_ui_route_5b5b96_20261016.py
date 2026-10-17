#!/usr/bin/env python3
"""Direct stock/C replay of Conversate previous-item route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_route_5b5b96.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-route-5b5b96"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_conversate_reply_list_get_5b43e8": (0x101010, 0x5b43e8, "replies"),
          "audio_lv_child_44dce2": (0x101020, 0x44dce2, "child"),
          "audio_terminal_session_animate_5896fc": (0x101030, 0x5896fc, "animate")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b5cc8-0x438000:0x5b5ccc-0x438000] == struct.pack("<I", 0x20071368)
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b5b96",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, index, reply_pointer, count, prior, parent, old, child_result, state):
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
        root = 0x20071368
        for offset, value in ((0x64, parent), (0x7c, prior),
                              (0x80, old), (0x84, index)):
            cpu.mem_write(root + offset, struct.pack("<I", value))
        cpu.mem_write(0x20005000, struct.pack("<H", count))
        cpu.reg_write(A.UC_ARM_REG_R0, state)
        cpu.reg_write(A.UC_ARM_REG_R1, 0xaabbccdd)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
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
            if kind == "replies":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, reply_pointer)
            elif kind == "child":
                events.append((kind, machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, child_result)
            else:
                events.append((kind, machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1),
                               machine.reg_read(A.UC_ARM_REG_R2)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b5b96 if native else symbols["audio_conversate_ui_route_5b5b96"]
        cpu.emu_start(entry | 1, 0, count=160)
        if not done[0]:
            raise RuntimeError("previous-item route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(root, 0xac))

    cases = [(i, p, c, oldptr, parent, old, child, state)
             for i in (0, 1, 3, 0xffffffff)
             for p in (0, 0x20005000)
             for c in (0, 2)
             for oldptr in (0, 0x20007000)
             for parent in (0x20008000,)
             for old in (0x20009000,)
             for child in (0, 0x2000a000)
             for state in (0, 255)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"previous-item mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B5B96_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b5b96..0x5b5bef",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Reply getter, child lookup and animation scheduler are controlled lower call boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
