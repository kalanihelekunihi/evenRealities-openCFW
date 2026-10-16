#!/usr/bin/env python3
"""Compare LV size setters with native calls, skips, and null assertions."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_size_43f4c0.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_page_43f4c0": (0x43f4c0, 0x43f506, "1258e9bbe9c2b2bfb71fdb97341d9d7386f0abd175cb244ab693cc8b7cd4b652"),
    "audio_uart_page_43f506": (0x43f506, 0x43f568, "80b3551e5004e2906368646e44e3cf3f4368db8c71278ad96bd4e00313e2b936"),
    "audio_uart_page_43f568": (0x43f568, 0x43f5ca, "3b4a83b0c22894cb71d868387e2473e20883de9270761ef4c54ce084a84ebf3f"),
    "audio_uart_page_441164": (0x441164, 0x441172, "dfae41b44b846301235271942e5ff864eae436df249b34a6966d0749e23aa495"),
    "audio_uart_page_44118e": (0x44118e, 0x44119c, "75f58c772500c63334a65bd89b41060b1fade822792432bf61d8dad408dd0730"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-obj-set-size-43f4c0"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_page_style_get_44beaa(uint32_t a,uint32_t b,uint32_t*c,uint32_t d){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_style_apply_44be4c(void*a,uint8_t b,uint32_t c,uint32_t d){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43f4c0",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, object_, first, second, status, same):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        for reg, word in ((A.UC_ARM_REG_R0, object_), (A.UC_ARM_REG_R1, first),
                          (A.UC_ARM_REG_R2, second), (A.UC_ARM_REG_SP, 0x2000f000),
                          (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, word)
        hooks = ({0x44d25c: "log", 0x44beaa: "get", 0x44be4c: "apply"} if not compiled
                 else {symbols["audio_uart_lvgl_log"] & ~1: "log",
                       symbols["audio_uart_page_style_get_44beaa"] & ~1: "get",
                       symbols["audio_uart_page_style_apply_44be4c"] & ~1: "apply"})
        seen = []

        def string(address):
            return bytes(uc.mem_read(address, 160)).split(b"\0")[0].decode("ascii")

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == "log":
                stack = cpu.reg_read(A.UC_ARM_REG_SP)
                args = [int.from_bytes(cpu.mem_read(stack + 4*i, 4), "little")
                        for i in range(3)]
                seen.append((name, r0, string(r1), r2, string(r3),
                             *(string(arg) for arg in args)))
                cpu.emu_stop()
            elif name == "get":
                seen.append((name, r0, r1, r3))
                expected = first if r1 == 1 else second if entry == "audio_uart_page_43f4c0" else first
                current = expected if same else expected ^ 1
                cpu.mem_write(r2, current.to_bytes(4, "little"))
                cpu.reg_write(A.UC_ARM_REG_R0, status)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            else:
                seen.append((name, r0, r1, r2, r3))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x600000, count=500)
        return seen

    cases = 0
    for entry in BODIES:
        is_size = entry in ("audio_uart_page_43f4c0", "audio_uart_page_43f506",
                            "audio_uart_page_43f568")
        for object_ in (0, 0x20000120):
            for status in ((0, 1, 2, 0x101) if is_size and object_ else (0,)):
                for same in ((False, True) if is_size and object_ else (False,)):
                    for first, second in ((0, 0), (0x12345678, 0xfedcba98)):
                        native = run(False, entry, object_, first, second, status, same)
                        candidate = run(True, entry, object_, first, second, status, same)
                        assert native == candidate, (entry, object_, status, same,
                                                     first, second, native, candidate)
                        cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_OBJ_SET_SIZE_43F4C0",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["Null assertions are compared through logger arguments before the invalid write.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
