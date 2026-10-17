#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate slot opacity and fade scheduler."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_list_slot_alpha_fade_5b0c72.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-list-slot-alpha-fade-5b0c72"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_terminal_ui_object_valid_43e2ea": (0x101010, 0x43e2ea, "valid"),
    "audio_uart_lv_style_unlink_450500": (0x101020, 0x450500, "unlink"),
    "audio_lv_style_opa_441488": (0x101030, 0x441488, "opacity"),
    "audio_uart_lv_anim_init_4503d6": (0x101040, 0x4503d6, "init"),
    "audio_uart_lv_anim_values_4506ce": (0x101050, 0x4506ce, "values"),
    "audio_uart_lv_anim_start_450408": (0x101060, 0x450408, "start"),
    "audio_uart_lv_anim_path_450688": (0x101080, 0x450688, "path"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_list_slot_fade_5b0ca0",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, kind, object_, first, last, delay, duration, valid):
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
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, object_)
        cpu.reg_write(A.UC_ARM_REG_R1, first)
        cpu.reg_write(A.UC_ARM_REG_R2, last)
        cpu.reg_write(A.UC_ARM_REG_R3, delay)
        cpu.mem_write(0x200ff000, struct.pack("<I", duration))
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}
        callback = 0x5b0c4f if native else symbols["audio_conversate_list_slot_opacity_callback_5b0c4e"] | 1
        path = 0x450689 if native else 0x101081

        def normalize(value):
            if value == callback:
                return "callback"
            if value == path:
                return "path"
            return value

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            lower = names.get(pc)
            if lower is None or lower == "path":
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            value = 0
            if lower == "valid":
                events.append((lower, r[0]))
                value = valid
            elif lower == "unlink":
                events.append((lower, r[0], normalize(r[1])))
            elif lower == "opacity":
                events.append((lower, r[0], r[1], r[2]))
            elif lower == "init":
                events.append((lower,))
                machine.mem_write(r[0], bytes(0x60))
            elif lower == "values":
                events.append((lower, r[1], r[2]))
            else:
                words = struct.unpack("<14I", machine.mem_read(r[0], 56))
                events.append((lower, words[0], normalize(words[1]),
                               normalize(words[8]), words[12], words[13]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ({"callback": 0x5b0c4e, "alpha": 0x5b0c72, "fade": 0x5b0ca0}[kind]
                 if native else symbols[{"callback": "audio_conversate_list_slot_opacity_callback_5b0c4e",
                                         "alpha": "audio_conversate_list_slot_alpha_5b0c72",
                                         "fade": "audio_conversate_list_slot_fade_5b0ca0"}[kind]])
        cpu.emu_start(entry | 1, 0, count=500)
        if not done[0]:
            raise RuntimeError("slot alpha/fade did not return")
        return events

    cases = [(kind, object_, first, last, delay, duration, valid)
             for kind in ("callback", "alpha", "fade")
             for object_ in (0, 0x20010000)
             for first in (0, 127, 255, 0x100)
             for last in (0, 255, 0x100)
             for delay in (0, 50)
             for duration in (0, 300)
             for valid in (0, 1)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"slot alpha/fade mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_LIST_SLOT_ALPHA_FADE_5B0C72_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_bodies": ["0x5b0c4e..0x5b0c71", "0x5b0c72..0x5b0c9f",
                                "0x5b0ca0..0x5b0d23"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL validity, style and animation APIs remain controlled lower boundaries.",
                         "Animation descriptor callback, path, duration and negative delay are compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
