#!/usr/bin/env python3
"""Compare LV position setter call and coordinate effects with official Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_position_440246.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x440246-0x438000:0x44035e-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-position-440246"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "flag": (0x43e0e0, "audio_uart_lv_obj_has_flag_43e0e0"),
    "scroll_x": (0x44e486, "audio_uart_lv_obj_x_44e486"),
    "scroll_y": (0x44e498, "audio_uart_lv_obj_y_44e498"),
    "pad_x": (0x43efc6, "audio_uart_lv_style_pad_left_43efc6"),
    "pad_y": (0x43f022, "audio_uart_lv_style_pad_top_43f022"),
    "invalidate": (0x440656, "audio_uart_page_invalidate_440656"),
    "coords": (0x43fc2a, "audio_uart_lv_obj_coords_43fc2a"),
    "content_coords": (0x43feca, "audio_uart_lv_obj_content_coords_43feca"),
    "contains": (0x450f28, "audio_uart_lv_area_contains_450f28"),
    "scrollbar": (0x44f2ca, "audio_uart_lv_scrollbar_invalidate_44f2ca"),
    "move_children": (0x44035e, "audio_uart_lv_obj_move_children_44035e"),
    "event": (0x451670, "audio_uart_lv_obj_event_451670"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n" + "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b,uint32_t c,uint32_t d){{__asm volatile("bx lr");}}'
        for _, symbol in PROVIDERS.values()))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_position_440246",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(value): return (value & 0xffffffff).to_bytes(4, "little")
    def area(values): return b"".join(u32(v) for v in values)

    def run(compiled, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        obj, parent = 0x20001000, 0x20002000
        uc.mem_write(obj + 4, u32(parent if config["parent"] else 0))
        uc.mem_write(obj + 0x14, area((100, 50, 130, 70)))
        uc.mem_write(parent + 0x14, area((200, 90, 300, 180)))
        uc.reg_write(A.UC_ARM_REG_R0, obj)
        uc.reg_write(A.UC_ARM_REG_R1, config["x"] & 0xffffffff)
        uc.reg_write(A.UC_ARM_REG_R2, config["y"] & 0xffffffff)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): key
                 for key, (address, symbol) in PROVIDERS.items()}
        trace, contains_count = [], 0

        def observe(cpu, address, size, _):
            nonlocal contains_count
            key = hooks.get(address)
            if key is None: return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            if key == "coords":
                cpu.mem_write(r1, area((100, 50, 130, 70)))
            elif key == "content_coords":
                cpu.mem_write(r1, area((210, 100, 290, 170)))
            elif key == "contains":
                trace.append((key, bytes(cpu.mem_read(r0, 16)),
                              bytes(cpu.mem_read(r1, 16))))
                cpu.reg_write(A.UC_ARM_REG_R0, config["contains"][contains_count])
                contains_count += 1
            elif key == "move_children":
                trace.append((key, r0, r1, cpu.reg_read(A.UC_ARM_REG_R2),
                              cpu.reg_read(A.UC_ARM_REG_R3)))
            elif key == "event":
                trace.append((key, r0, r1, cpu.reg_read(A.UC_ARM_REG_R2)))
            else:
                trace.append((key, r0))
            if key not in ("contains",):
                cpu.reg_write(A.UC_ARM_REG_R0, config.get(key, 0) & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols["audio_uart_lv_obj_position_440246"] if compiled else 0x440246
        uc.emu_start(start | 1, 0x600000, count=2500)
        return trace, bytes(uc.mem_read(obj + 0x14, 16))

    cases = 0
    for parent in (False, True):
        for flag in (0, 1):
            for x, y in ((100, 50), (0, 0), (7, -9), (200, 90)):
                for contains in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    config = {"parent": parent, "flag": flag, "x": x, "y": y,
                              "scroll_x": 11, "scroll_y": 7,
                              "pad_x": 3, "pad_y": 5, "contains": contains}
                    native = run(False, config)
                    candidate = run(True, config)
                    if native != candidate:
                        raise AssertionError((config, native, candidate))
                    cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_OBJ_POSITION_440246",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": BODY_SHA,
               "source_owned_symbols": ["audio_uart_lv_obj_position_440246"],
               "cases": cases,
               "limits": ["Lower providers were controlled hooks; final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
