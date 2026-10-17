#!/usr/bin/env python3
"""Direct stock/C replay of timer callback-table dispatch."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_remove_5b36be.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_timer_callbacks_75ea90.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-timer-remove-5b36be"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLBACKS = [
    ("audio_conversate_timer_1_start_5b3766", 0x5b3766, 0x101100, "1_start"),
    ("audio_conversate_timer_1_stop_5b37c8", 0x5b37c8, 0x101110, "1_stop"),
    ("audio_conversate_timer_2_start_5b37d8", 0x5b37d8, 0x101120, "2_start"),
    ("audio_conversate_timer_2_stop_5b383c", 0x5b383c, 0x101130, "2_stop"),
    ("audio_conversate_timer_3_start_5b384c", 0x5b384c, 0x101140, "3_start"),
    ("audio_conversate_timer_3_stop_5b38b6", 0x5b38b6, 0x101150, "3_stop"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b3e2c-0x438000:0x5b3e30-0x438000] == (0x75ea90).to_bytes(4, "little")
    stock_table = payload[0x75ea90-0x438000:0x75eab0-0x438000]
    expected = b"\0"*8 + b"".join(struct.pack("<I", native|1) for _, native, _, _ in CALLBACKS)
    if stock_table != expected:
        raise RuntimeError("native timer callback table changed")
    obj, elf_path = OUT / "oracle-remove.o", OUT / "oracle-remove.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-T", str(LINKER), "-e",
                    "audio_conversate_timer_remove_5b36be",
                    *[f"--defsym={name}=0x{compiled|1:x}" for name, _, compiled, _ in CALLBACKS],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        table = elf.get_section_by_name(".g2_conversate_timer_callbacks_75ea90")
        if table is None or table["sh_addr"] != 0x75ea90 or table["sh_size"] != 0x20:
            raise RuntimeError("compiled timer callback table moved")
        expected_compiled = b"\0"*8 + b"".join(struct.pack("<I", compiled|1) for _, _, compiled, _ in CALLBACKS)
        if table.data() != expected_compiled:
            raise RuntimeError("compiled timer callback table changed")

    def run(native, index, slot):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        for reg, value in ((A.UC_ARM_REG_R0, index), (A.UC_ARM_REG_R1, slot),
                           (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        callbacks = {n if native else c: label for _, n, c, label in CALLBACKS}
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc in callbacks:
                events.append(callbacks[pc])
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b36be if native else symbols["audio_conversate_timer_remove_5b36be"])|1,
                      0, count=200)
        if not done[0]: raise RuntimeError(f"timer dispatch did not return: {native, index, slot}")
        return events

    cases = [(index, slot) for index in (0, 1, 2, 3, 4, 255, 256, 257, 258, 259)
             for slot in (0, 1, 2, 3, 255, 256, 257, 258)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"timer dispatch mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_REMOVE_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "linker_script": str(LINKER.relative_to(ROOT)),
              "linker_sha256": hashlib.sha256(LINKER.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Six callback bodies are controlled lower contracts.",
                         "The indirect-call target is compared; incidental argument/return registers are not."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
