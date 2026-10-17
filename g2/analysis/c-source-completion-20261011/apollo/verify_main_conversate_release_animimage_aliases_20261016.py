#!/usr/bin/env python3
"""Replay Conversate aliases with the already verified source-owned animimage body."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
PROVIDER = G2 / "components/audio/uart_thread_source_candidate/display_lv_animimage_597ea6.c"
ROWS = [
    ("cleanup", 0x597ee0, "audio_conversate_route_cleanup_597ee0",
     G2 / "components/audio/uart_thread_source_candidate/conversate_route_cleanup_597ee0.c",
     G2 / "build/c-firmware/20261016/main-conversate-route-cleanup-597ee0",
     "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_CLEANUP_597EE0_C", 20),
    ("property", 0x597f52, "audio_conversate_route_set_property_597f52",
     G2 / "components/audio/uart_thread_source_candidate/conversate_route_set_property_597f52.c",
     G2 / "build/c-firmware/20261016/main-conversate-route-set-property-597f52",
     "PASS_DIRECT_MAIN_CONVERSATE_ROUTE_SET_PROPERTY_597F52_C", 12),
]
LOWERS = {"audio_uart_lvgl_log": (0x101010, 0x44d25c, "log"),
          "audio_uart_lv_anim_values_4506ce": (0x101020, 0x4506ce, "values"),
          "audio_uart_lv_anim_start_450408": (0x101030, 0x450408, "start")}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    out = G2 / "build/c-firmware/20261016/main-conversate-release-animimage-aliases"
    out.mkdir(parents=True, exist_ok=True)
    objects = []
    for index, source in enumerate([PROVIDER, *(r[3] for r in ROWS)]):
        obj = out / f"source-{index}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    elf_path = out / "oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    *(str(p) for p in objects), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, row, handle, value):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        cpu.mem_map(0x20000000, 0x100000)
        if handle:
            cpu.mem_write(handle, bytes((i * 11 + 27) & 255 for i in range(0xd0)))
        events = []
        lower_names = {r[1 if native else 0]: r[2] for r in LOWERS.values()}

        def cstr(machine, pointer):
            return bytes(machine.mem_read(pointer, 180)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            kind = lower_names.get(pc)
            if kind is None:
                return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            if kind == "log":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                tail = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append((kind, r0, cstr(machine, machine.reg_read(A.UC_ARM_REG_R1)),
                               machine.reg_read(A.UC_ARM_REG_R2),
                               cstr(machine, machine.reg_read(A.UC_ARM_REG_R3)),
                               *(cstr(machine, p) for p in tail)))
            elif kind == "start":
                events.append((kind, r0))
            else:
                events.append((kind, r0, machine.reg_read(A.UC_ARM_REG_R1)))
            machine.reg_write(A.UC_ARM_REG_R0, 0x12345678)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        def fault(_machine, _access, address, size, written, _user):
            events.append(("fault_write", address, size, written))
            return False

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED, fault)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, handle)
        cpu.reg_write(A.UC_ARM_REG_R1, value)
        entry = row[1] if native else symbols[row[2]]
        try:
            cpu.emu_start(entry | 1, 0x101f00, count=250)
        except UcError:
            if not events or events[-1][0] != "fault_write":
                raise
        return events, bytes(cpu.mem_read(handle, 0xd0)) if handle else b""

    for row in ROWS:
        kind, _address, _symbol, source, folder, status, count = row
        handles = (0, 0x20001000, 0x20002000, 0x20003000, 0x20004000) if kind == "cleanup" else (0, 0x20001000, 0x20002000)
        cases = [(h, v) for h in handles for v in (0, 1, 0x12345678, 0xffffffff)]
        assert len(cases) == count
        for case in cases:
            stock, selected = run(True, row, *case), run(False, row, *case)
            if stock != selected:
                raise RuntimeError(f"{kind} mismatch {case}: {stock} != {selected}")
        record = {"status": status, "stock_payload_sha256": PAYLOAD_SHA,
                  "cases": count, "native_body":
                      "0x597ee0..0x597f0f" if kind == "cleanup" else "0x597f52..0x597f81",
                  "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                  "provider_source": str(PROVIDER.relative_to(ROOT)),
                  "provider_source_sha256": sha(PROVIDER),
                  "oracle_elf": str(elf_path.relative_to(ROOT)),
                  "oracle_elf_sha256": sha(elf_path),
                  "source_complete": False, "flashable": False, "hardware_proof": False,
                  "limits": ["Animation-start lower routine is controlled; full display behavior is outside this replay.",
                             "Native fatal write is observed as an unmapped write fault."]}
        folder.mkdir(parents=True, exist_ok=True)
        receipt = folder / "oracle-receipt.json"
        receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(status, count, sha(receipt))


if __name__ == "__main__":
    main()
