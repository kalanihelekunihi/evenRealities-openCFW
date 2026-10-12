"""Actual compiled ARM C/native 0x451862 event selection and null fault."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_event_remove_callback.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_display_event_count_451790(void*a){(void)a;return 0;}
void *audio_uart_display_event_at_4517d6(void*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_uart_display_event_remove_45181c(void*a,uint32_t b){(void)a;(void)b;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
NATIVE={'count':0x451790,'at':0x4517d6,'remove':0x45181c,'log':0x44d25c}
NAMES={'count':'audio_uart_display_event_count_451790',
       'at':'audio_uart_display_event_at_4517d6',
       'remove':'audio_uart_display_event_remove_45181c','log':'audio_uart_lvgl_log'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_event_remove_callback',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[(0,()),(1,()),(1,(0,)),(3,(1,)),(3,(0,2)),(3,(0,1,2)),(-1,())]
    for count,matched in cases:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            for i in range(max(0,count)):
                u.mem_write(0x20002000+i*16,struct.pack('<I',0x500001 if i in matched else 0x500101))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,0 if count<0 else 0x20001000)
            u.reg_write(UC_ARM_REG_R1,0x500001)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                calls.append((n,r0,r1 if n in ('at','remove') else None))
                ret={'count':max(0,count),'at':0x20002000+r1*16}.get(n,0)
                uc.reg_write(UC_ARM_REG_R0,ret)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            faults=[]
            def bad_write(uc,access,address,size,value,_):
                faults.append((address,size,value));uc.emu_stop();return False
            u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad_write)
            start=syms['audio_uart_display_event_remove_callback'] if is_c else 0x451862
            try:u.emu_start(start|1,0x600000,count=500)
            except Exception:
                if not faults:raise
            traces.append((None if count<0 else u.reg_read(UC_ARM_REG_R0),calls,faults))
        assert traces[0]==traces[1],(count,matched,traces)
    print('PASS 7 compiled-C/native event removal and null-fault cases')
