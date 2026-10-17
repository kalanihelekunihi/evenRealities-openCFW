#!/usr/bin/env python3
"""Direct stock/C comparison of Conversate tag-update route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_update_5b6426.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-tag-update-5b6426"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_tag_storage_count_59674e": (0x59674e, "stored"),
    "audio_conversate_ui_list_count_5b0c18": (0x5b0c18, "shown"),
    "audio_conversate_tag_get_by_index_5964e2": (0x5964e2, "tag"),
    "audio_conversate_tag_icon_get_5b0af6": (0x5b0af6, "icon"),
    "audio_conversate_prep_button_create_5b1150": (0x5b1150, "button"),
    "audio_uart_page_44daca": (0x44daca, "move"),
    "audio_conversate_tag_ai_cue_enabled_5967bc": (0x5967bc, "cue"),
    "audio_conversate_tag_scroll_update_5b63d4": (0x5b63d4, "scroll_update"),
    "audio_conversate_report_5b02e4": (0x5b02e4, "report"),
    "audio_conversate_ui_list_view_mode_set_5b0edc": (0x5b0edc, "view_mode"),
    "audio_conversate_ui_slot_fade_5b1072": (0x5b1072, "fade"),
    "audio_terminal_list_anim_new_start_58c622": (0x58c622, "fade_new"),
    "audio_terminal_list_anim_old_start_58c6c4": (0x58c6c4, "fade_old"),
    "audio_terminal_ui_scroll_to_view_44ea2e": (0x44ea2e, "scroll_view"),
    "audio_conversate_ui_main_page_refresh_5b13fe": (0x5b13fe, "refresh"),
    "audio_log_flags": (0x43d0ce, "flags"),
    "audio_log_extended": (0x43d574, "extended"),
    "compressed_log_output": (0x43ce9e, "compressed"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "tag-update.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b6426",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, stored, shown, tag_present, button_present, display,
            auto_pop, highlighted, single, cue, state_byte, flags):
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
        ui = 0x20071368
        cpu.mem_write(ui, bytes([state_byte]))
        for offset, value in ((0x64, 0x20082000), (0x80, 0x20083000), (0x84, 4)):
            cpu.mem_write(ui + offset, struct.pack("<I", value))
        for offset, value in ((0x8c, display), (0x8e, auto_pop),
                              (0x96, highlighted), (0x97, single)):
            cpu.mem_write(ui + offset, bytes([value]))
        cpu.mem_write(0x200e4000, bytes([2, 0, 0, 0]) +
                      struct.pack("<I", 0x200e4100))
        cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x5678)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: kind for address, kind in LOWERS.values()}
        events, done = [], [False]

        def cstr(address):
            out = bytearray()
            for i in range(180):
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
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if kind in ("stored", "shown", "cue", "tag"):
                events.append((kind,) if kind != "tag" else (kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  {"stored": stored, "shown": shown, "cue": cue,
                                   "tag": 0x200e4000 if tag_present else 0}[kind])
            elif kind == "icon":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x76a47c)
            elif kind == "button":
                events.append((kind, r0, r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20081000 if button_present else 0)
            elif kind == "view_mode":
                events.append((kind, r0, r1, cstr(r2)))
            elif kind == "scroll_update":
                events.append((kind, r0))
            elif kind in ("refresh", "flags"):
                events.append((kind,))
                if kind == "flags":
                    machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                events.append((kind, r0, cstr(r1), cstr(r2), cstr(r3), line, cstr(fmt)))
            elif kind == "compressed":
                events.append((kind, r0, cstr(r1), cstr(r2)))
            elif kind in ("move", "fade", "scroll_view"):
                events.append((kind, r0, r1))
            else:
                events.append((kind, r0, r1, r2))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b6426 if native else symbols["audio_conversate_ui_route_5b6426"]
        cpu.emu_start(entry | 1, 0, count=800)
        if not done[0]:
            raise RuntimeError("tag update did not return")
        return (events, cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(ui, 0x9c)))

    cases = [(stored, shown, tag_present, button_present, display,
              auto_pop, highlighted, single, cue, state_byte, flags)
             for stored, shown in ((0, 0), (1, 1), (1, 0), (3, 1))
             for tag_present, button_present in ((0, 1), (1, 0), (1, 1))
             for display, auto_pop, highlighted, single in
             ((0, 0, 0, 0), (1, 1, 1, 0), (1, 1, 0, 0),
              (1, 0, 0, 0), (1, 0, 1, 1), (1, 0, 1, 0))
             for cue, state_byte, flags in ((0, 0, 0), (1, 2, 2), (1, 2, 7))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"tag update mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TAG_UPDATE_5B6426_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b6426..0x5b660d",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Tag storage, image, LVGL, animation, report, view mode and logging calls are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
