#!/usr/bin/env python3
"""Compare EvenAI lock/unlock lower calls against authenticated Apollo main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_state_mutex_4e1fa6.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CELL = 0x20074580
assert int.from_bytes(IMAGE[0x4e2a40-0x438000:0x4e2a44-0x438000], "little") == CELL
ROUTES = (("audio_even_ai_state_lock_4e1fa6", 0x4e1fa6, "audio_file_mutex_acquire", 0x4497b6),
          ("audio_even_ai_state_unlock_4e1fbe", 0x4e1fbe, "audio_file_mutex_release", 0x44981c))

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) int32_t audio_file_mutex_acquire(void*p,uint32_t n){__asm volatile("bx lr");}\n'
                    '__attribute__((naked)) int32_t audio_file_mutex_release(void*p){__asm volatile("bx lr");}\n')
    elf = Path(temp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-Wno-unused-parameter", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_even_ai_state_lock_4e1fa6",
                    "-Wl,--defsym=audio_even_ai_mutex_20074580=0x20074580",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, route, mutex):
        function, stock_entry, lower_name, stock_lower = route
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x80000)
        cpu.mem_write(CELL, mutex.to_bytes(4, "little"))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(A.UC_ARM_REG_R7, 0x76543210)
        seen = []
        lower = (symbols[lower_name] & ~1) if compiled else stock_lower
        def intercept(uc, address, size, _):
            if address != lower:
                return
            seen.append((uc.reg_read(A.UC_ARM_REG_R0),
                         uc.reg_read(A.UC_ARM_REG_R1) if lower_name.endswith("acquire") else None))
            uc.reg_write(A.UC_ARM_REG_R0, 0)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE, intercept)
        cpu.emu_start((symbols[function] if compiled else stock_entry) | 1, 0x600000, count=150)
        return seen, bytes(cpu.mem_read(CELL, 4))

    results = []
    for route in ROUTES:
        for mutex in (0, 0x20012340, 0xffffffff):
            stock = run(False, route, mutex)
            candidate = run(True, route, mutex)
            assert stock == candidate, (route[0], mutex, stock, candidate)
            results.append({"function": route[0], "mutex": mutex, "calls": stock[0]})

OUT = G2 / "build/c-firmware/20261016/main-even-ai-state-mutex-4e1fa6"
OUT.mkdir(parents=True, exist_ok=True)
receipt = {"status": "PASS_NATIVE_MAIN_EVEN_AI_STATE_MUTEX_4E1FA6",
           "cases": len(results), "results": results,
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "ram_cell": hex(CELL),
           "bounds": "lock/unlock call suppression and arguments; lower mutex semantics and RAM placement excluded"}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print(receipt["status"], receipt["cases"], hashlib.sha256(path.read_bytes()).hexdigest())
