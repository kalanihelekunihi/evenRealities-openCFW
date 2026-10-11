"""Compiled C/native Cordio message allocation, enqueue and task ready flow."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_wsf_task_state[80],block[32];
void *audio_wsf_buffer_alloc(uint16_t n){(void)n;return block;}
void audio_wsf_queue_enqueue(void *q,void *m){(void)q;(void)m;}
void audio_wsf_cs_enter(void){}void audio_wsf_cs_exit(void){}void audio_wsf_set_os_event(void){}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_wsf_msg_alloc',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_msg.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_msg_children.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,alloc_ok,handler):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        block=syms['block'] if c else 0x20085000;state=syms['audio_wsf_task_state'] if c else 0x20073230
        captures=[];u.reg_write(UC_ARM_REG_R0,12);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        mapping={syms['audio_wsf_buffer_alloc'] if c else 0x530446:'alloc',
                 syms['audio_wsf_queue_enqueue'] if c else 0x538c24:'enqueue',
                 syms['audio_wsf_cs_enter'] if c else 0x52b8a4:'enter',
                 syms['audio_wsf_cs_exit'] if c else 0x52b8b6:'exit',
                 syms['audio_wsf_set_os_event'] if c else 0x52b8d8:'event'}
        def cut(uc,a,size,_):
            if a not in mapping:return
            kind=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
            if kind=='alloc':captures.append((kind,r0));result=block if alloc_ok else 0
            elif kind=='enqueue':captures.append((kind,r0-state,r1-block));result=0
            else:captures.append((kind,));result=0
            uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_wsf_msg_alloc'] if c else 0x4bf99e)|1,0x600000,count=1000)
        allocated=u.reg_read(UC_ARM_REG_R0)
        if allocated:
            u.reg_write(UC_ARM_REG_R0,handler);u.reg_write(UC_ARM_REG_R1,allocated);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((syms['audio_wsf_msg_send'] if c else 0x4bf9ba)|1,0x600000,count=3000)
        return allocated-block if allocated else 0,bytes(u.mem_read(block,16)),bytes(u.mem_read(state+0x3c,1)),captures
    for case in [(False,3),(True,3),(True,9)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
        print('PASS WSF msg',case)
