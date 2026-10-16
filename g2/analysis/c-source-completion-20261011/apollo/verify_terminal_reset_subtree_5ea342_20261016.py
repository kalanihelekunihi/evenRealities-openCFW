#!/usr/bin/env python3
"""Compare Terminal empty-list subtree with pinned stock call contract."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_subtree_5ea342.c"
ASSETS = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_assets_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-subtree-5ea342"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_page_43de82", 0x43de82, 1),
         ("audio_uart_page_43f4c0", 0x43f4c0, 3),
         ("audio_uart_page_43f09a", 0x43f09a, 3),
         ("audio_uart_page_43dfa4", 0x43dfa4, 2),
         ("audio_uart_page_44129e", 0x44129e, 3),
         ("audio_uart_page_44131c", 0x44131c, 3),
         ("audio_terminal_lv_style_four_5ea224", 0x5ea224, 3),
         ("audio_uart_page_44146a", 0x44146a, 3),
         ("audio_uart_page_498668", 0x498668, 1),
         ("audio_uart_page_498680", 0x498680, 2),
         ("audio_uart_page_43f6b8", 0x43f6b8, 4),
         ("audio_terminal_initial_image_y_5ea2d4", 0x5ea2d4, 0),
         ("audio_uart_page_499416", 0x499416, 1),
         ("audio_uart_page_43f506", 0x43f506, 2),
         ("audio_uart_page_layout_499678", 0x499678, 2),
         ("audio_uart_page_49942e", 0x49942e, 2),
         ("audio_uart_page_44104c", 0x44104c, 1),
         ("audio_uart_page_44140e", 0x44140e, 3),
         ("audio_uart_page_44145a", 0x44145a, 3),
         ("audio_uart_page_44143e", 0x44143e, 3))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "reset-subtree-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n"
                    "uint32_t audio_uart_ring_primary_head_cell;\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c,uint32_t d)"
                              "{{(void)a;(void)b;(void)c;(void)d;return 0;}}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "reset-subtree-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_reset_subtree_5ea342",
                    str(SOURCE), str(ASSETS), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, root, existing, font, pattern, return_zero):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        font_cell = symbols["audio_uart_ring_primary_head_cell"] if compiled else 0x200746dc
        u.mem_write(state, bytes(((i + pattern) & 255 for i in range(0x2a0))))
        u.mem_write(state, struct.pack("<I", 0x20001000 if root else 0))
        u.mem_write(state + 0x1e0, struct.pack("<I", 0x20002000 if existing else 0))
        u.mem_write(font_cell, struct.pack("<I", font))
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address, _) in enumerate(CALLS)}
        trace = []
        create_count = {0: 0, 8: 0, 12: 0}
        image_seen = 0
        def hook(cpu, pc, size, _):
            nonlocal image_seen
            i = cuts.get(pc)
            if i is None:
                return
            name, _, arity = CALLS[i]
            args = tuple(cpu.reg_read(r) for r in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            visible = list(args[:arity])
            if i == 9:
                image_seen += 1
                stock_asset = (0x773028, 0x7733a8)[image_seen - 1]
                if compiled:
                    expected = symbols[f"audio_terminal_asset_{stock_asset:x}"]
                    if visible[1] != expected:
                        raise RuntimeError("source image descriptor pointer changed")
                    original = blob[stock_asset - 0x438000:stock_asset - 0x438000 + 28]
                    observed = bytes(cpu.mem_read(expected, 28))
                    if observed[:16] != original[:16] or observed[20:] != original[20:]:
                        raise RuntimeError("source image descriptor fields changed")
                    size_bytes = struct.unpack_from("<I", original, 12)[0]
                    original_pixels = struct.unpack_from("<I", original, 16)[0]
                    selected_pixels = struct.unpack_from("<I", observed, 16)[0]
                    if bytes(cpu.mem_read(selected_pixels, size_bytes)) != blob[original_pixels - 0x438000:original_pixels - 0x438000 + size_bytes]:
                        raise RuntimeError("source image pixels changed")
                visible[1] = stock_asset
            elif i == 15:
                if compiled:
                    expected = symbols["audio_terminal_welcome_text_7069d0"]
                    if visible[1] != expected or bytes(cpu.mem_read(expected, 68)) != blob[0x7069d0 - 0x438000:0x7069d0 - 0x438000 + 68]:
                        raise RuntimeError("source welcome text changed")
                visible[1] = 0x7069d0
            trace.append((name, *visible))
            result = 0
            if i in create_count:
                create_count[i] += 1
                result = 0 if return_zero else {0: 0x20002000, 8: 0x20004000,
                                                12: 0x20006000}[i] + create_count[i] * 0x100
            elif i == 11:
                result = 0x12
            elif i == 16:
                result = 0x1234
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_reset_subtree_5ea342"] if compiled else 0x5ea342
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for root in (0, 1):
        for existing in (0, 1):
            for font in (0, 0x20007000):
                for pattern in (0, 0x5a, 0xff):
                    for return_zero in (0, 1):
                        args = (root, existing, font, pattern, return_zero)
                        stock, selected = run(False, *args), run(True, *args)
                        if stock != selected:
                            raise RuntimeError(f"subtree mismatch {args}: {stock[1]} != {selected[1]}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_RESET_SUBTREE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "assets": str(ASSETS.relative_to(ROOT)), "assets_sha256": sha(ASSETS),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Full Terminal UI state and ordered LVGL call arguments with controlled factories",
              "limits": ["Lower LVGL effects and final RAM placement remain open; source image pointers require final linker relocation."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
