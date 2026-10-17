#!/usr/bin/env python3
"""Stock/C lower-call replay for LVGL async post and timer repeat setter."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_async_post_484014.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-lv-async-post-484014"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_malloc": (0x101010, 0x44f718, "malloc"),
    "audio_uart_lv_heap_free": (0x101020, 0x44f758, "free"),
    "audio_uart_lv_timer_create_464466": (0x101030, 0x464466, "create"),
    "audio_uart_lvgl_log": (0x101040, 0x44d25c, "log"),
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
                    "audio_uart_lv_async_post_484014",
                    "--defsym=audio_uart_lv_async_dispatch_4840ac=0x4840ad",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, entry_kind, alloc_ok, timer_ok, callback, user, repeat):
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
        cpu.mem_write(0x20001000, bytes([0x5a]) * 8)
        cpu.mem_write(0x20002000, bytes([0x6b]) * 0x20)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, callback if entry_kind == "post" else 0x20002000)
        cpu.reg_write(A.UC_ARM_REG_R1, user if entry_kind == "post" else repeat)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}
        if native:
            names[0x4645ac] = "repeat"

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 180)).split(b"\0", 1)[0]

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
            if kind == "malloc":
                events.append((kind, r[0]))
                value = 0x20001000 if alloc_ok else 0
            elif kind == "free":
                events.append((kind, r[0]))
                value = 0
            elif kind == "create":
                events.append((kind, r[0], r[1], r[2]))
                value = 0x20002000 if timer_ok else 0
            elif kind == "repeat":
                machine.mem_write(r[0] + 0x10, struct.pack("<I", r[1]))
                value = 0
            else:
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                fmt, expr, reason = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append((kind, r[0], cstr(machine, r[1]), r[2],
                               cstr(machine, r[3]), cstr(machine, fmt),
                               cstr(machine, expr), cstr(machine, reason)))
                done[0] = True
                machine.emu_stop()
                return
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ((0x484014 if entry_kind == "post" else 0x4645ac) if native else
                 symbols["audio_uart_lv_async_post_484014" if entry_kind == "post"
                         else "audio_uart_lv_timer_repeat_count_4645ac"])
        cpu.emu_start(entry | 1, 0, count=220)
        if not done[0]:
            raise RuntimeError("LVGL async routine did not return")
        return (events, cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(0x20001000, 8)),
                bytes(cpu.mem_read(0x20002000 + 0x10, 4)))

    post_cases = [(alloc_ok, timer_ok, callback, user)
                  for alloc_ok in (False, True)
                  for timer_ok in (False, True)
                  for callback in (0x44df21, 0x1010a1)
                  for user in (0, 0x20003000)]
    for alloc_ok, timer_ok, callback, user in post_cases:
        args = ("post", alloc_ok, timer_ok, callback, user, 1)
        stock, selected = run(True, *args), run(False, *args)
        if stock != selected:
            raise RuntimeError(f"LVGL async post mismatch {args}: {stock} != {selected}")
    setter_cases = [(0x20002000, count) for count in (0, 1, 0xffffffff)]
    for pointer, count in setter_cases:
        # The timer setter is reached directly with a non-null timer here.
        args = ("setter", True, True, pointer, 0, count)
        stock, selected = run(True, *args), run(False, *args)
        if (stock[0], stock[2:]) != (selected[0], selected[2:]):
            raise RuntimeError(f"LVGL repeat setter mismatch {args}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_LV_ASYNC_POST_484014_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(post_cases) + len(setter_cases),
              "native_bodies": ["0x484014..0x484051", "0x4645ac..0x4645d7"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Allocator, timer creation and free remain controlled lower boundaries.",
                         "Timer setter null fatal loop is not replayed."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
