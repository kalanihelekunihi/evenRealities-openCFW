#!/usr/bin/env python3
"""Compare LV page instance cache/rebuild effects with official Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_instance_487022.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
FUNCTIONS = {"audio_uart_page_487022": (0x487022, 0x487156),
             "audio_uart_page_instance_ready_48716c": (0x48716c, 0x487180),
             "audio_uart_page_rgb_equal_44102e": (0x44102e, 0x44104c)}
OUT = G2 / "build/c-firmware/20261015/main-lv-page-instance-487022"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "alloc": (0x44f730, "audio_uart_lv_heap_alloc"),
    "current": (0x44fa1a, "audio_uart_display_current_44fa1a"),
    "dpi": (0x44fbe6, "audio_uart_lv_display_dpi_44fbe6"),
    "width": (0x44fa7e, "audio_uart_lv_display_width_44fa7e"),
    "build": (0x484a98, "audio_uart_lv_page_build_484a98"),
    "theme": (0x44fe7e, "audio_uart_lv_theme_lookup_44fe7e"),
    "refresh": (0x44bc48, "audio_uart_lv_theme_refresh_all_44bc48"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint8_t audio_uart_display_lv_state[0x400];\n" +
                    "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b){{__asm volatile("bx lr");}}'
        for _, symbol in PROVIDERS.values()) +
        '\n__attribute__((naked)) void audio_uart_lv_page_callback_487188(void){__asm volatile("bx lr");}\n')
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_487022",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")
    def write32(cpu, a, v): cpu.mem_write(a, u32(v))

    def run(compiled, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        state = symbols["audio_uart_display_lv_state"] if compiled else 0x2006f548
        instance, display, fallback, resource = (0x20010000, 0x20020000,
                                                  0x20021000, 0x20030000)
        if config["ready"]:
            write32(uc, state + 0x178, instance)
            uc.mem_write(instance + 0x3c, b"\x01")
        write32(uc, instance + 0x2c, config["old_dpi"])
        uc.mem_write(instance + 0x28, bytes([config["old_class"]]))
        uc.mem_write(instance + 0x10, u32(config["old_foreground"])[:3])
        uc.mem_write(instance + 0x13, u32(config["old_background"])[:3])
        write32(uc, instance + 0x24, config["old_opacity"])
        write32(uc, instance + 0x18, config["old_resource"])
        uc.reg_write(A.UC_ARM_REG_R0, display if config["display"] else 0)
        uc.reg_write(A.UC_ARM_REG_R1, config["foreground"])
        uc.reg_write(A.UC_ARM_REG_R2, config["background"])
        uc.reg_write(A.UC_ARM_REG_R3, config["opacity"])
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        write32(uc, 0x200ff000, resource)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): key
                 for key, (address, symbol) in PROVIDERS.items()}
        trace = []

        def observe(cpu, address, size, _):
            key = hooks.get(address)
            if key is None: return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            trace.append((key,) if key in ("current", "alloc") else (key, r0))
            result = 0
            if key == "alloc": result = instance
            elif key == "current": result = fallback
            elif key == "dpi": result = config["dpi"]
            elif key == "width": result = config["width"]
            elif key == "theme": result = instance if config["theme_match"] else 0x20031000
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols["audio_uart_page_487022"] if compiled else 0x487022
        uc.emu_start(start | 1, 0x600000, count=5000)
        data = bytearray(uc.mem_read(instance, 0x40))
        data[0:4] = b"CALL"
        return trace, bytes(data), uc.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for ready in (False, True):
        for display in (False, True):
            for width in (100, 400, 800):
                for changed in ("none", "dpi", "class", "foreground",
                                "background", "opacity", "resource"):
                    for theme_match in (False, True):
                        config = {"ready": ready, "display": display,
                                  "width": width, "dpi": 180,
                                  "foreground": 0x112233, "background": 0x445566,
                                  "opacity": 1, "old_dpi": 181 if changed == "dpi" else 180,
                                  "old_class": 0 if changed == "class" else
                                               3 if width < 321 else 2 if width < 720 else 1,
                                  "old_foreground": 0x112234 if changed == "foreground" else 0x112233,
                                  "old_background": 0x445567 if changed == "background" else 0x445566,
                                  "old_opacity": 0 if changed == "opacity" else 1,
                                  "old_resource": 0x20030004 if changed == "resource" else 0x20030000,
                                  "theme_match": theme_match}
                        native = run(False, config)
                        candidate = run(True, config)
                        if native != candidate:
                            raise AssertionError((config, native, candidate))
                        cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_PAGE_INSTANCE_487022",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": {name: hashlib.sha256(
                   IMAGE[start-0x438000:end-0x438000]).hexdigest()
                   for name, (start, end) in FUNCTIONS.items()},
               "source_owned_symbols": sorted(FUNCTIONS), "cases": cases,
               "limits": ["Allocation, display, theme and page-build providers were controlled hooks; the page callback body remains open.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
