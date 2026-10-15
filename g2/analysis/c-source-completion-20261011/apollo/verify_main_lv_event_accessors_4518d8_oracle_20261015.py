#!/usr/bin/env python3
"""Compare Apollo LV input-device and key event accessors with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_accessors_4518d8.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-accessors-4518d8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put(c, address, value): c.mem_write(address, value.to_bytes(4, "little"))
def string(c, address):
    raw = bytes(c.mem_read(address, 160))
    return raw.split(b"\0", 1)[0].decode("ascii")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    package = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
    blob = package.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim = directory / "log.c"
        elf = directory / "accessors.elf"
        shim.write_text("#include <stdint.h>\nvoid audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e){(void)a;(void)b;(void)c;(void)d;(void)e;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_input_reset_4518d8",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        cases = [("indev", code, 0x20013000, 0x14aabbcc) for code in
                 (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                  17, 18, 19, 20, 21, 22, 24, 25, 26, 0xffffffff)]
        cases += [("key", code, param, key) for code in (0, 17, 18, 0xffffffff)
                  for param, key in ((0, 0), (0x20013000, 0), (0x20013000, 0xaabbccdd))]
        def run(compiled, case):
            kind, code, param, key = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            event = 0x20011000
            c.mem_write(event, bytes([0xa5]) * 0x30)
            put(c, event + 8, code); put(c, event + 16, param)
            put(c, 0x20013000, key)
            log_address = (syms["audio_uart_lvgl_log"] if compiled else 0x44d25c) & ~1
            calls = []
            def hook(c, address, size, _):
                if address != log_address: return
                r0, r1, r2, r3 = (c.reg_read(r) for r in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                fifth = int.from_bytes(c.mem_read(c.reg_read(A.UC_ARM_REG_SP), 4), "little")
                calls.append((r0, string(c, r1), r2, string(c, r3), string(c, fifth)))
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, event)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            symbol = ("audio_uart_lv_input_reset_4518d8" if kind == "indev"
                      else "audio_uart_lv_event_param_4519a0")
            start = syms[symbol] if compiled else (0x4518d8 if kind == "indev" else 0x4519a0)
            c.emu_start(start | 1, 0x600000, count=1000)
            return c.reg_read(A.UC_ARM_REG_R0), calls, bytes(c.mem_read(event, 0x20))
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_ACCESSORS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x4518d8..0x45195f", "0x4519a0..0x4519cb"],
               "cases": len(cases), "limits": ["Controlled event memory and log boundary only; live input-device state remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
