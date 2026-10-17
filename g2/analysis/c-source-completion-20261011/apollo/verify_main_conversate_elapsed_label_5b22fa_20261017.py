#!/usr/bin/env python3
"""Compare stock/C Conversate elapsed-time label branches and logging."""
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
SOURCES = [G2 / "components/audio/uart_thread_source_candidate" / name for name in
           ("conversate_elapsed_label_5b22fa.c",
            "time_epoch_to_calendar_449ed4_44a100.c",
            "time_epoch_to_calendar_449fda.c")]
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-elapsed-label-5b22fa"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_buffer_zero": (0x43c0e4, "zero"),
    "audio_ble_format_to_buffer": (0x4b4728, "format"),
    "audio_uart_page_49942e": (0x49942e, "label"),
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
    objects = []
    for index, source in enumerate(SOURCES):
        obj = OUT / f"elapsed-{index}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-O2", "-Wall", "-Wextra",
                        "-Werror", "-ffreestanding", "-fno-builtin", "-c",
                        str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    elf_path = OUT / "oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_route_scroll_5b22fa",
                    "--defsym=audio_uart_hand_record=0x200736d4",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    *map(str, objects), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, seconds, mode, flags):
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
        cpu.mem_write(0x200736d4 + 24, struct.pack("<I", mode))
        buffer = (0x20073cac if native else
                  symbols["audio_conversate_clock_label_buffer_20073cac"])
        cpu.mem_write(buffer, bytes([0xa5]) * 20)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x20001000)
        cpu.reg_write(A.UC_ARM_REG_R1, seconds)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def cstr(address):
            return bytes(cpu.mem_read(address, 150)).split(b"\0", 1)[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            name = kinds.get(pc)
            if name is None:
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if name == "zero":
                assert r0 == buffer and r1 == 20 and r2 == 0
                machine.mem_write(r0, bytes(r1))
                events.append((name, r1))
            elif name == "format":
                fmt = cstr(r1)
                text = (f"{r2:02d}:{r3:02d} {cstr(word(sp))}" if "%s" in fmt
                        else f"{r2:02d}:{r3:02d}")
                machine.mem_write(r0, text.encode() + b"\0")
                events.append((name, fmt, r2, r3, text))
                machine.reg_write(A.UC_ARM_REG_R0, len(text))
            elif name == "label":
                events.append((name, r0, cstr(r1)))
            elif name == "flags":
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif name == "extended":
                events.append((name, r0, cstr(r1), cstr(r2), cstr(r3),
                               word(sp), cstr(word(sp + 4)), cstr(word(sp + 8))))
            else:
                events.append((name, r0, cstr(r1), cstr(r2), cstr(r3)))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b22fa if native else symbols["audio_conversate_route_scroll_5b22fa"]
        cpu.emu_start(entry | 1, 0, count=15000)
        if not done[0]:
            raise RuntimeError(f"elapsed label did not return: {native} {seconds} {mode} {flags}")
        return bytes(cpu.mem_read(buffer, 20)), events

    cases = [(seconds, mode, flags)
             for seconds in (0, 946684799, 946684800, 946728000,
                             946771199, 946771200, 1700000000, 4294967295)
             for mode in (0, 1, 2) for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"elapsed label mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_ELAPSED_LABEL_5B22FA_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b22fa..0x5b23ad",
              "sources": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                          for path in SOURCES],
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Formatter, buffer-zero, label update and logging are controlled lower boundaries; exact RAM placement remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
