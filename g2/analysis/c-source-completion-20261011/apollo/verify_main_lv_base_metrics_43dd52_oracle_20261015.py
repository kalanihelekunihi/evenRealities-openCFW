#!/usr/bin/env python3
"""Compare Apollo base-object style metric wrappers with native code."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_base_metrics_43dd52.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-metrics-43dd52"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void*p,uint32_t s,uint32_t m)
{(void)p;(void)s;(void)m;return 0;}
'''
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_metric_43dd52",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            variant,selector,value=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            page=0x20011000
            c.mem_write(page,bytes([0])*0x80)
            target=syms["audio_uart_lv_style_property_44bdea"] if compiled else 0x44bdea
            trace=[]
            def hook(cpu,address,size,_):
                if address!=(target&~1):return
                trace.append(tuple(cpu.reg_read(r) for r in
                    (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)))
                cpu.reg_write(A.UC_ARM_REG_R0,value)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,page)
            c.reg_write(A.UC_ARM_REG_R1,selector)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            name=("audio_uart_lv_metric_43dd52","audio_uart_lv_metric_43dd5c","audio_uart_lv_metric_43dd66","audio_uart_lv_metric_43de76")[variant]
            entry=syms[name] if compiled else (0x43dd52,0x43dd5c,0x43dd66,0x43de76)[variant]
            c.emu_start(entry|1,0x600000,count=10000)
            return trace,c.reg_read(A.UC_ARM_REG_R0)
        cases=list(itertools.product(range(4),(0,1,0xff,0xffffffff),
                                     (0,0x12345678,0xffffffff)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_METRICS_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,
             "native_spans":["0x43dd52..0x43dd5b","0x43dd5c..0x43dd65","0x43dd66..0x43dd71","0x43de76..0x43de81"],
             "cases":len(cases),"limits":["Style provider is controlled; base-class event and final descriptor layout remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
