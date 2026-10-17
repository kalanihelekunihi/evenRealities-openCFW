#!/usr/bin/env python3
"""Direct stock/C replay of prep-note scroll route with source-owned bounds."""
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
ROUTE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_scroll_route_5b6f8e.c"
BOUNDS = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_scroll_bounds_5b6a06.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-scroll-route-5b6f8e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_obj_height_43fdda": (0x101010, 0x43fdda, "height"),
    "audio_uart_lv_obj_y_44e498": (0x101020, 0x44e498, "current"),
    "audio_terminal_display_status_44ea04": (0x101030, 0x44ea04, "scroll"),
    "audio_log_flags": (0x101040, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101050, 0x43d574, "extended"),
    "compressed_log_output": (0x101060, 0x43ce9e, "compact"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    objs = [OUT / "route.o", OUT / "bounds.o"]
    for source, obj in zip((ROUTE, BOUNDS), objs):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                        "-fno-builtin", "-c", str(source), "-o", str(obj)], check=True)
    elf_path = OUT / "oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b6f8e",
                    "--defsym=audio_conversate_prep_note_ram_200d7630=0x200d7630",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    *map(str, objs), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, ready, note, height, count, current, requested, flags):
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
        cpu.mem_write(0x20071368 + 0x24, struct.pack("<I", note))
        cpu.mem_write(0x20071368 + 0x28, struct.pack("<I", ready))
        cpu.mem_write(0x200d7630 + 0x109a, struct.pack("<H", count))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x12345678)
        cpu.reg_write(A.UC_ARM_REG_R1, requested & 0xffffffff)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 170)).split(b"\0", 1)[0]

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
            if kind == "height":
                events.append((kind, r[0]))
                value = height & 0xffffffff
            elif kind == "current":
                events.append((kind, r[0]))
                value = current & 0xffffffff
            elif kind == "scroll":
                events.append((kind, r[0], r[1], r[2]))
                value = 0
            elif kind == "flags":
                events.append((kind,))
                value = flags
            elif kind == "extended":
                line, fmt = struct.unpack("<II", machine.mem_read(sp, 8))
                args = struct.unpack("<II", machine.mem_read(sp + 8, 8))[:1 if line == 0x11e else 2]
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, fmt), args))
                value = 0
            else:
                args = (r[3],) if r[0] == 0x08400000 else (
                    r[3], struct.unpack("<I", machine.mem_read(sp, 4))[0])
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]), args))
                value = 0
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b6f8e if native else symbols["audio_conversate_ui_route_5b6f8e"]
        cpu.emu_start(entry | 1, 0, count=350)
        if not done[0]:
            raise RuntimeError("prep scroll route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = [(ready, note, height, count, current, requested, flags)
             for ready in (0, 0x20006000)
             for note in (0, 0x20001000)
             for height in (0, 28, 100)
             for count in (0, 1, 10)
             for current in (-1, 0, 28)
             for requested in (-1, 0, 28)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"prep scroll route mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_SCROLL_ROUTE_5B6F8E_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b6f8e..0x5b705f",
              "sources": [str(path.relative_to(ROOT)) for path in (ROUTE, BOUNDS)],
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (ROUTE, BOUNDS)},
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL height, current position, animated scroll and log remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
