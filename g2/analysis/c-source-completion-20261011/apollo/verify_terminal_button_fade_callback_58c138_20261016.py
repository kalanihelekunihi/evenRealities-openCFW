#!/usr/bin/env python3
"""Compare recursive button fade callback and wrapper with pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_button_fade_callback_58c138.c"
OUT = G2 / "build/c-firmware/20261016/main-terminal-button-fade-callback-58c138"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (("audio_uart_page_44130c", 0x44130c),
         ("audio_uart_page_44104c", 0x44104c),
         ("audio_uart_page_441068", 0x441068),
         ("audio_uart_lv_child_count_44ddea", 0x44ddea),
         ("audio_uart_lv_child_get_44dce2", 0x44dce2),
         ("audio_uart_lv_class_is_43e2d4", 0x43e2d4),
         ("audio_uart_page_4413ce", 0x4413ce),
         ("audio_uart_page_44140e", 0x44140e))
ROOT_OBJECT = 0x20001000
IMAGE, LABEL, CONTAINER, NESTED = (0x20002000, 0x20002100, 0x20002200, 0x20002300)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "button-fade-callback-oracle-stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "const uint8_t audio_uart_image_class_756108[36]={0};\n"
                    "const uint8_t audio_uart_page_class_7561bc[36]={0};\n"
                    "__attribute__((noinline,used)) void audio_uart_page_44130c(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_page_44104c(uint32_t a){return a;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_page_441068(uint32_t a,uint32_t b,uint32_t c){return a+b+c;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_child_count_44ddea(uint32_t a){(void)a;return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_child_get_44dce2(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n"
                    "__attribute__((noinline,used)) uint32_t audio_uart_lv_class_is_43e2d4(uint32_t a,const void*b){(void)a;(void)b;return 0;}\n"
                    "__attribute__((noinline,used)) void audio_uart_page_4413ce(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n"
                    "__attribute__((noinline,used)) void audio_uart_page_44140e(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n")
    elf = OUT / "button-fade-callback-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_button_fade_callback_58c230",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry_kind, object, alpha, layout):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        image_class = symbols["audio_uart_image_class_756108"] if compiled else 0x756108
        page_class = symbols["audio_uart_page_class_7561bc"] if compiled else 0x7561bc
        cuts = {(symbols[name] if compiled else address) & ~1: i
                for i, (name, address) in enumerate(CALLS)}
        tree = {ROOT_OBJECT: layout, CONTAINER: [NESTED], IMAGE: [], LABEL: [], NESTED: []}
        trace = []

        def hook(cpu, pc, size, _):
            i = cuts.get(pc)
            if i is None:
                return
            a, b, c = (cpu.reg_read(reg) for reg in
                       (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if i == 0:
                trace.append(("root-opacity", a, b, c))
                ret = 0
            elif i == 1:
                trace.append(("color", a))
                ret = 0x005a2c1f if a == 0x444444 else 0x00cfb782
            elif i == 2:
                trace.append(("blend", a, b, c))
                ret = 0x112233
            elif i == 3:
                trace.append(("count", a))
                ret = len(tree.get(a, []))
            elif i == 4:
                trace.append(("child", a, b))
                ret = tree.get(a, [])[b]
            elif i == 5:
                class_name = "image" if b == image_class else "page" if b == page_class else b
                trace.append(("class", a, class_name))
                ret = int((a == IMAGE and b == image_class) or
                          (a in (LABEL, NESTED) and b == page_class))
            elif i == 6:
                trace.append(("style-opacity", a, b, c))
                ret = 0
            else:
                trace.append(("style-color", a, b, c))
                ret = 0
            cpu.reg_write(A.UC_ARM_REG_R0, ret)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object)
        u.reg_write(A.UC_ARM_REG_R1, alpha)
        name = "audio_terminal_button_fade_callback_58c230" if entry_kind == "wrapper" else "audio_terminal_button_fade_recursive_58c138"
        entry = symbols[name] if compiled else (0x58c230 if entry_kind == "wrapper" else 0x58c138)
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace

    cases = 0
    layouts = ([], [IMAGE], [LABEL], [CONTAINER],
               [IMAGE, LABEL], [CONTAINER, IMAGE, LABEL], [0, CONTAINER, LABEL])
    for entry_kind in ("wrapper", "recursive"):
        for object in (0, ROOT_OBJECT):
            for alpha in (0, 1, 0x80, 0xff, 0x100, 0xffffffff):
                for layout in layouts:
                    case = (entry_kind, object, alpha, layout)
                    stock, selected = run(False, *case), run(True, *case)
                    if stock != selected:
                        raise RuntimeError(f"button fade mismatch {case}: {stock} != {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_BUTTON_FADE_CALLBACK_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Wrapper, color interpolation, opacity, recursive image/page dispatch",
              "limits": ["Real LVGL style effects and concurrent or cyclic object trees outside bounded oracle."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()
