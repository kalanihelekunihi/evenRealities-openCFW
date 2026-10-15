#!/usr/bin/env python3
"""Compare Apollo LV draw-task style builder with stock under controlled leaves."""
import hashlib, json, re, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_build_452616.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-build-452616"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SPECIAL = {"audio_queue_copy_bytes": 0x439be4,
           "audio_uart_lv_grid_copy_454738": 0x454738,
           "audio_uart_lv_image_source_type_488cb8": 0x488cb8,
           "audio_uart_lv_draw_task_opacity_452df0": 0x452df0,
           "audio_uart_lv_draw_rgb_mix_452e22": 0x452e22,
           "audio_uart_lv_draw_color_variant_452e68": 0x452e68}
BASE_VALUES = {
    0x4525f4: 0x123, 0x452308: 255, 0x4522e8: 0x112233,
    0x45236c: 0, 0x452334: 1, 0x452314: 0x334455,
    0x452340: 2, 0x45234a: 3, 0x452354: 4, 0x452360: 5,
    0x4523fa: 1, 0x4523ee: 255, 0x452404: 17, 0x4523ce: 0x445566,
    0x452410: 1, 0x45243a: 255, 0x452446: 0x9988, 0x45241a: 0x667788,
    0x452376: 0x20016000, 0x452380: 255, 0x4525be: 0x20018000,
    0x452592: 0x778899, 0x45238c: 0x8899aa, 0x4523ac: 128,
    0x4523b8: 1, 0x452450: 1, 0x452498: 255, 0x45245a: 7,
    0x452464: 8, 0x45246e: 9, 0x452478: 0xaabbcc}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def cases():
    suite = []
    def add(name, selector=0, opacity=255, flags="frisc", values=None, kind=2, border=False):
        suite.append(dict(name=name, selector=selector, opacity=opacity, flags=flags,
                          values=values or {}, kind=kind, border=border))
    add("all-full")
    add("all-half", opacity=128)
    add("all-opaque-boundary", opacity=253)
    add("all-attenuate-boundary", opacity=252)
    add("all-zero", opacity=0)
    add("all-two", opacity=2)
    add("selected-hidden", selector=1, opacity=2)
    add("selected-full", selector=1)
    add("selected-half", selector=4, opacity=128)
    add("selected-small", selector=4, opacity=3)
    for flag in "frisc": add("only-" + flag, flags=flag)
    add("none", flags="")
    add("fill-border-record", flags="f", border=True)
    add("fill-no-border", flags="f", values={0x452334: 0})
    add("fill-low", flags="f", values={0x452308: 2})
    add("rectangle-low", flags="r", values={0x4523ee: 2})
    add("rectangle-zero", flags="r", values={0x4523fa: 0})
    add("image-zero", flags="i", values={0x452376: 0})
    add("image-low", flags="i", values={0x452380: 2})
    add("image-other", flags="i", kind=1)
    add("image-other-selected", selector=3, flags="i", kind=1)
    add("shadow-low", flags="s", values={0x45243a: 2})
    add("shadow-zero", flags="s", values={0x452410: 0})
    add("compass-alpha-boundary", flags="c", values={0x452498: 3})
    add("compass-low", flags="c", values={0x452498: 2})
    add("compass-zero", flags="c", values={0x452450: 0})
    return suite

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj, elf, shim = directory / "builder.o", directory / "builder.elf", directory / "shim.c"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-c",
                        str(SOURCE), "-o", str(obj)], check=True)
        names = [line.split()[-1] for line in subprocess.check_output(
            ["arm-none-eabi-nm", "-u", str(obj)], text=True).splitlines()]
        addresses = {name: SPECIAL.get(name, int(match.group(1), 16) if
                     (match := re.search(r"_([0-9a-f]{6})$", name)) else 0)
                     for name in names}
        if len(addresses) != 37 or any(value == 0 for value in addresses.values()):
            raise RuntimeError(("builder leaf inventory changed", addresses))
        shim.write_text("#include <stdint.h>\n" + "\n".join(
            f"uintptr_t {name}(void){{return 0;}}" for name in names) + "\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_task_build_452616",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, cfg):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj_addr, task, border, image = 0x20011000, 0x20013000, 0x20015000, 0x20016000
            t = bytearray((i * 7 + 3) & 0xff for i in range(0x80))
            for flag, offset in (("f", 0x20), ("r", 0x48), ("i", 0x3b),
                                 ("s", 0x58), ("c", 0x6c)):
                t[offset] = 255 if flag in cfg["flags"] else 0
            c.mem_write(task, bytes(t))
            b = bytearray((i * 3 + 2) & 0xff for i in range(0x20))
            b[0x0b] = (b[0x0b] & 0xf0) | (1 if cfg["border"] else 0)
            c.mem_write(border, bytes(b))
            c.mem_write(image, bytes([0x55]) * 0x20)
            targets = {(syms[name] if compiled else native) & ~1: native
                       for name, native in addresses.items()}
            trace = []
            def hook(c, current, size, _):
                native = targets.get(current)
                if native is None: return
                r0, r1, r2, r3 = (c.reg_read(r) for r in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if native in (0x439be4, 0x454738):
                    data = bytes(c.mem_read(r1, r2))
                    trace.append((native, r0, data, r2))
                    c.mem_write(r0, data)
                    value = r0
                elif native == 0x452df0:
                    value = cfg["opacity"]
                    trace.append((native, r0, r1, r2, value))
                elif native == 0x452e22:
                    value = (r3 ^ 0x00abcdef) & 0x00ffffff
                    trace.append((native, r0, r1, r2, r3, value))
                elif native == 0x452e68:
                    fifth = int.from_bytes(c.mem_read(c.reg_read(A.UC_ARM_REG_SP), 4), "little")
                    value = 0x88776655
                    trace.append((native, r0, r1, r2, r3, fifth, value))
                elif native == 0x488cb8:
                    value = cfg["kind"]
                    trace.append((native, r0, value))
                else:
                    value = cfg["values"].get(native, BASE_VALUES.get(native))
                    if value is None: raise AssertionError(("unmapped leaf", hex(native)))
                    if native == 0x45236c and cfg["border"]: value = border
                    trace.append((native, r0, r1, value))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj_addr)
            c.reg_write(A.UC_ARM_REG_R1, cfg["selector"])
            c.reg_write(A.UC_ARM_REG_R2, task)
            c.reg_write(A.UC_ARM_REG_R3, 0x12345678)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_task_build_452616"] if compiled else 0x452616
            c.emu_start(start | 1, 0x600000, count=30000)
            return trace, bytes(c.mem_read(task, 0x80))
        suite = cases()
        for index, cfg in enumerate(suite):
            native, source = run(False, cfg), run(True, cfg)
            if native != source: raise AssertionError((index, cfg["name"], native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_BUILD_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_entry": "0x452616", "cases": len(suite),
               "controlled_provider_count": len(addresses),
               "compared_task_bytes": 0x80,
               "limits": ["Style, opacity, color, image-type and copy providers are controlled; live theme mutation and rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), len(addresses), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
