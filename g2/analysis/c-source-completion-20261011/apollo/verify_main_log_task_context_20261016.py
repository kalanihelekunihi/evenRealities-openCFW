#!/usr/bin/env python3
"""Compare compiled Main logger task-context wrappers with stock paths."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/log_task_context_strings_44ab14.c"
OUT = G2 / "build/c-firmware/20261016/main-log-task-context"
BASE = G2 / "build/c-firmware/20261016/main-locale-five-current-replay/801-final-final-main-ring-descriptor-data-20002c48.o"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def engine():
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x300000, 0x1000)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_map(0x20000000, 0x10000)
    uc.reg_write(UC_ARM_REG_SP, 0x2000f000)
    uc.reg_write(UC_ARM_REG_LR, 0x300001)
    return uc


def read_string(uc, address):
    return bytes(uc.mem_read(address, 64)).split(b"\0", 1)[0]


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    probe_source = OUT / "task-context-oracle-stubs.c"
    probe_source.write_text("""#include <stdint.h>
volatile uint32_t probe_scheduler_state;
volatile uintptr_t probe_current_task;
uint32_t audio_scheduler_state(void) { return probe_scheduler_state; }
void *receiver_current_task(void) { return (void *)probe_current_task; }
uint32_t audio_os_interrupt_mask_5fa0a4(void) { return 0; }
""")
    elf_path = OUT / "task-context-oracle.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-ffreestanding", "-fno-builtin",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,g2_log_process_string",
                    str(SOURCE), str(probe_source), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
        symbols = {sym.name: sym["st_value"] for sym in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = [(1, 0), (1, 0x20001000), (0, 0x20001000), (2, 0x20001000)]
    rows = []
    for name, native in (("g2_log_process_string", 0x44ab14),
                         ("g2_log_thread_string", 0x44ab1c)):
        for scheduler, task in cases:
            stock = engine()
            stock.mem_write(0x438000, payload)
            calls = []

            def hook(uc, address, size, _):
                if address in (0x4558a4, 0x45589c):
                    calls.append(hex(address))
                    uc.reg_write(UC_ARM_REG_R0, scheduler if address == 0x4558a4 else task)
                    uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

            stock.hook_add(UC_HOOK_CODE, hook)
            if task:
                stock.mem_write(task + 0x34, b"probe-task\0")
            stock.emu_start(native | 1, 0x300000, count=10000)
            original = read_string(stock, stock.reg_read(UC_ARM_REG_R0))
            compiled = engine()
            for address, data in segments:
                if data:
                    compiled.mem_write(address, data)
            compiled.mem_write(symbols["probe_scheduler_state"], scheduler.to_bytes(4, "little"))
            compiled.mem_write(symbols["probe_current_task"], task.to_bytes(4, "little"))
            if task:
                compiled.mem_write(task + 0x34, b"probe-task\0")
            compiled.emu_start(symbols[name] | 1, 0x300000, count=10000)
            candidate = read_string(compiled, compiled.reg_read(UC_ARM_REG_R0))
            if original != candidate or original != (b"unknown" if scheduler == 1 else b"probe-task"):
                raise RuntimeError(f"task-context mismatch {name} {scheduler} {task:#x}")
            rows.append({"symbol": name, "scheduler": scheduler, "task": hex(task),
                         "result": original.decode(), "stock_cuts": calls})
    base_undefined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(BASE)], text=True).splitlines() if line.strip()}
    candidate_obj = OUT / "candidate.o"
    final_undefined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(candidate_obj)], text=True).splitlines() if line.strip()}
    if (len(base_undefined) != 134 or len(final_undefined) != 132 or
            base_undefined - final_undefined != {"g2_log_process_string", "g2_log_thread_string"} or
            final_undefined - base_undefined):
        raise RuntimeError("Main import frontier changed")
    result = {"status": "PASS_BOUNDED_MAIN_LOG_TASK_CONTEXT_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "base_object": str(BASE.relative_to(ROOT)), "base_object_sha256": sha(BASE),
              "candidate_object": str(candidate_obj.relative_to(ROOT)), "candidate_object_sha256": sha(candidate_obj),
              "oracle_elf": str(elf_path.relative_to(ROOT)), "oracle_elf_sha256": sha(elf_path),
              "oracle_stubs": str(probe_source.relative_to(ROOT)), "oracle_stubs_sha256": sha(probe_source),
              "cases": rows, "case_count": len(rows),
              "unresolved_before": 134, "unresolved_after": 132,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Only scheduler states 0/1/2 and non-null task-name paths are compared.",
                         "The null-TCB fatal path is source-shaped from disassembly, not executed in this oracle.",
                         "The separate date/time formatter at 0x44aaa8 and whole Main image remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(rows), sha(path))


if __name__ == "__main__":
    main()
