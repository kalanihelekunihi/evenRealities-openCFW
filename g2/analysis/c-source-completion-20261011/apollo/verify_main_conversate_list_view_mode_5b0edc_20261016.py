#!/usr/bin/env python3
"""Stock/C replay for Conversate mode rank, immediate apply, and mode setter."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_list_view_mode_5b0edc.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-list-view-mode-5b0edc"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_terminal_ui_object_valid_43e2ea": (0x101010, 0x43e2ea, "valid"),
    "audio_conversate_list_slot_alpha_5b0c72": (0x101020, 0x5b0c72, "alpha"),
    "audio_conversate_list_slot_fade_5b0ca0": (0x101030, 0x5b0ca0, "fade"),
    "audio_log_flags": (0x101040, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101050, 0x43d574, "extended"),
    "compressed_log_output": (0x101060, 0x43ce9e, "compact"),
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
                    "audio_conversate_ui_list_view_mode_set_5b0edc",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, kind, mode, old, animate, list_object, reason, valid, flags):
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
        base = 0x20071368
        cpu.mem_write(base, bytes(0xb0))
        cpu.mem_write(base + 0x64, struct.pack("<I", list_object))
        for i in range(4):
            cpu.mem_write(base + 0x6c + 4 * i, struct.pack("<I", 0x20010000 + i * 0x100))
        cpu.mem_write(base + 0x97, bytes([old]))
        cpu.mem_write(0x20006000, b"main unselected\0")
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, mode)
        cpu.reg_write(A.UC_ARM_REG_R1, animate if kind == "mode" else mode)
        cpu.reg_write(A.UC_ARM_REG_R2, reason)
        if kind == "apply":
            cpu.reg_write(A.UC_ARM_REG_R0, base)
            cpu.reg_write(A.UC_ARM_REG_R1, mode)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 180)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            lower = names.get(pc)
            if lower is None:
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                  A.UC_ARM_REG_R3)]
            value = 0
            if lower == "valid":
                events.append((lower, r[0]))
                value = valid
            elif lower == "alpha":
                events.append((lower, r[0], r[1]))
            elif lower == "fade":
                duration = struct.unpack("<I", machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 4))[0]
                events.append((lower, r[0], r[1], r[2], r[3], duration))
            elif lower == "flags":
                events.append((lower,))
                value = flags
            elif lower == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, message = struct.unpack("<II", machine.mem_read(sp, 8))
                arg = struct.unpack("<I", machine.mem_read(sp + 8, 4))[0]
                why = cstr(machine, struct.unpack("<I", machine.mem_read(sp + 12, 4))[0]) if line == 0x11b else None
                events.append((lower, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, message), arg, why))
            else:
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                why = cstr(machine, struct.unpack("<I", machine.mem_read(sp, 4))[0]) if r[0] == 0x0c800000 else None
                events.append((lower, r[0], cstr(machine, r[1]), cstr(machine, r[2]), r[3], why))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ({"rank": 0x5b0c30, "apply": 0x5b0d24, "mode": 0x5b0edc}[kind]
                 if native else symbols[{"rank": "audio_conversate_list_view_mode_rank_5b0c30",
                                         "apply": "audio_conversate_list_view_apply_5b0d24",
                                         "mode": "audio_conversate_ui_list_view_mode_set_5b0edc"}[kind]])
        cpu.emu_start(entry | 1, 0, count=2000)
        if not done[0]:
            raise RuntimeError("list-view routine did not return")
        return events, (cpu.reg_read(A.UC_ARM_REG_R0) if kind == "rank" else None), bytes(cpu.mem_read(base, 0xb0))

    cases = [(mode, old, animate, list_object, reason, valid, flags)
             for mode in (0, 1, 2, 3, 255, 0x100)
             for old in (0, 1, 2, 3)
             for animate in (0, 1)
             for list_object in (0, 0x20003000)
             for reason in (0, 0x20006000)
             for valid in (0, 1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, "mode", *case), run(False, "mode", *case)
        if stock != selected:
            raise RuntimeError(f"list-view mode mismatch {case}: {stock} != {selected}")
    extra = 0
    for mode in range(256):
        case = (mode, 0, 0, 0x20003000, 0, 1, 0)
        if run(True, "rank", *case) != run(False, "rank", *case):
            raise RuntimeError(f"list-view rank mismatch {mode}")
        extra += 1
    for mode in (0, 1, 2, 3, 255):
        for valid in (0, 1):
            case = (mode, 0, 0, 0x20003000, 0, valid, 0)
            if run(True, "apply", *case) != run(False, "apply", *case):
                raise RuntimeError(f"list-view apply mismatch {case}")
            extra += 1
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_LIST_VIEW_MODE_5B0EDC_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + extra,
              "native_bodies": ["0x5b0c30..0x5b0c51", "0x5b0d24..0x5b0d63", "0x5b0edc..0x5b1071"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL validity, alpha/fade helpers and log transport remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
