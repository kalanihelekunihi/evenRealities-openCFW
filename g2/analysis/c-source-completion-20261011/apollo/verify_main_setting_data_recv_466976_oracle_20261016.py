#!/usr/bin/env python3
"""Controlled native/C comparison for stock Setting data receive routing."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_data_recv_handler_466976.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x466976-0x438000:0x466abc-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-data-recv-466976"
CALLS={"audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e,
       "audio_setting_dispatch_message_466abc":0x466abc,
       "audio_setting_serialize_response_49b900":0x49b900,
       "audio_setting_serialize_local_response_49ba58":0x49ba58}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        shim=Path(temp)/"shim.c"
        shim.write_text("#include <stdint.h>\n"+"\n".join(
            f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
        elf=Path(temp)/"candidate.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                        "-nostdlib","-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_setting_process_data_466976",str(SOURCE),str(shim),
                        "-o",str(elf)],check=True)
        with elf.open("rb") as handle:
            parsed=ELFFile(handle)
            segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                      if s["p_type"]=="PT_LOAD"]
            symbols={s.name:s["st_value"] for s in
                     parsed.get_section_by_name(".symtab").iter_symbols()}
        def run(compiled,kind,flags,response,local):
            uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
            uc.mem_map(0x100000,0x200000)
            for address,data in segments:uc.mem_write(address,data)
            uc.mem_map(0x20000000,0x100000)
            ptr=0 if kind is None else 0x20020000
            if ptr:
                message=bytearray(32);message[8:10]=kind.to_bytes(2,"little")
                uc.mem_write(ptr,bytes(message))
            for reg,value in ((A.UC_ARM_REG_R0,ptr),(A.UC_ARM_REG_SP,0x200ff000),
                              (A.UC_ARM_REG_LR,0x600001)):
                uc.reg_write(reg,value)
            hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
            trace=[]
            def cstr(address):
                data=bytes(uc.mem_read(address,160))
                return data.split(b"\0",1)[0].decode("ascii")
            def observe(cpu,address,size,_):
                name=hooks.get(address)
                if name is None:return
                regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                 A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                result=0
                if name=="audio_log_flags":
                    trace.append(("flags",));result=flags
                elif name=="audio_log_extended":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    line=int.from_bytes(cpu.mem_read(sp,4),"little")
                    message=int.from_bytes(cpu.mem_read(sp+4,4),"little")
                    item=("extended",regs[0],cstr(regs[1]),cstr(regs[2]),cstr(regs[3]),
                          line,cstr(message))
                    if "%d" in item[-1]:
                        item+=(int.from_bytes(cpu.mem_read(sp+8,4),"little"),)
                    trace.append(item)
                elif name=="compressed_log_output":
                    item=("compressed",regs[0],cstr(regs[1]),cstr(regs[2]))
                    if "%d" in item[-1]:item+=(regs[3],)
                    trace.append(item)
                elif name=="audio_setting_dispatch_message_466abc":
                    trace.append(("dispatch",regs[0]==ptr))
                elif name=="audio_setting_serialize_response_49b900":
                    trace.append(("serialize_app",));result=response
                elif name=="audio_setting_serialize_local_response_49ba58":
                    trace.append(("serialize_local",));result=local
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE,observe)
            start=symbols["audio_setting_process_data_466976"] if compiled else 0x466976
            uc.emu_start(start|1,0x600000,count=1200)
            return uc.reg_read(A.UC_ARM_REG_R0),trace
        cases=0
        for kind in (None,0,3,4,5,0xffff):
            for flags in (0,1,2,4,7):
                for response in (0,1,0xfffffffd):
                    for local in (0,2):
                        n=run(False,kind,flags,response,local)
                        c=run(True,kind,flags,response,local)
                        if n!=c:raise AssertionError((kind,flags,response,local,n,c))
                        cases+=1
        receipt={"status":"PASS_NATIVE_MAIN_SETTING_DATA_RECV_466976",
                 "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
                 "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
                 "source_owned_symbols":["audio_setting_process_data_466976"],"cases":cases,
                 "limits":["Message dispatcher and two serializers are controlled hooks; final RAM layout and hardware behavior remain open."]}
        path=OUT/"oracle-receipt.json"
        path.write_text(json.dumps(receipt,indent=2)+"\n")
        print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
