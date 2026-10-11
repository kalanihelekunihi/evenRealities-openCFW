"""Compiled C/native Cordio pool choice, free-list removal and FIFO enqueue."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t descriptors[24],blocks[512],queue[8];void *audio_wsf_pool_list=descriptors;
volatile uint8_t audio_wsf_pool_count,audio_wsf_cs_depth;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_wsf_buffer_alloc',str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_buf_queue.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_wsf_cs.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def setup(c):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        desc=syms['descriptors'] if c else 0x20084000;blocks=syms['blocks'] if c else 0x20085000
        wr(desc,16);wr(desc+8,blocks);wr(desc+12,64);wr(desc+20,blocks+256)
        wr(blocks,0);wr(blocks+4,0x12345678);wr(blocks+256,0);wr(blocks+260,0x12345678)
        wr(syms['audio_wsf_pool_list'],syms['descriptors']);wr(0x20074eec,0x20084000)
        u.mem_write(syms['audio_wsf_pool_count'],b'\x02');u.mem_write(0x20075044,b'\x02')
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                if a!=0x43d0ce:return
                uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        return u,wr,rd,desc,blocks
    for size in [8,20,100]:
        out=[]
        for c in [False,True]:
            u,wr,rd,desc,blocks=setup(c);u.reg_write(UC_ARM_REG_R0,size)
            u.emu_start((syms['audio_wsf_buffer_alloc'] if c else 0x530446)|1,0x600000,count=5000)
            p=u.reg_read(UC_ARM_REG_R0);out.append((p-blocks if p else None,rd(desc+8)-blocks if rd(desc+8) else None,rd(desc+20)-blocks if rd(desc+20) else None,rd(blocks+4),rd(blocks+260)))
        assert out[0]==out[1],(size,out)
        print('PASS WSF buf',size)
    for existing in [False,True]:
        out=[]
        for c in [False,True]:
            u,wr,rd,desc,blocks=setup(c);q=syms['queue'] if c else 0x20086000
            first=blocks+16;second=blocks+32
            if existing:wr(q,first);wr(q+4,first);wr(first,0)
            u.reg_write(UC_ARM_REG_R0,q);u.reg_write(UC_ARM_REG_R1,second)
            u.emu_start((syms['audio_wsf_queue_enqueue'] if c else 0x538c24)|1,0x600000,count=1000)
            out.append((rd(q)-blocks,rd(q+4)-blocks,rd(first)-blocks if existing else 0,rd(second)))
        assert out[0]==out[1],(existing,out)
        print('PASS WSF queue',existing)
    for length in [0,1,2]:
        out=[]
        for c in [False,True]:
            u,wr,rd,desc,blocks=setup(c);q=syms['queue'] if c else 0x20086000
            first=blocks+16;second=blocks+32
            wr(q,first if length else 0);wr(q+4,second if length==2 else first if length==1 else 0)
            wr(first,second if length==2 else 0);wr(second,0)
            u.reg_write(UC_ARM_REG_R0,q)
            u.emu_start((syms['audio_wsf_queue_dequeue'] if c else 0x538c4a)|1,0x600000,count=1000)
            p=u.reg_read(UC_ARM_REG_R0)
            out.append((p-blocks if p else None,rd(q)-blocks if rd(q) else None,rd(q+4)-blocks if rd(q+4) else None))
        assert out[0]==out[1],(length,out)
        print('PASS WSF dequeue',length)
