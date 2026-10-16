#!/usr/bin/env python3
"""Native/C LV event callback descriptor and array setup comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_add_451740.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_page_451740": (0x451740, 0x451790, "2b01a268acfe0bf6b126a8a5720cdf1f80bfa3ef7ae2afc92d78f70b7619d3ba"),
    "audio_uart_lv_event_add_4500e4": (0x4500e4, 0x450158, "54dd79b705b3dac36b31cb50ca25e43a613a336c3037eed8ab7048c06a207a7f"),
    "audio_uart_lv_array_init_4883fc": (0x4883fc, 0x488440, "985d46cc3f391c6c3aaac9808c0e4a334727d1fbda99f41c847e5ae11a26db1d"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-lv-event-add-451740"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_malloc(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_setup_layer_43e1fa(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_event_count_450388(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_array_push_488506(void*a,const void*b){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_451740",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, null_object, count, allocation_failure,
            callback, filter_, user_data):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        object_, spec, list_, descriptor, array_data = (0x20001000, 0x20002000,
                                                        0x20002008, 0x20005000,
                                                        0x20006000)
        uc.mem_write(object_ + 8, spec.to_bytes(4, "little"))
        uc.mem_write(list_, array_data.to_bytes(4, "little") +
                     count.to_bytes(4, "little") + b"\x01\0\0\0\x04\0\0\0")
        first_arg = (0 if null_object else object_) if entry == "audio_uart_page_451740" else list_
        if entry == "audio_uart_lv_array_init_4883fc":
            args = (list_, 1, 4, user_data)
        else:
            args = (first_arg, callback, filter_, user_data)
        for reg, word in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), args):
            uc.reg_write(reg, word)
        uc.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        native_hooks = {0x44d25c: "log", 0x44f718: "malloc",
                        0x43e1fa: "setup", 0x450388: "count",
                        0x488506: "push"}
        compiled_hooks = {symbols["audio_uart_lvgl_log"] & ~1: "log",
                          symbols["audio_uart_lv_malloc"] & ~1: "malloc",
                          symbols["audio_uart_lv_obj_setup_layer_43e1fa"] & ~1: "setup",
                          symbols["audio_uart_lv_event_count_450388"] & ~1: "count",
                          symbols["audio_uart_lv_array_push_488506"] & ~1: "push"}
        hooks = compiled_hooks if compiled else native_hooks
        seen = []

        def string(address):
            return bytes(uc.mem_read(address, 180)).split(b"\0")[0].decode("ascii")

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == "log":
                stack = cpu.reg_read(A.UC_ARM_REG_SP)
                words = [int.from_bytes(cpu.mem_read(stack + 4*i, 4), "little")
                         for i in range(3)]
                seen.append((name, r0, string(r1), r2, string(r3),
                             *(string(word) for word in words)))
                cpu.emu_stop()
                return
            if name == "push":
                seen.append((name, r0, int.from_bytes(cpu.mem_read(r1, 4), "little")))
                cpu.reg_write(A.UC_ARM_REG_R0, 1)
            elif name == "malloc":
                seen.append((name, r0))
                answer = 0 if allocation_failure == r0 else descriptor if r0 == 12 else array_data
                cpu.reg_write(A.UC_ARM_REG_R0, answer)
            elif name == "count":
                seen.append((name, r0))
                cpu.reg_write(A.UC_ARM_REG_R0, count)
            else:
                seen.append((name, r0))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x600000, count=600)
        result = (seen, bytes(uc.mem_read(list_, 17)),
                  bytes(uc.mem_read(descriptor, 12)))
        if entry != "audio_uart_lv_array_init_4883fc" and not any(item[0] == "log" for item in seen):
            result += (uc.reg_read(A.UC_ARM_REG_R0),)
        return result

    cases = 0
    for entry in BODIES:
        for null_object in ((False, True) if entry == "audio_uart_page_451740" else (False,)):
            for count in (0, 1):
                for allocation_failure in (0, 12, 4):
                    for callback, filter_, user_data in ((0x100001, 0, 0x20007000),
                                                         (0x100041, 0x12345678, 0)):
                        if entry == "audio_uart_lv_array_init_4883fc" and allocation_failure == 12:
                            continue
                        native = run(False, entry, null_object, count, allocation_failure,
                                     callback, filter_, user_data)
                        candidate = run(True, entry, null_object, count, allocation_failure,
                                        callback, filter_, user_data)
                        assert native == candidate, (entry, null_object, count,
                                                     allocation_failure, native, candidate)
                        cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_LV_EVENT_ADD_451740",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["Allocator, event-count, setup and array-push children were controlled hooks.",
                      "Fatal branches stop after logger arguments, before deliberate invalid writes.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
