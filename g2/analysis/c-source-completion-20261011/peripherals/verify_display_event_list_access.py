"""Connected actual compiled ARM C/native LV event-list accessor effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_event_list_access.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_event_count_450388(void*a){(void)a;return 3;}
void *audio_uart_lv_event_slot_450390(void*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_uart_lv_event_compact_450346(void*a){(void)a;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...)
{(void)a;(void)b;(void)c;(void)d;}'''
FUNCS={'count':(0x450158,'audio_uart_display_event_list_count_450158'),
       'at':(0x450190,'audio_uart_display_event_list_at_450190'),
       'remove':(0x4501d2,'audio_uart_display_event_list_remove_4501d2')}
NATIVE={'count':0x450388,'slot':0x450390,'compact':0x450346,'log':0x44d25c}
NAMES={'count':'audio_uart_lv_event_count_450388',
       'slot':'audio_uart_lv_event_slot_450390',
       'compact':'audio_uart_lv_event_compact_450346','log':'audio_uart_lvgl_log'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_event_list_count_450158',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        for present in (False,True):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                lst=0x20001000;slot=0x20002000;descriptor=0x20003000
                u.mem_write(slot,struct.pack('<I',descriptor if present else 0))
                u.mem_write(descriptor+8,struct.pack('<I',0x12345678))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,lst);u.reg_write(UC_ARM_REG_R1,1)
                mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
                calls=[]
                def hook(uc,a,size,_):
                    if a not in mapping:return
                    n=mapping[a];calls.append((n,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if n=='slot' else None))
                    uc.reg_write(UC_ARM_REG_R0,3 if n=='count' else slot if n=='slot' else 0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=150)
                result=u.reg_read(UC_ARM_REG_R0) if name!='remove' or not present else 1
                traces.append((result,calls,u.mem_read(lst+20,1),u.mem_read(descriptor+8,4)))
            assert traces[0]==traces[1],(name,present,traces)
    print('PASS 6 compiled-C/native event-list count/lookup/remove cases')
