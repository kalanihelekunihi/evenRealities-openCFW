#!/usr/bin/env python3
"""Native/C QuickList row-selection comparison with selected copy provider."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_select_records_4f5662.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-select-records"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    for literal, value in ((0x4f61f0, 0x20367bd8), (0x4f5c3c, 0x2012a72c),
                           (0x4f62f0, 0x20101a1c)):
        assert int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") == value
    shim = "void audio_uart_checksum_copy(void*a,const void*b,unsigned c){}\n"
    with tempfile.TemporaryDirectory() as td:
        sh = Path(td) / "shim.c"
        sh.write_text(shim)
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_select_records_4f5662", str(SRC), str(sh),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, output_present, selected_present, capacity, active, filter_value,
                existing_count, duplicate):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x200000)
            u.mem_map(0x20300000, 0x100000)
            source, output, default_output, count_addr = 0x20101a1c, 0x20020000, 0x20367bd8, 0x20018000
            for index in range(20):
                row = source + index*232
                u.mem_write(row, (index+1).to_bytes(4, "little"))
                u.mem_write(row+228, bytes([1 if index in active else 0]))
            u.mem_write(source+0x1222, b"\x02")
            u.mem_write(output, b"\xa5"*(20*232))
            u.mem_write(default_output, b"\xb6"*(20*232))
            u.mem_write(count_addr, (0xdeadbeef).to_bytes(4, "little"))
            existing = 0x2012a72c
            u.mem_write(existing, existing_count.to_bytes(2, "little"))
            for prior in range(1, existing_count):
                item_id = (2 if duplicate and prior == 1 else 100+prior)
                u.mem_write(existing+296*prior+0x114, item_id.to_bytes(4, "little"))
            copy_addr = (syms["audio_uart_checksum_copy"] & ~1) if compiled else 0x439c04
            trace = []

            def hook(uc, address, size, unused):
                if address != copy_addr:
                    return
                d, s, n = (uc.reg_read(r) for r in
                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                trace.append((d, s, n))
                if n:
                    uc.mem_write(d, bytes(uc.mem_read(s, n)))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, output if output_present else 0)
            u.reg_write(A.UC_ARM_REG_R1, capacity)
            u.reg_write(A.UC_ARM_REG_R2, count_addr if selected_present else 0)
            u.reg_write(A.UC_ARM_REG_R3, filter_value)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_select_records_4f5662"] if compiled else 0x4f5662
            u.emu_start(entry | 1, 0x600000, count=10000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace,
                    bytes(u.mem_read(count_addr, 4)), bytes(u.mem_read(output, 20*232)),
                    bytes(u.mem_read(default_output, 20*232)), bytes(u.mem_read(source, 20*232)))

        count = 0
        active_sets = ((), (0,), (1,), (0, 1, 3, 19), tuple(range(20)))
        for output_present, selected_present, capacity, active, filter_value, existing_count, duplicate in itertools.product(
                (False, True), (False, True), (0, 1, 4, 20), active_sets, (1, 2), (0, 3), (False, True)):
            old = run(False, output_present, selected_present, capacity, active, filter_value,
                      existing_count, duplicate)
            new = run(True, output_present, selected_present, capacity, active, filter_value,
                      existing_count, duplicate)
            if old != new:
                raise AssertionError((output_present, selected_present, capacity, active,
                                      filter_value, existing_count, duplicate, old[:2], new[:2],
                                      old[2:] == new[2:]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SELECT_RECORDS_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5662..0x4f570d", "cases": count,
               "limits": ["Forward copy is controlled at the native lower interface.",
                          "Tests cover null output/count, filter, capacity, active rows and duplicate IDs.",
                          "Final RAM placement and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
