"""Actual compiled ARM C/native 0x451790/7d6/81c wrapper effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_event_access.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_display_event_list_count_450158(void*a){(void)a;return 5;}
void *audio_uart_display_event_list_at_450190(void*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_uart_display_event_list_remove_4501d2(void*a,uint32_t b){(void)a;(void)b;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
FUNCS={'count':(0x451790,'audio_uart_display_event_count_451790'),
       'at':(0x4517d6,'audio_uart_display_event_at_4517d6'),
       'remove':(0x45181c,'audio_uart_display_event_remove_45181c')}
NATIVE={'list_count':0x450158,'list_at':0x450190,'list_remove':0x4501d2,'log':0x44d25c}
NAMES={'list_count':'audio_uart_display_event_list_count_450158',
       'list_at':'audio_uart_display_event_list_at_450190',
       'list_remove':'audio_uart_display_event_list_remove_4501d2','log':'audio_uart_lvgl_log'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_event_count_451790',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        for scenario in ('null','absent','present'):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                obj=0x20001000;u.mem_write(obj+8,struct.pack('<I',0x20002000 if scenario=='present' else 0))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,0 if scenario=='null' else obj)
                u.reg_write(UC_ARM_REG_R1,3)
                mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
                calls=[]
                def hook(uc,a,size,_):
                    if a not in mapping:return
                    n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                    if n=='log':calls.append((n,uc.reg_read(UC_ARM_REG_R2)))
                    else:calls.append((n,r0,r1 if n!='list_count' else None))
                    uc.reg_write(UC_ARM_REG_R0,5 if n=='list_count' else 0x20003000 if n=='list_at' else 0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                faults=[]
                def bad(uc,access,address,size,value,_):
                    faults.append((address,size,value));uc.emu_stop();return False
                u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad)
                try:u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=120)
                except Exception:
                    if not faults:raise
                result=u.reg_read(UC_ARM_REG_R0) if scenario!='null' and name!='remove' else None
                traces.append((result,calls,faults))
            assert traces[0]==traces[1],(name,scenario,traces)
    print('PASS 9 compiled-C/native object-event wrapper cases')
