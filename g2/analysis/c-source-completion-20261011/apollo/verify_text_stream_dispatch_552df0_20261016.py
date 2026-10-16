#!/usr/bin/env python3
"""Controlled stock/C comparison for text-stream dispatch decisions."""
import hashlib, json, subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4
ROOT=Path(__file__).resolve().parents[4]; G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_dispatch_552df0.c'
OUT=G2/'build/c-firmware/20261016/main-text-stream-dispatch'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STUB='''#include <stdint.h>\n#include <stddef.h>\nvoid audio_text_stream_pause_552d40(void*a){(void)a;}\nuint32_t audio_text_stream_buffer_create_553338(void*a,void**b,uint32_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}\nuint32_t audio_text_stream_prefix_match_552ecc(const char*a,const char*b){(void)a;(void)b;return 0;}\nvoid audio_text_stream_begin_552f0a(void*a,uint32_t b){(void)a;(void)b;}\nvoid audio_text_stream_finish_552f14(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nsize_t strlen(const char*a){(void)a;return 0;}\nchar*strcpy(char*a,const char*b){(void)b;return a;}\n'''
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(payload,segments,sy,compiled,mode,notify,source,target,total,capacity_ok):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,payload)
    cpu.mem_map(0x100000,0x100000);cpu.mem_map(0x20000000,0x100000)
    for a,b in segments:cpu.mem_write(a,b)
    obj=0x20003000;dst=0x20004000;src=0x20005000
    seed=bytearray([0xa5]*0x30)
    for off,value in ((0,dst if target is not None else 0),(4,src if source is not None else 0),(0x0c,7),(0x10,total),(0x18,0),(0x24,64)):
        seed[off:off+4]=value.to_bytes(4,'little')
    cpu.mem_write(obj,bytes(seed))
    if target is not None:cpu.mem_write(dst,target+b'\0')
    if source is not None:cpu.mem_write(src,source+b'\0')
    cpu.reg_write(UC_ARM_REG_R0,obj);cpu.reg_write(UC_ARM_REG_R1,mode);cpu.reg_write(UC_ARM_REG_R2,notify)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    stock={0x552d40:'pause',0x44a43c:'strlen',0x553338:'capacity',0x48d540:'strcpy',0x552ecc:'prefix',0x552f0a:'begin',0x552f14:'finish'}
    compiled_names={'audio_text_stream_pause_552d40':'pause','strlen':'strlen','audio_text_stream_buffer_create_553338':'capacity','strcpy':'strcpy','audio_text_stream_prefix_match_552ecc':'prefix','audio_text_stream_begin_552f0a':'begin','audio_text_stream_finish_552f14':'finish'}
    hooks={sy[k]&~1:v for k,v in compiled_names.items()} if compiled else stock
    calls=[]
    def readstr(machine,p):
        s=bytearray();i=0
        while (ch:=machine.mem_read(p+i,1)[0])!=0:s.append(ch);i+=1
        return bytes(s)
    def hook(machine,pc,width,unused):
        kind=hooks.get(pc)
        if kind is None:return
        a=machine.reg_read(UC_ARM_REG_R0);b=machine.reg_read(UC_ARM_REG_R1);c=machine.reg_read(UC_ARM_REG_R2);d=machine.reg_read(UC_ARM_REG_R3)
        if kind=='strlen':result=len(readstr(machine,a));calls.append(('strlen',a,result))
        elif kind=='capacity':result=int(capacity_ok);calls.append(('capacity',a,b,c,d))
        elif kind=='strcpy':
            data=readstr(machine,b)+b'\0';machine.mem_write(a,data);result=a;calls.append(('strcpy',a,b))
        elif kind=='prefix':
            x=readstr(machine,a);y=readstr(machine,b);result=next((i for i,(p,q) in enumerate(zip(x,y)) if p!=q),min(len(x),len(y)))
            calls.append(('prefix',a,b,result))
        elif kind=='finish':result=0;calls.append(('finish',a,b,c))
        else:result=0;calls.append((kind,a,b) if kind=='begin' else (kind,a))
        machine.reg_write(UC_ARM_REG_R0,result);machine.reg_write(UC_ARM_REG_PC,machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=sy['audio_text_stream_dispatch_552df0'] if compiled else 0x552df0
    cpu.emu_start(entry|1,0x600000,count=2000)
    return bytes(cpu.mem_read(obj,0x30)),bytes(cpu.mem_read(dst,32)),calls

def main():
    payload=PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest()!=PINNED:raise RuntimeError('Apollo payload changed')
    OUT.mkdir(parents=True,exist_ok=True)
    stub=OUT/'dispatch-oracle-stub.c';stub.write_text(STUB)
    elf_path=OUT/'dispatch-oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_text_stream_dispatch_552df0',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as f:
        elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    for mode in (0,1,2,3,256,257,258):
      for notify in (0,1,257):
       for source,target,total in ((None,b'',5),(b'abc',b'',0),(b'abc',b'',5),(b'abc',b'ab',5),(b'abc',b'ax',5),(b'abc',b'abcde',5),(b'abc',b'abcdef',5),(b'abc',b'ab',2)):
        for capacity_ok in (False,True):
         args=(mode,notify,source,target,total,capacity_ok)
         stock=run(payload,segments,sy,False,*args);actual=run(payload,segments,sy,True,*args)
         if stock!=actual:raise RuntimeError(f'dispatch mismatch {args}: {stock!r} != {actual!r}')
         cases+=1
    receipt={'status':'PASS_EXPERIMENTAL_TEXT_STREAM_DISPATCH_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Mode byte narrowing, empty input, prefix/length decisions, capacity and lower-call order','limits':['Callback branch and lower-call side effects remain open.']}
    path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(receipt['status'],cases,sha(path))
if __name__=='__main__':main()
