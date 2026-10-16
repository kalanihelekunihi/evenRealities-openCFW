#!/usr/bin/env python3
"""Compare the button-fade Bezier path wrapper with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_path_450688.c"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-path-450688"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "list-anim-path-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "__attribute__((noinline,used)) int32_t audio_uart_lv_anim_bezier_450a04(void *a,int32_t b,int32_t c,int32_t d,int32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n")
    elf = OUT / "list-anim-path-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_anim_path_450688",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, pointer, value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cut = (syms["audio_uart_lv_anim_bezier_450a04"] if compiled else 0x450a04) & ~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc != cut:
                return
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            trace.append(tuple(cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)) +
                         (int.from_bytes(cpu.mem_read(sp, 4), "little"),))
            cpu.reg_write(A.UC_ARM_REG_R0, value)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_R0, pointer)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = syms["audio_uart_lv_anim_path_450688"] if compiled else 0x450688
        u.emu_start(entry | 1, 0x600000, count=1000)
        return trace, u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for pointer in (0, 0x20001000, 0x20003000):
        for value in (0, 1, 0x400, 0x7fffffff, 0xffffffff):
            case = (pointer, value)
            stock, selected = run(False, *case), run(True, *case)
            if stock != selected:
                raise RuntimeError(f"button path mismatch {case}: {stock} != {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_PATH_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Five-argument Bezier dispatch and return value",
              "limits": ["Bezier lower provider isolated; final placement remains open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()
