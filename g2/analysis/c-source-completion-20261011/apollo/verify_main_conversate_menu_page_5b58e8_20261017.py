#!/usr/bin/env python3
"""Direct stock/C route comparison for Conversate display menu page."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_menu_page_5b58e8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-menu-page-5b58e8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_ux_get_system_ble_status": (0x47d8ce, "ble"),
    "audio_log_flags": (0x43d0ce, "flags"),
    "audio_log_extended": (0x43d574, "extended"),
    "compressed_log_output": (0x43ce9e, "compressed"),
    "audio_uart_page_460084": (0x460084, "locale_index"),
    "audio_uart_page_45fffe": (0x45fffe, "locale_text"),
    "audio_conversate_ui_message_send_58bfb2": (0x58bfb2, "message"),
    "audio_uart_page_43de82": (0x43de82, "root"),
    "audio_uart_page_43f4c0": (0x43f4c0, "size"),
    "audio_uart_page_43f09a": (0x43f09a, "position"),
    "audio_uart_page_44129e": (0x44129e, "style_a"),
    "audio_uart_page_44131c": (0x44131c, "style_b"),
    "audio_uart_page_44146a": (0x44146a, "style_c"),
    "audio_conversate_menu_style_5b5720": (0x5b5720, "menu_style"),
    "audio_uart_page_43dfa4": (0x43dfa4, "root_flag"),
    "audio_conversate_menu_request_prep_notes_5b1e52": (0x5b1e52, "prep_request"),
}
DATA = {"audio_conversate_ui_settings_extension_20071369": 0x20071369,
        "audio_conversate_ui_app_id_200743a0": 0x200743a0}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "menu-page.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b58e8",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    *[f"--defsym={name}=0x{address:x}" for name, address in DATA.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, ble, flags, app_id):
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
        cpu.mem_write(0x200743a0, struct.pack("<I", app_id))
        cpu.mem_write(0x20090000, b"localized disconnect\0")
        cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x5678)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: kind for address, kind in LOWERS.values()}
        events, done = [], [False]

        def cstr(address):
            out = bytearray()
            for i in range(160):
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
            if kind in ("ble", "flags", "prep_request"):
                events.append((kind,))
                if kind == "ble":
                    machine.reg_write(A.UC_ARM_REG_R0, ble)
                elif kind == "flags":
                    machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                events.append((kind, r0, cstr(r1), cstr(r2), cstr(r3), line, cstr(fmt)))
            elif kind == "compressed":
                events.append((kind, r0, cstr(r1), cstr(r2)))
            elif kind == "locale_index":
                events.append((kind, cstr(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, 9)
            elif kind == "locale_text":
                events.append((kind, cstr(r0), r1))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20090000)
            elif kind == "message":
                fifth = struct.unpack("<I", machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 4))[0]
                events.append((kind, r0, cstr(r1), r2, r3, fifth))
            elif kind == "root":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20081000)
            elif kind == "root_flag":
                events.append((kind, r0, r1))
            else:
                events.append((kind, r0, r1, r2))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b58e8 if native else symbols["audio_conversate_ui_route_5b58e8"]
        cpu.emu_start(entry | 1, 0, count=500)
        if not done[0]:
            raise RuntimeError("menu page did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), cpu.mem_read(0x20071368, 12)

    cases = [(ble, flags, app) for ble in (0, 1) for flags in (0, 1, 2, 4, 7)
             for app in (0, 0x12, 0xffffffff)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"menu page mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MENU_PAGE_5B58E8_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b58e8..0x5b59f9",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["BLE status, LVGL, locale, message sender, prep-note sender and logs are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
