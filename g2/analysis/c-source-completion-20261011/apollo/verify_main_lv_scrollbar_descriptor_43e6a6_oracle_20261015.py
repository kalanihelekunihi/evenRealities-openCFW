#!/usr/bin/env python3
"""Compare Apollo scrollbar draw descriptor with stock under controlled services."""
import hashlib, json, re, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scrollbar_descriptor_43e6a6.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-scrollbar-descriptor-43e6a6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def cases():
    base = dict(fill=0, border=0, border_width=0, pad=0, pad_width=0,
                alpha=255, color=0x12345678, radius=7)
    suite = []
    def add(**fields): suite.append(base | fields)
    add()
    add(fill=2)
    add(fill=3)
    add(border=3)
    add(border=3, border_width=1)
    add(border=255, border_width=-1)
    add(pad=3)
    add(pad=3, pad_width=1)
    add(pad=255, pad_width=-1)
    add(fill=3, border=3, border_width=1, pad=3, pad_width=1)
    add(fill=3, border=3, border_width=1, pad=3, pad_width=1, alpha=252)
    add(fill=3, border=3, border_width=1, pad=3, pad_width=1, alpha=2)
    add(fill=255, border=255, border_width=1, pad=255, pad_width=1, alpha=253)
    add(fill=255, border=255, border_width=1, pad=255, pad_width=1, alpha=256)
    add(fill=255, alpha=128)
    add(border=255, border_width=1, alpha=128)
    add(pad=255, pad_width=1, alpha=128)
    add(fill=3, color=0xaabbccdd, radius=0x87654321)
    return suite

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        obj, shim, elf = directory / "descriptor.o", directory / "shim.c", directory / "descriptor.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-c",
                        str(SOURCE), "-o", str(obj)], check=True)
        providers = [line.split()[-1] for line in subprocess.check_output(
            ["arm-none-eabi-nm", "-u", str(obj)], text=True).splitlines()]
        addresses = {name: (0x439be4 if name == "audio_queue_copy_bytes" else
                            int(re.search(r"_([0-9a-f]{6})$", name).group(1), 16))
                     for name in providers}
        if len(addresses) != 13: raise RuntimeError("descriptor provider set changed")
        shim.write_text("#include <stdint.h>\n" + "\n".join(
            f"uint32_t {name}(void){{return 0;}}" for name in providers) + "\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_scrollbar_draw_descriptor_43e6a6",
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
            obj_addr, task = 0x20011000, 0x20013000
            c.mem_write(obj_addr, bytes([0x55]) * 0x40)
            c.mem_write(task, bytes([0xa5]) * 0x90)
            targets = {(syms[name] if compiled else native) & ~1: native
                       for name, native in addresses.items()}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                op = f"{native:06x}"
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                value = 0
                if native == 0x451b9c:
                    trace.append((op, r0))
                    c.mem_write(r0, bytes((i * 7 + 3) & 0xff for i in range(0x70)))
                elif native == 0x439be4:
                    data = bytes(c.mem_read(r1, r2))
                    trace.append((op, r0, data, r2))
                    c.mem_write(r0, data)
                else:
                    trace.append((op, r0, r1))
                    values = {0x43dda8: cfg["fill"], 0x43dd9a: cfg["color"],
                              0x43ddf0: cfg["border"],
                              0x43ddfc: cfg["border_width"],
                              0x43dde2: cfg["color"], 0x43de3e: cfg["pad"],
                              0x43de1c: cfg["pad_width"],
                              0x43de26: 0xabcdef01,
                              0x43de30: cfg["color"],
                              0x44c47a: cfg["alpha"], 0x43de4a: cfg["radius"]}
                    value = values[native]
                c.reg_write(A.UC_ARM_REG_R0, value & 0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj_addr)
            c.reg_write(A.UC_ARM_REG_R1, task)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_scrollbar_draw_descriptor_43e6a6"] if compiled else 0x43e6a6
            c.emu_start(start | 1, 0x600000, count=10000)
            return c.reg_read(A.UC_ARM_REG_R0), trace, bytes(c.mem_read(task, 0x90))
        suite = cases()
        for index, cfg in enumerate(suite):
            native, source = run(False, cfg), run(True, cfg)
            if native != source: raise AssertionError((index, cfg, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_DESCRIPTOR_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x43e6a6..0x43e7d1", "cases": len(suite),
               "controlled_provider_count": len(addresses),
               "limits": ["Draw task init, style and copy providers are controlled; live theme, allocations and rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), len(addresses), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
