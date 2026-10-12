"""Actual compiled ARM C/native 0x4d03f0 trim, error and flag effects."""
from pathlib import Path
import struct,subprocess,tempfile
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
void __aeabi_memcpy(void*a,const void*b,size_t c){(void)a;(void)b;(void)c;}
'''
NATIVE={'isfree':0x4cfdb4,'can':0x4d01bc,'split':0x4d01d4,
        'merge':0x4d033a,'insert':0x4d019a,'error':0x4d09b4}
NAMES={'isfree':'g2_tlsf_block_is_free','can':'g2_tlsf_block_can_split',
       'split':'g2_tlsf_block_split','merge':'g2_tlsf_block_merge_next',
       'insert':'g2_tlsf_block_insert','error':'g2_file_close_error'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,g2_tlsf_block_trim_used',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for is_free in (0,1):
        for can_split in (0,1):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                u.mem_write(0x20002104,struct.pack('<I',0x1234567a))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),
                               (0x20005000,0x20002000,24)):u.reg_write(r,v)
                mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
                calls=[]
                def hook(uc,a,size,_):
                    if a not in mapping:return
                    n=mapping[a];r=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
                    if n=='error':
                        msg=bytes(uc.mem_read(r[0],100)).split(b'\0',1)[0]
                        calls.append((n,msg,r[2]))
                    else:calls.append((n,r[:2]))
                    ret={'isfree':is_free,'can':can_split,'split':0x20002100,'merge':0x20002200}.get(n,0)
                    uc.reg_write(UC_ARM_REG_R0,ret)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                start=syms['g2_tlsf_block_trim_used'] if is_c else 0x4d03f0
                u.emu_start(start|1,0x600000,count=180)
                traces.append((calls,bytes(u.mem_read(0x20002104,4))))
            assert traces[0]==traces[1],(is_free,can_split,traces)
    print('PASS 4 compiled-C/native TLSF used-block trim/error cases')
