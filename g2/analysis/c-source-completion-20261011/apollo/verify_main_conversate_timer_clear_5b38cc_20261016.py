#!/usr/bin/env python3
"""Direct stock/C replay of timer-manager RAM clear."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_clear_5b38cc.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_timer_mgr_ram_20261016.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-timer-clear-5b38cc"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b3e48-0x438000:0x5b3e4c-0x438000] == (0x20073a3c).to_bytes(4, "little")
    obj, elf_path = OUT / "oracle-clear.o", OUT / "oracle-clear.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-T", str(LINKER), "-e",
                    "audio_conversate_timer_clear_5b38cc", str(obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        section = elf.get_section_by_name(".g2_conversate_timer_mgr_ram_20073a3c")
        if (section is None or section["sh_addr"] != 0x20073a3c or
                section["sh_size"] != 0x1c or section["sh_type"] != "SHT_NOBITS"):
            raise RuntimeError("timer-manager RAM layout changed")

    def run(native, fill):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20073a38, bytes([fill])*0x24)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b38cc if native else symbols["audio_conversate_timer_clear_5b38cc"])|1,
                      0, count=100)
        if not done[0]: raise RuntimeError(f"timer clear did not return: {native, fill}")
        return bytes(cpu.mem_read(0x20073a38, 0x24)).hex()

    cases = [0, 1, 0x5a, 0xa5, 0xff]
    for fill in cases:
        a, b = run(True, fill), run(False, fill)
        if a != b: raise RuntimeError(f"timer clear mismatch {fill}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_CLEAR_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "linker_script": str(LINKER.relative_to(ROOT)),
              "linker_sha256": hashlib.sha256(LINKER.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Only direct clear effects and adjacent sentinels are compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
