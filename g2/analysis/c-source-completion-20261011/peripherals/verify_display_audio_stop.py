"""Actual compiled ARM C/native 0x45faa8 branch/call effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_audio_stop.c'
SHIM='''#include <stdint.h>
void audio_uart_display_audio_stop_all_45f6da(void*a,uint32_t b){(void)a;(void)b;}
void *audio_uart_display_audio_find_45f840(void*a,uint32_t b){(void)a;(void)b;return 0;}
void audio_uart_display_audio_stop_one_45f6c0(void*a,uint32_t b){(void)a;(void)b;}
void audio_uart_display_audio_stop_top_45f6ec(void*a,uint32_t b){(void)a;(void)b;}'''
NATIVE={'all':0x45f6da,'find':0x45f840,'one':0x45f6c0,'top':0x45f6ec}
NAMES={'all':'audio_uart_display_audio_stop_all_45f6da',
       'find':'audio_uart_display_audio_find_45f840',
       'one':'audio_uart_display_audio_stop_one_45f6c0',
       'top':'audio_uart_display_audio_stop_top_45f6ec'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_audio_stop',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for mode in (0,1,2,3,257):
        for state_null in (False,True):
            for idzero in (False,True):
                for found in (False,True):
                    traces=[]
                    for is_c in (False,True):
                        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                        for a,d in segs:u.mem_write(a,d)
                        state=0x20001000;entry=0x20002000;head=0x20003000
                        u.mem_write(state,struct.pack('<I',head));u.mem_write(head,struct.pack('<I',7))
                        u.mem_write(entry+11,b'\x01')
                        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                        u.reg_write(UC_ARM_REG_R0,0 if state_null else state)
                        u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,0 if idzero else 8)
                        mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
                        calls=[]
                        def hook(uc,a,size,_):
                            if a not in mapping:return
                            n=mapping[a];calls.append((n,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
                            uc.reg_write(UC_ARM_REG_R0,entry if found and n=='find' else 0)
                            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE,hook)
                        u.emu_start((syms['audio_uart_display_audio_stop'] if is_c else 0x45faa8)|1,0x600000,count=160)
                        traces.append((u.reg_read(UC_ARM_REG_R0),calls))
                    assert traces[0]==traces[1],(mode,state_null,idzero,found,traces)
    print('PASS 40 compiled-C/native audio-stop selector cases')
