#!/usr/bin/env python3
"""Compare stock/C EvenAI service state writes and ordered lower calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_service_dispatch_497ea2.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    stub = tmp / "stub.c"
    stub.write_text("""#include <stdint.h>
uint8_t audio_even_ai_service_state_2006ed10[0x218];
uint8_t audio_even_ai_config_state_20074974[3];
uint32_t trace[8],trace_count,timer_argument;
void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t n){timer_argument=n;trace[trace_count++]=1;}
void audio_even_ai_state_lock_4e1fa6(void){trace[trace_count++]=2;}
void audio_even_ai_state_unlock_4e1fbe(void){trace[trace_count++]=3;}
""")
    elf = tmp / "service.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_even_ai_service_dispatch_497ea2",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, opcode, status, text_length):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x100000)
        payload = bytearray((17 + i * 13) & 255 for i in range(0x220))
        payload[0] = status
        payload[4:6] = text_length.to_bytes(2, "little")
        payload[8:10] = text_length.to_bytes(2, "little")
        cpu.mem_write(0x20001000, bytes(payload))
        state_seed = bytes((91 + i * 7) & 255 for i in range(0x218))
        config_seed = b"\xc1\xc2\xc3"
        cpu.mem_write(0x2006ed10, state_seed)
        cpu.mem_write(0x20074974, config_seed)
        cpu.mem_write(symbols["audio_even_ai_service_state_2006ed10"], state_seed)
        cpu.mem_write(symbols["audio_even_ai_config_state_20074974"], config_seed)
        cpu.reg_write(A.UC_ARM_REG_R0, opcode)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x20001000)
        cpu.reg_write(A.UC_ARM_REG_R2, 0x208)
        cpu.reg_write(A.UC_ARM_REG_R3, 0)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        calls = []
        if not compiled:
            lower = {0x4e304c: 1, 0x4e1fa6: 2, 0x4e1fbe: 3}
            def intercept(uc, address, size, _):
                if address not in lower:
                    return
                code = lower[address]
                calls.append((code, uc.reg_read(A.UC_ARM_REG_R0) if code == 1 else 0))
                uc.reg_write(A.UC_ARM_REG_R0, 0)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, intercept)
        entry = symbols["audio_even_ai_service_dispatch_497ea2"] if compiled else 0x497ea2
        cpu.emu_start(entry | 1, 0x600000, count=200000)
        if compiled:
            n = int.from_bytes(cpu.mem_read(symbols["trace_count"], 4), "little")
            assert n <= 8
            raw = cpu.mem_read(symbols["trace"], n * 4)
            timer_arg = int.from_bytes(cpu.mem_read(symbols["timer_argument"], 4), "little")
            calls = [(int.from_bytes(raw[i:i+4], "little"),
                      timer_arg if i == 0 else 0) for i in range(0, len(raw), 4)]
        state_addr = symbols["audio_even_ai_service_state_2006ed10"] if compiled else 0x2006ed10
        config_addr = symbols["audio_even_ai_config_state_20074974"] if compiled else 0x20074974
        return (cpu.reg_read(A.UC_ARM_REG_R0), calls,
                bytes(cpu.mem_read(state_addr, 0x218)),
                bytes(cpu.mem_read(config_addr, 3)))

    cases = []
    for opcode in range(12):
        statuses = (0, 1, 2, 3, 4, 255) if opcode in (1, 2) else (0x2a,)
        lengths = (0, 1, 16, 512, 513, 65535) if opcode in (3, 5, 6) else (0,)
        for status in statuses:
            for length in lengths:
                stock = run(False, opcode, status, length)
                source = run(True, opcode, status, length)
                assert stock == source, (opcode, status, length, stock[:2], source[:2],
                                         [(i, a, b) for i, (a, b) in enumerate(zip(stock[2], source[2])) if a != b][:6])
                cases.append((opcode, status, length, stock[0]))

    output = G2 / "build/c-firmware/20261016/main-even-ai-service-dispatch-497ea2/oracle-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_NATIVE_MAIN_EVEN_AI_SERVICE_DISPATCH_497EA2",
               "cases": len(cases),
               "case_tuples": cases,
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "bounds": "timer/lock/unlock controlled, full 0x218 state and three config bytes compared; no timer or final RAM ownership"}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(cases), hashlib.sha256(output.read_bytes()).hexdigest())
