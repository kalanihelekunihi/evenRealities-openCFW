#!/usr/bin/env python3
"""Compare selector rebuild C call sequence and state writes with stock Apollo."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_session_list_rebuild_5ecef6.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-session-list-rebuild-5ecef6"
CALLS = {
    "audio_td_active_session": (0x59732a, 0),
    "audio_terminal_session_count_5eca48": (0x5eca48, 0),
    "audio_terminal_ui_stop_service_a_5eceb2": (0x5eceb2, 0),
    "audio_uart_page_43de82": (0x43de82, 1),
    "audio_uart_page_43f4c0": (0x43f4c0, 3),
    "audio_uart_page_43f09a": (0x43f09a, 3),
    "audio_uart_page_43dfa4": (0x43dfa4, 2),
    "audio_uart_page_44104c": (0x44104c, 1),
    "audio_uart_page_44127e": (0x44127e, 3),
    "audio_uart_page_44129e": (0x44129e, 3),
    "audio_uart_page_44131c": (0x44131c, 3),
    "audio_terminal_session_four_margins_5eca00": (0x5eca00, 3),
    "audio_uart_page_44146a": (0x44146a, 3),
    "audio_uart_page_48ba78": (0x48ba78, 2),
    "audio_uart_page_48ba92": (0x48ba92, 4),
    "audio_uart_page_441246": (0x441246, 3),
    "audio_uart_page_43ded4": (0x43ded4, 2),
    "audio_uart_page_44e368": (0x44e368, 2),
    "audio_terminal_session_row_factory_5ecd06": (0x5ecd06, 4),
    "audio_terminal_session_row_text_5ecc74": (0x5ecc74, 3),
    "audio_terminal_session_valid_5eca64": (0x5eca64, 1),
    "audio_td_current_session_index_signed": (0x5ecaac, 0),
    "audio_terminal_session_apply_5ecb88": (0x5ecb88, 1),
    "audio_terminal_ui_scroll_to_view_44ea2e": (0x44ea2e, 2),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "rebuild-oracle.o"
    elf = OUT / "rebuild-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, (address, _) in CALLS.items()}
    defs.update(audio_terminal_ui_state_base=0x2006e0d0,
                audio_terminal_display_queue_handle=0x20074a90)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_terminal_session_list_rebuild_5ecef6")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, count, requested, valid, current):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, requested & 0xffffffff)
        u.mem_write(0x20074a90, (0x20091000).to_bytes(4, "little"))
        u.mem_write(0x2006e0d0, bytes(0x2a0))
        u.mem_write(0x20080000, bytes(0x400))
        for i in range(count):
            u.mem_write(0x20080000 + 0x122 + i * 0x90, bytes((i + 1,)))
        trace = []
        created = 0

        def hook(cpu, pc, size, _):
            nonlocal created
            if pc not in by_address:
                return
            name, argc = by_address[pc]
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            args = tuple(cpu.reg_read(r) for r in regs[:argc])
            if name == "audio_terminal_session_row_factory_5ecd06":
                raw = bytes(cpu.mem_read(args[1], 64)).split(b"\0", 1)[0]
                args = (args[0], raw, args[2], args[3])
            elif name == "audio_terminal_session_row_text_5ecc74":
                cpu.mem_write(args[0], f"Row {len([t for t in trace if t[0] == name])}".encode() + b"\0")
                args = ("stack buffer", args[1], args[2])
            trace.append((name, args))
            result = 0
            if name == "audio_td_active_session":
                result = 0x20080000
            elif name == "audio_terminal_session_count_5eca48":
                result = count
            elif name in ("audio_uart_page_43de82", "audio_terminal_session_row_factory_5ecd06"):
                created += 1
                result = 0x20092000 + created * 0x100
            elif name == "audio_uart_page_44104c":
                result = 0x12345678
            elif name == "audio_terminal_session_valid_5eca64":
                result = valid
            elif name == "audio_td_current_session_index_signed":
                result = current & 0xffffffff
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5ecef6) | 1,
                    0x600000, count=2500)
        state = bytes(u.mem_read(0x2006e0d0 + 0x240, 0x38))
        return trace, state

    cases = 0
    for count, requested, valid, current in itertools.product(
            (0, 1, 2), (-2, -1, 0, 1, 3), (0, 1), (-1, 0)):
        args = (count, requested, valid, current)
        stock = run(False, *args)
        candidate = run(True, *args)
        if stock != candidate:
            for n, (a, b) in enumerate(itertools.zip_longest(stock[0], candidate[0])):
                if a != b:
                    print("first call mismatch", args, n, a, b)
                    break
            if stock[1] != candidate[1]:
                print("state mismatch", args, stock[1].hex(), candidate[1].hex())
            raise RuntimeError("selector rebuild mismatch")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_REBUILD_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf),
               "cases": cases,
               "scope": "Selector root/list/row construction call order, state pointers, and selected-row handling",
               "limits": ["Lower LVGL effects, row factory and row text are mocked; full image and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()
