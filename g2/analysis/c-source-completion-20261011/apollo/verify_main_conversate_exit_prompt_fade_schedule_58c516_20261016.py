#!/usr/bin/env python3
"""Stock/C lower-boundary replay of fade scheduler 0x58c516."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_exit_prompt_fade_schedule_58c516.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-exit-prompt-fade-schedule-58c516"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "compressed_log_output": (0x101030, 0x43ce9e, "compact"),
    "audio_uart_lv_style_unlink_450500": (0x101040, 0x450500, "unlink"),
    "audio_uart_lv_anim_init_4503d6": (0x101050, 0x4503d6, "init"),
    "audio_uart_lv_anim_values_4506ce": (0x101060, 0x4506ce, "values"),
    "audio_uart_lv_anim_start_450408": (0x101070, 0x450408, "start"),
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
                    "audio_conversate_exit_prompt_fade_schedule_58c516",
                    "--defsym=audio_legal_regulatory_fade_callback_58c12c=0x58c12d",
                    "--defsym=audio_uart_lv_anim_path_450672=0x450673",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, obj_id, duration, delay, callback, flags):
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
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                              (obj_id, duration, delay, callback)):
            cpu.reg_write(reg, value)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, pointer):
            return bytes(machine.mem_read(pointer, 180)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in (A.UC_ARM_REG_R0,
                 A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, fmt = struct.unpack("<II", machine.mem_read(sp, 8))
                args = struct.unpack("<II", machine.mem_read(sp + 8, 8)) if line == 0xe2 else ()
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, fmt), args))
            elif kind == "compact":
                args = (r[3], struct.unpack("<I", machine.mem_read(sp, 4))[0]) if r[0] == 0x10800000 else ()
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]), args))
            elif kind == "unlink":
                events.append((kind, r[0], r[1]))
            elif kind == "init":
                events.append((kind,))
                machine.mem_write(r[0], bytes(96))
                for off, val in ((0x30, 500), (0x2c, 100), (0x44, 1), (0x20, 0x450635)):
                    machine.mem_write(r[0] + off, struct.pack("<I", val))
                machine.mem_write(r[0] + 0x5c, b"\x10")
            elif kind == "values":
                events.append((kind, r[1], r[2]))
                for off, val in ((0x24, r[1]), (0x28, 0x80000000), (0x2c, r[2])):
                    machine.mem_write(r[0] + off, struct.pack("<I", val))
            else:
                words = list(struct.unpack("<24I", machine.mem_read(r[0], 96)))
                events.append((kind, words))
            machine.reg_write(A.UC_ARM_REG_R0, 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x58c516 if native else symbols["audio_conversate_exit_prompt_fade_schedule_58c516"]
        cpu.emu_start(entry | 1, 0, count=600)
        if not done[0]:
            raise RuntimeError("fade scheduler did not return")
        return events

    cases = [(obj, duration, delay, cb, flags)
             for obj in (0, 0x20001000)
             for duration in (0, 1, 250, 0xffffffff)
             for delay in (0, 1, 1000, 0xffffffff)
             for cb in (0, 0x1010a1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"fade scheduler mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_EXIT_PROMPT_FADE_SCHEDULE_58C516_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x58c516..0x58c621",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL and log calls remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
