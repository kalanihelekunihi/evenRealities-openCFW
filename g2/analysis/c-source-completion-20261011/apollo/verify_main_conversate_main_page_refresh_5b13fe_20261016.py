#!/usr/bin/env python3
"""Stock/C lower-call replay for Conversate list count and oldest-tag deletion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_main_page_refresh_5b13fe.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-main-page-refresh-5b13fe"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_child_count_44ddea": (0x101010, 0x44ddea, "count"),
    "audio_terminal_ui_object_valid_43e2ea": (0x101020, 0x43e2ea, "valid"),
    "audio_lv_child_44dce2": (0x101030, 0x44dce2, "child"),
    "audio_uart_page_delete_event_filter_44d7b8": (0x101040, 0x44d7b8, "delete"),
    "audio_log_flags": (0x101050, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101060, 0x43d574, "extended"),
    "compressed_log_output": (0x101070, 0x43ce9e, "compact"),
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
                    "audio_conversate_ui_main_page_refresh_5b13fe",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, list_object, list_count, list_valid, selected_mode, child_valid, flags,
            entry_kind="refresh"):
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
        cpu.mem_write(base + 0x96, bytes([selected_mode]))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 200)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                  A.UC_ARM_REG_R3)]
            value = 0
            if kind == "count":
                events.append((kind, r[0]))
                value = list_count
            elif kind == "valid":
                events.append((kind, r[0]))
                value = list_valid if r[0] == list_object else child_valid
            elif kind == "child":
                events.append((kind, r[0], r[1]))
                value = 0x20010000 + r[1] * 0x100
            elif kind == "delete":
                events.append((kind, r[0]))
            elif kind == "flags":
                events.append((kind,))
                value = flags
            elif kind == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, message = struct.unpack("<II", machine.mem_read(sp, 8))
                arg = struct.unpack("<I", machine.mem_read(sp + 8, 4))[0] if line == 0x18b else None
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, message), arg))
            else:
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               r[3] if r[0] == 0x10400000 else None))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ((0x5b0c18 if entry_kind == "count" else 0x5b13fe) if native else
                 symbols["audio_conversate_ui_list_count_5b0c18" if entry_kind == "count"
                         else "audio_conversate_ui_main_page_refresh_5b13fe"])
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]:
            raise RuntimeError("Conversate main-page refresh did not return")
        return (events, (cpu.reg_read(A.UC_ARM_REG_R0) if entry_kind == "count" else None),
                bytes(cpu.mem_read(base, 0xb0)))

    cases = [(list_object, count, valid, mode, child_valid, flags)
             for list_object in (0, 0x20003000)
             for count in (0, 20, 21, 23)
             for valid in (0, 1)
             for mode in (0, 1)
             for child_valid in (0, 1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"main-page refresh mismatch {case}: {stock} != {selected}")
    for list_object in (0, 0x20003000):
        for count in (0, 1, 20, 23):
            case = (list_object, count, 1, 0, 1, 0)
            if run(True, *case, entry_kind="count") != run(False, *case, entry_kind="count"):
                raise RuntimeError(f"list-count mismatch {case}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MAIN_PAGE_REFRESH_5B13FE_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + 8,
              "native_bodies": ["0x5b0c18..0x5b0c2f", "0x5b13fe..0x5b14cd"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL count, object validity, child lookup, deletion and log transport remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
