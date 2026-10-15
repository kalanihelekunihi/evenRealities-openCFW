#!/usr/bin/env python3
"""Compare Apollo LV object state flag wrappers with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_flags_43e046.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43e046"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "flags.elf"
        shim.write_text("#include <stdint.h>\nvoid audio_uart_lv_obj_state_apply_43ebec(void*a,uint32_t b){(void)a;(void)b;}\nvoid audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_flag_set_43e046",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            kind, state, flags = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj = 0x20011000
            c.mem_write(obj, bytes([0xa5]) * 0x40)
            c.mem_write(obj + 0x28, state.to_bytes(2, "little"))
            target = (syms["audio_uart_lv_obj_state_apply_43ebec"] if compiled
                      else 0x43ebec) & ~1
            calls = []
            def hook(c, address, size, _):
                if address != target: return
                calls.append((c.reg_read(A.UC_ARM_REG_R0), c.reg_read(A.UC_ARM_REG_R1)))
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj)
            c.reg_write(A.UC_ARM_REG_R1, flags)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            symbol = ("audio_uart_lv_obj_flag_set_43e046" if kind == "set"
                      else "audio_uart_lv_obj_flag_clear_43e086")
            address = syms[symbol] if compiled else (0x43e046 if kind == "set" else 0x43e086)
            c.emu_start(address | 1, 0x600000, count=1000)
            return calls, bytes(c.mem_read(obj, 0x40))
        cases = [(kind, state, flags) for kind in ("set", "clear")
                 for state in (0, 1, 3, 0x1234, 0xffff)
                 for flags in (0, 1, 2, 0x20, 0x40, 0x10000, 0xffffffff)]
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_FLAGS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x43e046..0x43e085", "0x43e086..0x43e0c7"],
               "cases": len(cases),
               "limits": ["Valid object pointers and controlled state-apply boundary only; downstream state effects and null assertion trap remain untested."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
