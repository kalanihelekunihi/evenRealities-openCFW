#!/usr/bin/env python3
"""Compare new-object list-animation geometry and scroll choice with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_new_prepare_5894d6.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-new-prepare-5894d6"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_lv_obj_parent_44dca2", 0x44dca2),
         ("audio_uart_lv_child_count_44ddea", 0x44ddea),
         ("audio_uart_lv_child_index_44de92", 0x44de92),
         ("audio_uart_lv_obj_y_44e498", 0x44e498),
         ("audio_uart_lv_obj_height_43fdda", 0x43fdda),
         ("audio_uart_lv_child_get_44dce2", 0x44dce2),
         ("audio_terminal_ui_scroll_to_view_44ea2e", 0x44ea2e))
OBJECT = 0x20001000
PARENT = 0x20002000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "list-anim-new-prepare-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) void *audio_uart_lv_obj_parent_44dca2(void*a){return a;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_child_count_44ddea(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_child_index_44de92(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_y_44e498(void*a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_obj_height_43fdda(void*a){(void)a;return 1;}\n"
                    "__attribute__((noinline,used)) void *audio_uart_lv_child_get_44dce2(void*a,uint32_t b){(void)b;return a;}\n"
                    "__attribute__((noinline,used)) void audio_terminal_ui_scroll_to_view_44ea2e(void*a,uint32_t b){(void)a;(void)b;}\n")
    elf = OUT / "list-anim-new-prepare-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_list_anim_new_prepare_5894d6",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, index, count, y, object_height, parent_height):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        trace = []

        def hook(cpu, pc, size, _):
            which = cuts.get(pc)
            if which is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            if which == 0:
                trace.append(("parent", r0))
                ret = PARENT
            elif which == 1:
                trace.append(("count", r0))
                ret = count
            elif which == 2:
                trace.append(("index", r0))
                ret = index
            elif which == 3:
                trace.append(("y", r0))
                ret = y & 0xffffffff
            elif which == 4:
                trace.append(("height", r0))
                ret = object_height if r0 == OBJECT else parent_height
            elif which == 5:
                trace.append(("child", r0, r1))
                ret = 0x20003000 + r1 * 4
            else:
                trace.append(("scroll", r0, r1))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, OBJECT)
        entry = symbols["audio_terminal_list_anim_new_prepare_5894d6"] if compiled else 0x5894d6
        u.emu_start(entry | 1, 0x600000, count=3000)
        return trace

    cases = 0
    for index in (0, 1, 2, 3, 5, 9):
        for count in (0, 1, 4, 10):
            for y in (-120, 0, 40, 160):
                for object_height, parent_height in ((40, 40), (40, 80), (40, 160), (80, 240)):
                    case = (index, count, y, object_height, parent_height)
                    stock = run(False, *case)
                    selected = run(True, *case)
                    if stock != selected:
                        raise RuntimeError(f"list animation new prepare mismatch {case}: {stock} != {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_NEW_PREPARE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Parent, child count/index, signed geometry divisions and scroll target",
              "limits": ["Zero object height and real LVGL child effects outside bounded oracle; final placement open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()
