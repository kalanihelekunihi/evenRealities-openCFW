#!/usr/bin/env python3
"""Compare LV theme refresh and recursive style removal with official Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_theme_refresh_all_44bc48.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
FUNCTIONS = {"audio_uart_lv_theme_refresh_all_44bc48": (0x44bc48, 0x44bc8c),
             "audio_uart_lv_theme_refresh_node_44c970": (0x44c970, 0x44c9dc)}
OUT = G2 / "build/c-firmware/20261015/main-lv-theme-refresh-all-44bc48"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "display_next": (0x44fa22, "audio_uart_lv_display_next_44fa22"),
    "child_count": (0x44ddea, "audio_uart_lv_child_count_44ddea"),
    "selector": (0x44b860, "audio_uart_page_style_selector_44b860"),
    "removed": (0x44ce2a, "audio_uart_lv_style_removed_44ce2a"),
    "refresh": (0x44bc8c, "audio_uart_page_style_refresh_44bc8c"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint8_t audio_uart_display_lv_state[0x400];\n" +
                    "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b,uint32_t c){{__asm volatile("bx lr");}}'
        for _, symbol in PROVIDERS.values()))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_theme_refresh_all_44bc48",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")

    def run(compiled, name, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        state = symbols["audio_uart_display_lv_state"] if compiled else 0x2006f548
        uc.mem_write(state + 0x24, bytes([config["enabled"]]))
        display, roots, root, child = (0x20020000, 0x20021000, 0x20030000, 0x20031000)
        rows, spec, children = 0x20040000, 0x20042000, 0x20043000
        uc.mem_write(display + 0x2b8, u32(roots))
        uc.mem_write(display + 0x2d4, u32(config["root_count"]))
        uc.mem_write(roots, u32(root))
        uc.mem_write(root + 0x2a, (config["rows"] << 4).to_bytes(2, "little"))
        uc.mem_write(root + 0x0c, u32(rows))
        uc.mem_write(rows, u32(config["row_theme"]) + u32(0x01001234) +
                     u32(0x20050004) + u32(0x01005678))
        uc.mem_write(root + 8, u32(spec))
        uc.mem_write(spec, u32(children))
        uc.mem_write(children, u32(child))
        uc.mem_write(child + 0x2a, (1 << 4).to_bytes(2, "little"))
        uc.mem_write(child + 0x0c, u32(rows + 8))
        uc.mem_write(child + 8, u32(spec))
        uc.reg_write(A.UC_ARM_REG_R0, config["theme"])
        if name.endswith("node_44c970"):
            uc.reg_write(A.UC_ARM_REG_R1, root)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): key
                 for key, (address, symbol) in PROVIDERS.items()}
        trace = []

        def observe(cpu, address, size, _):
            key = hooks.get(address)
            if key is None: return
            r0, r1, r2 = (cpu.reg_read(A.UC_ARM_REG_R0),
                          cpu.reg_read(A.UC_ARM_REG_R1),
                          cpu.reg_read(A.UC_ARM_REG_R2))
            trace.append((key, r0, r1 if key in ("refresh", "removed") else None,
                          r2 if key == "refresh" else None))
            result = 0
            if key == "display_next": result = display if r0 == 0 else 0
            elif key == "child_count": result = config["children"] if r0 == root else 0
            elif key == "selector": result = 0x9876
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols[name] if compiled else FUNCTIONS[name][0]
        uc.emu_start(start | 1, 0x600000, count=3000)
        return trace

    cases = 0
    for name in FUNCTIONS:
        for enabled in (0, 1):
            for root_count in (0, 1):
                for rows in (0, 1, 2):
                    for theme in (0, 0x20050000, 0x20050004):
                        for children in (0, 1):
                            config = {"enabled": enabled, "root_count": root_count,
                                      "rows": rows, "theme": theme,
                                      "row_theme": 0x20050000, "children": children}
                            native = run(False, name, config)
                            candidate = run(True, name, config)
                            if native != candidate:
                                raise AssertionError((name, config, native, candidate))
                            cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_THEME_REFRESH_ALL_44BC48",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": {name: hashlib.sha256(
                   IMAGE[start-0x438000:end-0x438000]).hexdigest()
                   for name, (start, end) in FUNCTIONS.items()},
               "source_owned_symbols": sorted(FUNCTIONS), "cases": cases,
               "limits": ["Display iteration, style effects and child count were controlled hooks; final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
