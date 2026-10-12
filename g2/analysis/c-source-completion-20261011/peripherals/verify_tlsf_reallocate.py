"""Actual compiled ARM C/native 0x4d0868 realloc branch/call contracts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/tlsf_reallocate.c'
SHIM='''#include <stdint.h>
#include <stddef.h>
void *g2_file_pool_allocate(void*a,uint32_t b){(void)a;(void)b;return 0;}
void g2_file_pool_free(void*a,void*b){(void)a;(void)b;}
void *g2_tlsf_block_from_ptr(void*a){return a;}
void *g2_tlsf_block_next(void*a){return a;}
uint32_t g2_tlsf_block_size(void*a){(void)a;return 0;}
int32_t g2_tlsf_block_is_free(void*a){(void)a;return 0;}
uint32_t g2_tlsf_adjust_request(uint32_t a,uint32_t b){(void)b;return a;}
void *g2_tlsf_block_merge_next(void*a,void*b){(void)a;return b;}
void g2_tlsf_block_mark_used(void*a){(void)a;}
uint32_t g2_tlsf_block_can_split(void*a,uint32_t b){(void)a;(void)b;return 0;}
void *g2_tlsf_block_split(void*a,uint32_t b){(void)b;return a;}
void g2_tlsf_block_insert(void*a,void*b){(void)a;(void)b;}
void g2_file_close_error(const char*a,const char*b,uint32_t c){(void)a;(void)b;(void)c;}
void *memcpy(void*a,const void*b,size_t c){(void)b;(void)c;return a;}
void __aeabi_memcpy(void*a,const void*b,size_t c){(void)a;(void)b;(void)c;}
'''
NATIVE={'alloc':0x4d0722,'free':0x4d0808,'from':0x4cfe04,'next':0x4cfe44,
        'size':0x4cfd70,'isfree':0x4cfdb4,'adjust':0x4cff42,'merge':0x4d033a,
        'mark':0x4cfeac,'trim':0x4d03f0,'copy':0x439be4,'error':0x4d09b4}
NAMES={'alloc':'g2_file_pool_allocate','free':'g2_file_pool_free',
       'from':'g2_tlsf_block_from_ptr','next':'g2_tlsf_block_next',
       'size':'g2_tlsf_block_size','isfree':'g2_tlsf_block_is_free',
       'adjust':'g2_tlsf_adjust_request','merge':'g2_tlsf_block_merge_next',
       'mark':'g2_tlsf_block_mark_used','trim':'g2_tlsf_block_trim_used',
       'copy':'__aeabi_memcpy','error':'g2_file_close_error'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,g2_tlsf_reallocate_4d0868',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[('null',0,8,8,0,1),('zero',0x20001000,0,8,0,1),
           ('shrink',0x20001000,8,8,0,1),('grow_fit',0x20001000,24,24,1,1),
           ('grow_used',0x20001000,24,24,0,1),('grow_large',0x20001000,48,48,1,1),
           ('alloc_fail',0x20001000,24,24,0,0)]
    for label,pointer,bytes_,requested,next_free,alloc_ok in cases:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),
                           (0x20005000,pointer,bytes_)):u.reg_write(r,v)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
                calls.append((n,regs if n not in ('error',) else (regs[2],)))
                ret={'alloc':0x20003000 if alloc_ok else 0,'from':0x20002000,
                     'next':0x20002100,'size':16 if regs[0]==0x20002000 else 16,
                     'isfree':next_free if regs[0]==0x20002100 else 0,
                     'adjust':requested,'merge':regs[1],'copy':regs[0],
                     'trim':0,'error':0}.get(n,0)
                uc.reg_write(UC_ARM_REG_R0,ret)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['g2_tlsf_reallocate_4d0868'] if is_c else 0x4d0868
            u.emu_start(start|1,0x600000,count=350)
            traces.append((u.reg_read(UC_ARM_REG_R0),calls))
        assert traces[0]==traces[1],(label,traces)
    print('PASS',len(cases),'compiled-C/native TLSF realloc branch/call cases')
