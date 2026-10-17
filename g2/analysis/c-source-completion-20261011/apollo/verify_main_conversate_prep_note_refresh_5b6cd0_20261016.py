#!/usr/bin/env python3
"""Stock/C lower-call replay for prep-note virtual row refresh."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_refresh_5b6cd0.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-refresh-5b6cd0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
    "audio_terminal_display_status_44ea04": (0x101020, 0x44ea04, "scroll"),
    "audio_uart_page_44d878": (0x101030, 0x44d878, "clean"),
    "audio_uart_page_43ded4": (0x101040, 0x43ded4, "addflag"),
    "audio_conversate_prep_note_finish_5b476a": (0x101050, 0x5b476a, "ready"),
    "audio_conversate_prep_note_line_count_5b4770": (0x101060, 0x5b4770, "count"),
    "audio_log_flags": (0x101070, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101080, 0x43d574, "extended"),
    "compressed_log_output": (0x101090, 0x43ce9e, "compact"),
    "audio_uart_page_43de82": (0x1010a0, 0x43de82, "create"),
    "audio_uart_page_43f4c0": (0x1010b0, 0x43f4c0, "size"),
    "audio_uart_page_43f09a": (0x1010c0, 0x43f09a, "position"),
    "audio_uart_page_44129e": (0x1010d0, 0x44129e, "style29e"),
    "audio_uart_page_44131c": (0x1010e0, 0x44131c, "style31c"),
    "audio_uart_page_44146a": (0x1010f0, 0x44146a, "style46a"),
    "audio_uart_page_43dfa4": (0x101100, 0x43dfa4, "clearflag"),
    "audio_uart_page_499416": (0x101110, 0x499416, "label"),
    "audio_uart_page_44144c": (0x101120, 0x44144c, "spacing"),
    "audio_uart_page_layout_499678": (0x101130, 0x499678, "mode"),
    "audio_uart_page_44104c": (0x101140, 0x44104c, "color"),
    "audio_uart_page_44140e": (0x101150, 0x44140e, "textcolor"),
    "audio_uart_page_44143e": (0x101160, 0x44143e, "font"),
    "audio_uart_page_44145a": (0x101170, 0x44145a, "alpha"),
    "audio_uart_page_44122a": (0x101180, 0x44122a, "style22a"),
    "audio_uart_page_441238": (0x101190, 0x441238, "style238"),
    "audio_uart_page_44120e": (0x1011a0, 0x44120e, "style20e"),
    "audio_uart_page_44121c": (0x1011b0, 0x44121c, "style21c"),
    "audio_conversate_prep_note_pool_bind_5b6ac0": (0x1011c0, 0x5b6ac0, "bind"),
    "audio_uart_page_43f66c": (0x1011d0, 0x43f66c, "update"),
    "audio_conversate_prep_note_pool_show_5b6b58": (0x1011e0, 0x5b6b58, "show"),
    "audio_uart_page_58c238": (0x1011f0, 0x58c238, "fade"),
    "audio_uart_lv_obj_has_flag_43e0e0": (0x101200, 0x43e0e0, "hasflag"),
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
                    "audio_conversate_prep_note_refresh_5b6cd0",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    "--defsym=audio_uart_ring_primary_head_cell=0x200746dc",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, note, expanded, ready, count, animate, hasflag, flags):
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
        cpu.mem_write(base, bytes([0x5a]) * 0xa0)
        cpu.mem_write(base + 0x24, struct.pack("<I", note))
        cpu.mem_write(base + 0x2c, struct.pack("<I", expanded))
        cpu.mem_write(0x200746dc, struct.pack("<I", 0x20007000))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, animate)
        events, done, label_counter = [], [False], [0]
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
            value = 0
            if kind == "zero":
                events.append((kind, r[0] - base, r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2] & 0xff]) * r[1])
            elif kind in ("ready", "count", "flags"):
                events.append((kind,))
                value = {"ready": ready, "count": count, "flags": flags}[kind]
            elif kind == "extended":
                line, fmt = struct.unpack("<II", machine.mem_read(sp, 8))
                argc = 3 if line == 0x10d else 0
                args = struct.unpack("<" + "I" * argc, machine.mem_read(sp + 8, argc * 4)) if argc else ()
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, fmt), args))
            elif kind == "compact":
                argc = 3 if r[0] == 0x0cc00000 else 0
                args = (r[3], *struct.unpack("<II", machine.mem_read(sp, 8))) if argc else ()
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]), args))
            elif kind == "create":
                events.append((kind, r[0]))
                value = 0x20010000
            elif kind == "label":
                events.append((kind, r[0]))
                value = 0x20011000 + label_counter[0] * 0x100
                label_counter[0] += 1
            elif kind == "color":
                events.append((kind, r[0]))
                value = 0xabcdef
            elif kind == "hasflag":
                events.append((kind, r[0], r[1]))
                value = hasflag
            elif kind in ("clean", "bind", "update", "show"):
                events.append((kind, r[0]))
            elif kind in ("addflag", "clearflag", "mode"):
                events.append((kind, r[0], r[1]))
            else:
                events.append((kind, r[0], r[1], r[2]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b6cd0 if native else symbols["audio_conversate_prep_note_refresh_5b6cd0"]
        cpu.emu_start(entry | 1, 0, count=3000)
        if not done[0]:
            raise RuntimeError("prep-note refresh did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(base, 0xa0))

    cases = [(note, expanded, ready, count, animate, hasflag, flags)
             for note in (0, 0x20001000)
             for expanded in (0, 0x20002000)
             for ready in (0, 1)
             for count in (0, 1, 20)
             for animate in (0, 1)
             for hasflag in (0, 1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"prep-note refresh mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_REFRESH_5B6CD0_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_bodies": ["0x5b6cd0..0x5b6f8d", "0x5b69d4..0x5b6a05"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL and prep-note pool helpers remain controlled lower boundaries.",
                         "The twelve-label construction and RAM updates are compared directly."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
