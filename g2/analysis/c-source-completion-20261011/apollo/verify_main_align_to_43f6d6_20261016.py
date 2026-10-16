#!/usr/bin/env python3
"""Compare stock and C 0x43f6d6 with deterministic lower-call boundaries."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_align_to_43f6d6.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY = IMAGE[0x43f6d6-0x438000:0x43fc2a-0x438000]
assert hashlib.sha256(BODY).hexdigest() == "d50d4f057c691d118d54f4efbd06ca6041c5852f6055900d4ab68c7c451ef81d"
LOWER = {
    "audio_uart_page_43f66c": 0x43f66c,
    "audio_uart_lv_obj_parent_44dca2": 0x44dca2,
    "audio_uart_lv_style_pad_left_43efc6": 0x43efc6,
    "audio_uart_lv_style_pad_top_43f022": 0x43f022,
    "audio_uart_lv_style_base_dir_43efba": 0x43efba,
    "audio_uart_lv_obj_width_43fd9e": 0x43fd9e,
    "audio_uart_lv_obj_height_43fdda": 0x43fdda,
    "audio_uart_lv_obj_content_width_43fe16": 0x43fe16,
    "audio_uart_lv_obj_content_height_43fe70": 0x43fe70,
    "audio_uart_lv_scroll_right_44e67a": 0x44e67a,
    "audio_uart_lv_scroll_left_44e586": 0x44e586,
    "audio_uart_lv_scroll_top_44e4aa": 0x44e4aa,
    "audio_uart_page_4411d4": 0x4411d4,
    "audio_uart_page_43f09a": 0x43f09a,
}
VOID = {"audio_uart_page_43f66c", "audio_uart_page_4411d4", "audio_uart_page_43f09a"}
with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n" + "\n".join(
        f'__attribute__((naked)) {"void" if n in VOID else "int32_t"} {n}'
        '(uint32_t a,uint32_t b,uint32_t c){__asm volatile("bx lr");}'
        for n in LOWER))
    elf = Path(temp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-Wno-unused-parameter", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43f6d6",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, mode, xoff, yoff, rtl):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        obj, ref, parent = 0x20000100, 0x20000200, 0x20000300
        for address, x, y in ((obj, 11, 17), (ref, 29, 37), (parent, 41, 43)):
            uc.mem_write(address + 20, x.to_bytes(4, "little"))
            uc.mem_write(address + 24, y.to_bytes(4, "little"))
        for reg, val in ((A.UC_ARM_REG_R0, obj), (A.UC_ARM_REG_R1, ref),
                         (A.UC_ARM_REG_R2, mode), (A.UC_ARM_REG_R3, xoff),
                         (A.UC_ARM_REG_SP, 0x2000f000), (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, val)
        uc.mem_write(0x2000f000, yoff.to_bytes(4, "little"))
        hooks = {((symbols[n] & ~1) if compiled else addr): n
                 for n, addr in LOWER.items()}
        trace = []

        def lower(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            args = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            trace.append((name, args if name in VOID or name.endswith("43efba") else args[:1]))
            if name.endswith("44dca2"):
                value = parent
            elif name.endswith("43efba"):
                value = rtl
            elif name.endswith("43efc6"):
                value = {parent: 7, ref: 13}[args[0]]
            elif name.endswith("43f022"):
                value = {parent: 9, ref: 19}[args[0]]
            elif name.endswith("43fd9e"):
                value = {obj: 22, ref: 57}[args[0]]
            elif name.endswith("43fdda"):
                value = {obj: 15, ref: 43}[args[0]]
            elif name.endswith("43fe16"):
                value = 61
            elif name.endswith("43fe70"):
                value = 47
            elif name.endswith("44e67a"):
                value = 5
            elif name.endswith("44e586"):
                value = 6
            elif name.endswith("44e4aa"):
                value = 8
            else:
                value = 0
            cpu.reg_write(A.UC_ARM_REG_R0, value)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, lower)
        entry = symbols["audio_uart_page_43f6d6"] if compiled else 0x43f6d6
        uc.emu_start(entry | 1, 0x600000, count=3000)
        return trace

    cases = []
    for mode in range(23):
        for xoff, yoff in ((0, 0), (8, 28), (0x20000032, 0x20000019),
                           (0x2fffffff, 0x30000000),
                           (0x3ffffffe, 0xffffffff)):
            for rtl in (0, 1):
                stock = run(False, mode, xoff, yoff, rtl)
                candidate = run(True, mode, xoff, yoff, rtl)
                assert stock == candidate, (mode, xoff, yoff, rtl, stock, candidate)
                cases.append((mode, xoff, yoff, rtl))

OUT = G2 / "build/c-firmware/20261016/main-align-to-43f6d6"
OUT.mkdir(parents=True, exist_ok=True)
receipt = {"status": "PASS_NATIVE_MAIN_ALIGN_TO_43F6D6", "cases": len(cases),
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": hashlib.sha256(BODY).hexdigest(),
           "lower_boundary": LOWER,
           "limits": ["Deterministic lower-call comparisons do not prove lower implementation or final RAM placement.",
                      "Null assertions and unmodeled object memory are not exercised."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
