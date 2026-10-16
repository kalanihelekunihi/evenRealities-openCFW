#!/usr/bin/env python3
"""Compare LV object position refresh against the official Main Thumb body."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_refr_pos_43ffd0.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x43ffd0-0x438000:0x440246-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-lv-refr-pos-43ffd0"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "positioned": (0x43f612, "audio_uart_lv_layout_positioned_43f612"),
    "parent": (0x44dca2, "audio_uart_lv_obj_parent_44dca2"),
    "x": (0x43eee2, "audio_uart_lv_style_x_43eee2"),
    "y": (0x43eeec, "audio_uart_lv_style_y_43eeec"),
    "cw": (0x43fe16, "audio_uart_lv_obj_content_width_43fe16"),
    "ch": (0x43fe70, "audio_uart_lv_obj_content_height_43fe70"),
    "sw": (0x43eea6, "audio_uart_lv_style_width_43eea6"),
    "sh": (0x43eec4, "audio_uart_lv_style_height_43eec4"),
    "tx": (0x43ef02, "audio_uart_lv_style_translate_x_43ef02"),
    "ty": (0x43ef0c, "audio_uart_lv_style_translate_y_43ef0c"),
    "w": (0x43fd9e, "audio_uart_lv_obj_width_43fd9e"),
    "h": (0x43fdda, "audio_uart_lv_obj_height_43fdda"),
    "align": (0x43eef6, "audio_uart_lv_style_align_43eef6"),
    "base_dir": (0x43efba, "audio_uart_lv_style_base_dir_43efba"),
    "set_pos": (0x440246, "audio_uart_lv_obj_position_440246"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n" + "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b,uint32_t c){{__asm volatile("bx lr");}}'
        for key, (_, symbol) in PROVIDERS.items() if key not in ("tx", "ty")) +
        '\n__attribute__((naked)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}\n')
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_refr_pos_43ffd0",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, values):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.reg_write(A.UC_ARM_REG_R0, 0x20001000)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): key
                 for key, (address, symbol) in PROVIDERS.items()}
        if compiled:
            hooks[symbols["audio_uart_lv_style_property_44bdea"] & ~1] = "property"
        seen = []

        def observe(cpu, address, size, _):
            key = hooks.get(address)
            if key is None:
                return
            if key == "property":
                property_id = cpu.reg_read(A.UC_ARM_REG_R2)
                key = "tx" if property_id == 0x6c else "ty" if property_id == 0x6d else key
            obj = cpu.reg_read(A.UC_ARM_REG_R0)
            if key == "set_pos":
                seen.append((key, obj, cpu.reg_read(A.UC_ARM_REG_R1),
                             cpu.reg_read(A.UC_ARM_REG_R2)))
            else:
                seen.append((key, obj))
            cpu.reg_write(A.UC_ARM_REG_R0, values.get(key, 0) & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = (symbols["audio_uart_lv_obj_refr_pos_43ffd0"]
                 if compiled else 0x43ffd0)
        uc.emu_start(start | 1, 0x600000, count=2500)
        return seen

    cases = 0
    for positioned in (0, 1):
        for parent in (0, 0x20002000):
            for x in (0, 19, 0x20000032, 0x2ffffffb):
                for y in (0, 13, 0x20000019):
                    for align in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                        values = {"positioned": positioned, "parent": parent,
                                  "x": x, "y": y, "cw": 320, "ch": 180,
                                  "sw": 60, "sh": 50, "tx": 0x2000000a,
                                  "ty": 0x20000005, "w": 44, "h": 24,
                                  "align": align, "base_dir": 1}
                        native = run(False, values)
                        candidate = run(True, values)
                        if native != candidate:
                            raise AssertionError((values, native, candidate))
                        cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_REFR_POS_43FFD0",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": BODY_SHA,
               "source_owned_symbols": ["audio_uart_lv_obj_refr_pos_43ffd0",
                                        "audio_uart_lv_style_translate_x_43ef02",
                                        "audio_uart_lv_style_translate_y_43ef0c"],
               "cases": cases,
               "limits": ["Provider calls were controlled hooks; position setter remains a deeper source dependency.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
