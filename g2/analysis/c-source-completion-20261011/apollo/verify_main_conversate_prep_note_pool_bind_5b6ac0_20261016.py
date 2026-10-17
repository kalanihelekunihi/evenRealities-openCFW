#!/usr/bin/env python3
"""Compare the prep-note label-pool binder against stock at lower-call boundaries."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_note_pool_5b6ac0.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-note-pool-5b6ac0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_prep_note_line_count_5b4770": (0x101010, 0x5b4770, "count"),
    "audio_conversate_prep_note_line_text_5b4776": (0x101020, 0x5b4776, "line"),
    "audio_uart_buffer_zero": (0x101030, 0x43c0e4, "zero"),
    "audio_uart_page_43f09a": (0x101040, 0x43f09a, "pos"),
    "audio_uart_page_49942e": (0x101050, 0x49942e, "text"),
    "audio_uart_page_43dfa4": (0x101060, 0x43dfa4, "clear"),
    "audio_uart_page_43ded4": (0x101070, 0x43ded4, "add"),
    "audio_conversate_prep_scroll_clamp_5b6a3a": (0x101080, 0x5b6a3a, "clamp"),
    "audio_conversate_prep_scroll_max_5b6a06": (0x101090, 0x5b6a06, "max"),
    "audio_uart_lv_obj_height_43fdda": (0x1010a0, 0x43fdda, "height"),
    "audio_uart_lv_obj_content_width_43fe16": (0x1010b0, 0x43fe16, "width"),
    "audio_uart_lv_obj_y_43fce0": (0x1010c0, 0x43fce0, "y"),
    "audio_uart_page_43f4c0": (0x1010d0, 0x43f4c0, "size"),
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
                    "audio_conversate_prep_note_pool_bind_5b6ac0",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, first, count, mask, mode="bind", page=0, note=0, thumb=0,
            current_first=0, view_height=100, maximum=460):
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
        cpu.mem_write(base, bytes(0xa0))
        for i in range(12):
            if mask & (1 << i):
                cpu.mem_write(base + 0x30 + 4 * i, struct.pack("<I", 0x20010000 + i * 0x100))
        if mode == "show":
            for offset, value in ((0x1c, 0x20004000), (0x24, note),
                                  (0x28, page), (0x2c, thumb)):
                cpu.mem_write(base + offset, struct.pack("<I", value))
            cpu.mem_write(base + 0x60, struct.pack("<H", current_first))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, first)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            value = 0
            if kind == "count":
                events.append((kind,))
                value = count
            elif kind == "clamp":
                events.append((kind, r[0]))
                value = min(max(r[0], 0), maximum)
            elif kind == "max":
                events.append((kind,))
                value = maximum
            elif kind == "height":
                events.append((kind, r[0]))
                value = view_height
            elif kind == "width":
                events.append((kind, r[0]))
                value = 0x220
            elif kind == "y":
                events.append((kind, r[0]))
                value = 12
            elif kind == "zero":
                events.append((kind, r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2] & 0xff]) * r[1])
            elif kind == "line":
                events.append((kind, r[0], r[2]))
                machine.mem_write(r[1], f"line{r[0]}".encode() + b"\0")
            elif kind == "text":
                text = bytes(machine.mem_read(r[1], 140)).split(b"\0", 1)[0]
                events.append((kind, r[0], text))
            elif kind in ("clear", "add"):
                events.append((kind, r[0], r[1]))
            else:
                events.append((kind, r[0], r[1], r[2]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ((0x5b6ac0 if mode == "bind" else 0x5b6b58) if native else
                 symbols["audio_conversate_prep_note_pool_bind_5b6ac0" if mode == "bind"
                         else "audio_conversate_prep_note_pool_show_5b6b58"])
        cpu.emu_start(entry | 1, 0, count=3000)
        if not done[0]:
            raise RuntimeError("pool binder did not return")
        return events, bytes(cpu.mem_read(base, 0x64))

    cases = [(first, count, mask)
             for first in (0, 1, 10, 0xffff, 0x10000)
             for count in (0, 1, 12, 20, 0xffff)
             for mask in (0, 1, 0x555, 0xfff)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"prep-note pool bind mismatch {case}: {stock} != {selected}")
    show_cases = [(scroll, count, page, note, thumb, previous, height, maximum)
                  for scroll in (0, 56, 280)
                  for count in (8, 13, 24)
                  for page, note, thumb in ((0, 0, 0), (0x20005000, 0, 0),
                                            (0x20005000, 0x20006000, 0),
                                            (0x20005000, 0x20006000, 0x20007000))
                  for previous in (0, 5)
                  for height, maximum in ((100, 460), (250, 0))]
    for scroll, count, page, note, thumb, previous, height, maximum in show_cases:
        kw = dict(mode="show", page=page, note=note, thumb=thumb,
                  current_first=previous, view_height=height, maximum=maximum)
        stock = run(True, scroll, count, 0x555, **kw)
        selected = run(False, scroll, count, 0x555, **kw)
        if stock != selected:
            raise RuntimeError(f"prep-note pool show mismatch "
                               f"{(scroll,count,page,note,thumb,previous,height,maximum)}: "
                               f"{stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_NOTE_POOL_5B6AC0_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + len(show_cases),
              "native_bodies": ["0x5b6ac0..0x5b6b57", "0x5b6b58..0x5b6c47"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Line text provider, scroll clamp, LVGL and geometry functions remain controlled lower boundaries.",
                         "Pool binding, scrollbar state and call ordering are compared directly."]}
    receipt = OUT / "bind-oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
