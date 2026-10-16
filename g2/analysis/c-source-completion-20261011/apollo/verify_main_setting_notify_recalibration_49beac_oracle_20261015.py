#!/usr/bin/env python3
"""Compare recalibration notification packet and call flow to official Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/setting_notify_recalibration_49beac.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x49beac-0x438000:0x49bf16-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-setting-notify-recalibration-49beac"
OUT.mkdir(parents=True, exist_ok=True)
CALLS = {"audio_uart_buffer_zero": 0x48949c, "audio_log_flags": 0x43d0ce,
         "audio_log_extended": 0x43d574, "compressed_log_output": 0x43ce9e,
         "audio_settings_notify_common": 0x49bbfc}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n" +
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-w",
                    "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_settings_notify_recalibration_status_49beac",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, status, flags):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x200000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.reg_write(A.UC_ARM_REG_R0,status)
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        hooks = {((symbols[s] & ~1) if compiled else a): s for s,a in CALLS.items()}
        trace=[]

        def cstr(ptr):
            data=bytes(uc.mem_read(ptr,256))
            return data[:data.index(0)].decode("ascii")

        def observe(cpu,address,size,_):
            kind=hooks.get(address)
            if kind is None:return
            r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                         A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
            result=0
            if kind=="audio_uart_buffer_zero":
                assert r[1:3]==[104,0]
                cpu.mem_write(r[0],bytes(104))
            elif kind=="audio_log_flags":
                trace.append(("flags",))
                result=flags
            elif kind=="audio_log_extended":
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                line=int.from_bytes(cpu.mem_read(sp,4),"little")
                msg=int.from_bytes(cpu.mem_read(sp+4,4),"little")
                arg=int.from_bytes(cpu.mem_read(sp+8,4),"little")
                trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
                              line,cstr(msg),arg))
            elif kind=="compressed_log_output":
                trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2]),r[3]))
            elif kind=="audio_settings_notify_common":
                trace.append(("notify",bytes(cpu.mem_read(r[0],104))))
                result=43
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols["audio_settings_notify_recalibration_status_49beac"] if compiled else 0x49beac
        uc.emu_start(start | 1,0x600000,count=1000)
        return trace

    cases=0
    for status in (0,1,255,0x12345678,0xffffffff):
        for flags in (0,1,2,4,7):
            native=run(False,status,flags)
            candidate=run(True,status,flags)
            if native!=candidate:
                raise AssertionError((status,flags,native,candidate))
            cases+=1

    receipt={"status":"PASS_NATIVE_MAIN_SETTING_NOTIFY_RECALIBRATION_49BEAC",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_settings_notify_recalibration_status_49beac"],
             "cases":cases,
             "limits":["Packet construction and call flow were compared with controlled logging and notification providers; final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
