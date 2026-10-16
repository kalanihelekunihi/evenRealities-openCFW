#!/usr/bin/env python3
"""Compare EvenAI heartbeat state writes and lower calls with Apollo main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_heartbeat_timer_4e304c.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CELL = 0x20074014
assert int.from_bytes(IMAGE[0x4e316c-0x438000:0x4e3170-0x438000], "little") == CELL
ENTRY = 0x4e304c

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) uint32_t audio_settings_device_role(void){__asm volatile("bx lr");}\n'
                    '__attribute__((naked)) uint32_t g2_flashdb_candidate_tick(void){__asm volatile("bx lr");}\n')
    elf = Path(temp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_even_ai_heartbeat_timer_start_4e304c",
                    "-Wl,--defsym=audio_even_ai_heartbeat_state_20074014=0x20074014",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, role, timeout, tick):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x80000)
        cpu.mem_write(CELL, b"\xa5" * 12)
        cpu.reg_write(A.UC_ARM_REG_R0, timeout)
        cpu.reg_write(A.UC_ARM_REG_R3, 0x12345678)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols["audio_settings_device_role"] & ~1) if compiled else 0x45a568):
                 ("role", role),
                 ((symbols["g2_flashdb_candidate_tick"] & ~1) if compiled else 0x4490cc):
                 ("tick", tick)}
        trace = []
        def intercept(uc, address, size, _):
            if address not in hooks:
                return
            name, result = hooks[address]
            trace.append(name)
            uc.reg_write(A.UC_ARM_REG_R0, result)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE, intercept)
        entry = symbols["audio_even_ai_heartbeat_timer_start_4e304c"] if compiled else ENTRY
        cpu.emu_start(entry | 1, 0x600000, count=500)
        return trace, bytes(cpu.mem_read(CELL, 12))

    results = []
    for role in (0, 1, 2, 255):
        for timeout in (0, 10000, 0xffffffff):
            stock = run(False, role, timeout, 0x1234fedc)
            candidate = run(True, role, timeout, 0x1234fedc)
            assert stock == candidate, (role, timeout, stock, candidate)
            results.append({"role": role, "timeout": timeout,
                            "trace": stock[0], "state": stock[1].hex()})

OUT = G2 / "build/c-firmware/20261016/main-even-ai-heartbeat-timer-4e304c"
OUT.mkdir(parents=True, exist_ok=True)
receipt = {"status": "PASS_NATIVE_MAIN_EVEN_AI_HEARTBEAT_TIMER_4E304C",
           "cases": len(results), "results": results,
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "ram_cell": hex(CELL),
           "bounds": "mode/tick lower calls and twelve state bytes; lower semantics, incidental R3 return, and RAM placement excluded"}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print(receipt["status"], receipt["cases"], hashlib.sha256(path.read_bytes()).hexdigest())
