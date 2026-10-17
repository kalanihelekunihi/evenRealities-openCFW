#!/usr/bin/env python3
"""Direct stock/C comparison of the Conversate menu-list route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_menu_list_5b59fa.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-menu-list-5b59fa"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
DATA = {
    "audio_conversate_ui_settings_extension_20071369": 0x20071369,
    "audio_conversate_ui_app_id_200743a0": 0x200743a0,
    "audio_uart_ring_primary_head_cell": 0x200746dc,
    "audio_conversate_menu_icon_76a2a0": 0x76a2a0,
    "audio_conversate_prep_icon_76a47c": 0x76a47c,
}
LOWERS = {
    "audio_conversate_reply_list_get_5b43e8": (0x5b43e8, "replies"),
    "audio_uart_page_43de82": (0x43de82, "root"),
    "audio_uart_page_43f4c0": (0x43f4c0, "size"),
    "audio_uart_page_43f09a": (0x43f09a, "position"),
    "audio_uart_page_44129e": (0x44129e, "style_a"),
    "audio_uart_page_44131c": (0x44131c, "style_b"),
    "audio_uart_page_44146a": (0x44146a, "style_c"),
    "audio_conversate_menu_style_5b5720": (0x5b5720, "menu_style"),
    "audio_uart_page_43dfa4": (0x43dfa4, "root_flag"),
    "audio_uart_page_44d878": (0x44d878, "clean"),
    "audio_lv_label_create_499416": (0x499416, "label"),
    "audio_lv_label_text_49942e": (0x49942e, "label_text"),
    "audio_uart_page_460084": (0x460084, "locale_index"),
    "audio_uart_page_45fffe": (0x45fffe, "locale_text"),
    "audio_uart_page_44104c": (0x44104c, "color"),
    "audio_uart_page_44140e": (0x44140e, "label_color"),
    "audio_uart_page_44143e": (0x44143e, "label_font"),
    "audio_uart_page_44145a": (0x44145a, "label_mode"),
    "audio_conversate_prep_button_create_5b1150": (0x5b1150, "button"),
    "audio_conversate_ui_main_list_container_5b12ba": (0x5b12ba, "list"),
    "audio_conversate_ui_slot_fade_5b1072": (0x5b1072, "fade"),
    "audio_terminal_ui_scroll_to_view_44ea2e": (0x44ea2e, "scroll"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "menu-list.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b59fa",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    *[f"--defsym={name}=0x{address:x}" for name, address in DATA.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, state, count, selected, missing_button):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x400000)
        if not native:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        cpu.mem_write(0x200743a0, struct.pack("<I", 0x21))
        cpu.mem_write(0x200746dc, struct.pack("<I", 0x200d0000))
        cpu.mem_write(0x2007136c, struct.pack("<I", 0x20081000))
        cpu.mem_write(0x200d6b88, struct.pack("<H", count))
        cpu.mem_write(0x200d6b88 + 0xaa4, struct.pack("<I", selected))
        for i in range(count):
            cpu.mem_write(0x200d6b88 + i * 0x88 + 4, struct.pack("<I", 0x100 + i))
            cpu.mem_write(0x200d6b88 + i * 0x88 + 0xa, f"reply {i}".encode() + b"\0")
        cpu.mem_write(0x20090000, b"select prep notes\0")
        cpu.mem_write(0x20090100, b"skip and start\0")
        cpu.reg_write(A.UC_ARM_REG_R0, state)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x1234)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: kind for address, kind in LOWERS.values()}
        events, done, buttons = [], [False], [0]

        def cstr(address):
            out = bytearray()
            for i in range(120):
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
            kind = kinds.get(pc)
            if kind is None:
                return
            r0, r1, r2 = (machine.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if kind == "replies":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, 0x200d6b88)
            elif kind == "root":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20081000)
            elif kind == "label":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20082000)
            elif kind == "locale_index":
                events.append((kind, cstr(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, 4)
            elif kind == "locale_text":
                key = cstr(r0)
                events.append((kind, key, r1))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0x20090000 if "SELECT" in key else 0x20090100)
            elif kind == "label_text":
                events.append((kind, r0, cstr(r1)))
            elif kind == "button":
                number = buttons[0]
                buttons[0] += 1
                events.append((kind, r0, r1, cstr(r2) if number else cstr(r2)))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0 if number == missing_button else 0x20083000 + number * 0x1000)
            elif kind == "list":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20084000)
            elif kind == "color":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x200000ff)
            elif kind in ("root_flag", "clean", "fade", "scroll"):
                events.append((kind, r0, r1) if kind in ("root_flag", "fade", "scroll")
                              else (kind, r0))
            else:
                events.append((kind, r0, r1, r2))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b59fa if native else symbols["audio_conversate_ui_route_5b59fa"]
        cpu.emu_start(entry | 1, 0, count=1200)
        if not done[0]:
            raise RuntimeError("menu list did not return")
        return (events, cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(0x20071368, 0x90)))

    cases = [(state, count, selected, missing)
             for state in (0, 1, 256)
             for count in (0, 1, 3)
             for selected in (0, 0x100, 0x102)
             for missing in (-1, 1)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"menu list mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MENU_LIST_5B59FA_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b59fa..0x5b5b95",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL, locale, list getter and button factory are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
