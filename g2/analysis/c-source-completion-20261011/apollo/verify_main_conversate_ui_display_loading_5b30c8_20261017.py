#!/usr/bin/env python3
"""Direct stock/C replay of Conversate loading-page route with controlled calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_display_loading_5b30c8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-ui-display-loading-5b30c8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_reply_list_get_5b43e8": (0x110010, 0x5b43e8, "replies", 0),
    "audio_conversate_prep_note_get_5b4766": (0x110020, 0x5b4766, "notes", 0),
    "audio_uart_page_43ded4": (0x110030, 0x43ded4, "hide", 2),
    "audio_uart_page_43de82": (0x110040, 0x43de82, "create", 1),
    "audio_uart_page_43f4c0": (0x110050, 0x43f4c0, "size", 3),
    "audio_uart_page_43f09a": (0x110060, 0x43f09a, "position", 3),
    "audio_uart_page_44129e": (0x110070, 0x44129e, "style_a", 3),
    "audio_uart_page_44131c": (0x110080, 0x44131c, "style_b", 3),
    "audio_uart_page_44146a": (0x110090, 0x44146a, "style_c", 3),
    "audio_conversate_display_style_5b22bc": (0x1100a0, 0x5b22bc, "display_style", 3),
    "audio_uart_page_43dfa4": (0x1100b0, 0x43dfa4, "show", 2),
    "audio_lv_label_create_499416": (0x1100c0, 0x499416, "label", 1),
    "audio_uart_page_43f6b8": (0x1100d0, 0x43f6b8, "align", 4),
    "audio_uart_page_44104c": (0x1100e0, 0x44104c, "color", 1),
    "audio_uart_page_44140e": (0x1100f0, 0x44140e, "color_style", 3),
    "audio_uart_page_44143e": (0x110100, 0x44143e, "font", 3),
    "audio_uart_page_44145a": (0x110110, 0x44145a, "mode_a", 3),
    "audio_lv_label_mode_499678": (0x110120, 0x499678, "mode_b", 2),
    "audio_uart_page_460084": (0x110130, 0x460084, "key_length", 1),
    "audio_uart_page_45fffe": (0x110140, 0x45fffe, "translate", 2),
    "g2_audio_dump_snprintf": (0x110150, 0x44b728, "format", 4),
    "audio_lv_label_text_49942e": (0x110160, 0x49942e, "label_text", 2),
    "audio_uart_page_58c238": (0x110170, 0x58c238, "timer", 3),
    "audio_log_flags": (0x110180, 0x43d0ce, "flags", 0),
    "audio_log_extended": (0x110190, 0x43d574, "extended", 4),
    "compressed_log_output": (0x1101a0, 0x43ce9e, "compressed", 3),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("authenticated Main payload changed")
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b30c8",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    "--defsym=audio_conversate_machine_context_200e3aec=0x200e3aec",
                    "--defsym=audio_conversate_ui_app_id_200743a0=0x200743a0",
                    "--defsym=audio_uart_ring_primary_head_cell=0x200746dc",
                    "--defsym=audio_conversate_loading_text_200711dc=0x200711dc",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, state, context, notes_count, replies_count, index, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        root = 0x20071368
        cpu.mem_write(root+4, struct.pack("<I", 0x20002000))
        cpu.mem_write(root+0x84, struct.pack("<I", index))
        cpu.mem_write(0x200e3aec, bytes((context,)))
        cpu.mem_write(0x200743a0, struct.pack("<I", 0x20005000))
        cpu.mem_write(0x200746dc, struct.pack("<I", 0x2000a000))
        cpu.mem_write(0x20003000, struct.pack("<H", notes_count)+b"Notes text\x00")
        cpu.mem_write(0x20004000, struct.pack("<H", replies_count))
        for i in range(3):
            cpu.mem_write(0x20004000+i*0x88+0xa, f"Reply{i}".encode()+b"\x00")
        cpu.mem_write(0x2000b000, b"Start\x00")
        cpu.mem_write(0x2000b100, b"Prep %s\x00")
        cpu.reg_write(A.UC_ARM_REG_R0, state)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x7788)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x11ff01)
        events, done = [], [False]
        lowers = {row[1 if native else 0]: (row[2], row[3]) for row in LOWERS.values()}

        def cstr(address):
            result = bytearray()
            for i in range(256):
                value = cpu.mem_read(address+i, 1)[0]
                if value == 0:
                    return result.decode("utf-8", "replace")
                result.append(value)
            raise RuntimeError("unterminated source string")

        def hook(machine, pc, _size, _user):
            if pc == 0x11ff00:
                done[0] = True
                machine.emu_stop()
                return
            row = lowers.get(pc)
            if row is None:
                return
            kind, argc = row
            registers = [machine.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            args = registers[:argc]
            if kind in ("notes", "replies"):
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0x20003000 if kind == "notes" else 0x20004000)
            elif kind == "create":
                events.append((kind, *args))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20006000)
            elif kind == "label":
                events.append((kind, *args))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20006100)
            elif kind == "color":
                events.append((kind, *args))
                machine.reg_write(A.UC_ARM_REG_R0, 0xabcdef)
            elif kind == "key_length":
                events.append((kind, cstr(args[0])))
                machine.reg_write(A.UC_ARM_REG_R0, len(cstr(args[0])))
            elif kind == "translate":
                key = cstr(args[0])
                events.append((kind, key, args[1]))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0x2000b000 if key == "ID_CONVERSATE_START" else 0x2000b100)
            elif kind == "format":
                destination, capacity, fmt, argument = args
                fmt_text, arg_text = cstr(fmt), cstr(argument)
                rendered = (fmt_text % arg_text).encode()
                events.append((kind, destination, capacity, fmt_text, arg_text))
                data = rendered[:max(0, capacity-1)]
                machine.mem_write(destination, data+b"\x00")
                machine.reg_write(A.UC_ARM_REG_R0, len(rendered))
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                events.append((kind, args[0], cstr(args[1]), cstr(args[2]),
                               cstr(args[3]), line, cstr(fmt)))
            elif kind == "compressed":
                events.append((kind, args[0], cstr(args[1]), cstr(args[2])))
            else:
                events.append((kind, *args))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b30c8 if native else symbols["audio_conversate_ui_route_5b30c8"]
        cpu.emu_start(entry | 1, 0, count=2000)
        if not done[0]:
            raise RuntimeError("loading route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), \
            bytes(cpu.mem_read(root, 0x98)), bytes(cpu.mem_read(0x200711dc, 201))

    cases = [(state, context, notes_count, replies_count, index, flags)
             for state in (0, 1, 2, 3, 255)
             for context in (0, 1)
             for notes_count in (0, 1)
             for replies_count in (0, 2)
             for index in (0, 1, 0xffffffff, 2)
             for flags in (0, 2)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"loading route mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_LOADING_5B30C8_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b30c8..0x5b3249",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Page/LVGL, locale, snprintf and logging calls are controlled lower boundaries; loading text RAM extent remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
