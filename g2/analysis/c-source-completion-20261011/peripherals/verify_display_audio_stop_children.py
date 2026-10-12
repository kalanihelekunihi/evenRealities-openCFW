"""Actual compiled ARM C/native 0x45f840 list search and stop-event effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_audio_stop_children.c'
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_obj_event_451670(void*a,uint32_t b,void*c)
{(void)a;(void)b;(void)c;return 1;}'''
FUNCS={'all':(0x45f6da,'audio_uart_display_audio_stop_all_45f6da'),
       'find':(0x45f840,'audio_uart_display_audio_find_45f840'),
       'one':(0x45f6c0,'audio_uart_display_audio_stop_one_45f6c0'),
       'top':(0x45f6ec,'audio_uart_display_audio_stop_top_45f6ec')}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_audio_find_45f840',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        for where in ('none','first','second'):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                state=0x20001000;first=0x20002000;second=0x20003000
                u.mem_write(state+8,struct.pack('<I',first if where=='first' else 0))
                u.mem_write(state+12,struct.pack('<I',second if where=='second' else 0))
                u.mem_write(state+24,struct.pack('<I',0x20004000))
                u.mem_write(first,struct.pack('<I',7));u.mem_write(second,struct.pack('<I',7))
                u.mem_write(first+32,b'\0'*4);u.mem_write(second+32,b'\0'*4)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,state);u.reg_write(UC_ARM_REG_R1,7)
                event=(syms['audio_uart_lv_obj_event_451670']&~1) if is_c else 0x451670
                calls=[]
                def hook(uc,a,size,_):
                    if a!=event:return
                    code=uc.reg_read(UC_ARM_REG_R1);p=uc.reg_read(UC_ARM_REG_R2)
                    calls.append((uc.reg_read(UC_ARM_REG_R0),code,None if p==0 else struct.unpack('<I',uc.mem_read(p,4))[0]))
                    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=120)
                result=u.reg_read(UC_ARM_REG_R0) if name!='all' else 0
                traces.append((result,calls))
            assert traces[0]==traces[1],(name,where,traces)
    print('PASS 12 compiled-C/native stop child list/event cases')
