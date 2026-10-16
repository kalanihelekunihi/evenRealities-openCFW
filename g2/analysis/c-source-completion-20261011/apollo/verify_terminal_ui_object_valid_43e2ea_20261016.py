#!/usr/bin/env python3
"""Compare LVGL display/root membership traversal at descendant boundary."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_object_valid_43e2ea.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-object-valid-43e2ea"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void *audio_uart_lv_display_next_44fa22(void*p){return p;}
uint32_t audio_terminal_ui_object_descendant_43ee54(void*a,void*b){(void)a;(void)b;return 0;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "object-valid-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "object-valid-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_object_valid_43e2ea",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, display_count, root_count, target_index, descendant_index):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        displays = [0x20080000, 0x20081000][:display_count]
        roots = [[0x20090000 + 0x100*d + 4*i for i in range(root_count)]
                 for d in range(display_count)]
        flat = [x for row in roots for x in row]
        target = flat[target_index] if 0 <= target_index < len(flat) else 0x2009f000
        for d, display in enumerate(displays):
            root_array = 0x200a0000 + 0x100*d
            u.mem_write(display+0x2b8, root_array.to_bytes(4, "little"))
            u.mem_write(display+0x2d4, root_count.to_bytes(4, "little"))
            for i, root in enumerate(roots[d]):
                u.mem_write(root_array+4*i, root.to_bytes(4, "little"))
        nxt = (symbols["audio_uart_lv_display_next_44fa22"] if compiled else 0x44fa22)&~1
        desc = (symbols["audio_terminal_ui_object_descendant_43ee54"] if compiled else 0x43ee54)&~1
        calls = []
        def hook(cpu, pc, size, _):
            if pc == nxt:
                previous = cpu.reg_read(A.UC_ARM_REG_R0)
                calls.append(("next", previous))
                result = displays[0] if previous == 0 and displays else (
                    displays[displays.index(previous)+1]
                    if previous in displays and displays.index(previous)+1 < len(displays) else 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
            elif pc == desc:
                root = cpu.reg_read(A.UC_ARM_REG_R0)
                found = root in flat and flat.index(root) == descendant_index
                calls.append(("desc", root, cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_R0, 1 if found else 0)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_R0, target)
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_object_valid_43e2ea"] if compiled else 0x43e2ea
        u.emu_start(entry|1, 0x600000, count=100000)
        return u.reg_read(A.UC_ARM_REG_R0), calls

    cases = 0
    for args in itertools.product((0, 1, 2), (0, 1, 3), (-1, 0, 2, 4), (-1, 0, 1, 4)):
        stock, selected = run(False, *args), run(True, *args)
        if stock != selected:
            raise RuntimeError(f"object membership mismatch {args}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_OBJECT_VALID_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "0-2 displays, 0-3 roots, direct equality and descendant-call order",
              "limits": ["Descendant traversal and actual LVGL list mutation remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
