#!/usr/bin/env python3
"""Direct stock/C comparison for Conversate display-config route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_display_config_5b3398.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-ui-display-config-5b3398"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_ui_child_style_clear_5b3340": (0x101010, 0x5b3340, "clear"),
    "audio_lv_delete_44d7b8": (0x101020, 0x44d7b8, "delete"),
    "audio_uart_page_43dfa4": (0x101030, 0x43dfa4, "show"),
    "audio_uart_page_43ded4": (0x101040, 0x43ded4, "hide"),
    "audio_uart_display_audio_reset_441488": (0x101050, 0x441488, "opacity"),
    "audio_lv_child_count_44ddea": (0x101060, 0x44ddea, "count"),
    "audio_lv_child_44dce2": (0x101070, 0x44dce2, "child"),
    "audio_conversate_ui_slot_fade_5b1072": (0x101080, 0x5b1072, "fade"),
    "audio_conversate_ui_list_view_mode_set_5b0edc": (0x101090, 0x5b0edc, "mode"),
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
                    "audio_conversate_ui_route_5b3398",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    "--defsym=audio_conversate_ui_app_id_200743a0=0x200743a0",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, state, visible_menu, visible_secondary, child_count,
            child_mask, old, footer):
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
        for offset, value in ((4, 0x20002000), (8, 0x20003000),
                              (0x1c, old), (0x20, 0x20004000),
                              (0x64, 0x20005000), (0x7c, footer),
                              (0x80, 0x20008000), (0x84, 7)):
            cpu.mem_write(root+offset, struct.pack("<I", value))
        cpu.mem_write(root+0x8c, bytes((visible_menu, visible_secondary)))
        cpu.mem_write(root+0x96, b"\x01")
        cpu.mem_write(0x200743a0, struct.pack("<I", 0x20001000))
        cpu.reg_write(A.UC_ARM_REG_R0, state)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x77)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(address):
            result = bytearray()
            for i in range(80):
                value = cpu.mem_read(address+i, 1)[0]
                if value == 0:
                    return result.decode("utf-8", "replace")
                result.append(value)
            raise RuntimeError("unterminated route reason")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            r1 = machine.reg_read(A.UC_ARM_REG_R1)
            r2 = machine.reg_read(A.UC_ARM_REG_R2)
            if kind == "mode":
                events.append((kind, r0, r1, cstr(r2)))
            elif kind == "child":
                events.append((kind, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0x20006000+r1*0x100 if child_mask & (1 << r1) else 0)
            elif kind == "count":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, child_count)
            elif kind in ("show", "hide", "fade"):
                events.append((kind, r0, r1))
            elif kind == "opacity":
                events.append((kind, r0, r1, r2))
            else:
                events.append((kind, r0))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b3398 if native else symbols["audio_conversate_ui_route_5b3398"]
        cpu.emu_start(entry | 1, 0, count=1200)
        if not done[0]:
            raise RuntimeError("display-config route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(root, 0x98))

    cases = [(state, first, second, count, mask, old, footer)
             for state in (0, 4, 5, 255)
             for first, second in ((0, 0), (1, 0), (0, 1), (1, 1))
             for count, mask in ((0, 0), (1, 1), (2, 1), (2, 2), (2, 3))
             for old, footer in ((0, 0), (0x20007000, 0x20009000))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"display-config mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_CONFIG_5B3398_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b3398..0x5b349b",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Nine called helpers are controlled lower boundaries; final image placement remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
