"""Actual compiled ARM C/native 0x48f12c transport branch/call effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_thread_msg_rx_ble.c'
SHIM='''#include <stdint.h>
#include <stddef.h>
uint8_t audio_ble_rx_thread_state[16];
void *file_heap_allocate(uint32_t n){(void)n;return 0;}
void audio_file_heap_free(void*p){(void)p;}
void *memset(void*p,int c,size_t n){(void)c;(void)n;return p;}
void *memcpy(void*p,const void*q,size_t n){(void)q;(void)n;return p;}
uint32_t audio_cmsis_queue_get_count(void*p){(void)p;return 0;}
uint32_t audio_cmsis_queue_get_capacity(const void*p){(void)p;return 0;}
int32_t audio_cmsis_queue_put(void*p,const void*q,uint8_t r,uint32_t t)
{(void)p;(void)q;(void)r;(void)t;return 0;}
uint32_t audio_thread_flags_set(void*p,uint32_t f){(void)p;(void)f;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}'''
NATIVE={'alloc':0x474cd2,'free':0x474d16,'zero':0x43c0e4,'copy':0x439be4,
        'count':0x449bc8,'capacity':0x449bbc,'put':0x449abe,'flags_set':0x449238,
        'log_flags':0x43d0ce}
NAMES={'alloc':'file_heap_allocate','free':'audio_file_heap_free','zero':'memset','copy':'memcpy',
       'count':'audio_cmsis_queue_get_count','capacity':'audio_cmsis_queue_get_capacity',
       'put':'audio_cmsis_queue_put','flags_set':'audio_thread_flags_set','log_flags':'audio_log_flags'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_thread_msg_rx_from_ble_48f12c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for scenario in ('null','no_queue','alloc_fail','success','put_fail'):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            manager=syms['audio_ble_rx_thread_state'] if is_c else 0x20003ffc
            queue=0 if scenario=='no_queue' else 0x20003000
            u.mem_write(manager+8,struct.pack('<II',0x20004000,queue))
            u.mem_write(0x20005000,b'ABCD');u.mem_write(0x20002000,b'\xa5'*32)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,0x400);u.reg_write(UC_ARM_REG_R1,0 if scenario=='null' else 0x20005000)
            u.reg_write(UC_ARM_REG_R2,4)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                r2=uc.reg_read(UC_ARM_REG_R2)
                if n=='log_flags':uc.reg_write(UC_ARM_REG_R0,0)
                elif n=='alloc':
                    calls.append((n,r0));uc.reg_write(UC_ARM_REG_R0,0 if scenario=='alloc_fail' else 0x20002000)
                elif n=='zero':
                    length=r2 if is_c else r1
                    calls.append((n,r0,length));uc.mem_write(r0,b'\x00'*length);uc.reg_write(UC_ARM_REG_R0,r0)
                elif n=='copy':
                    calls.append((n,r0,r1,r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
                elif n=='put':
                    calls.append((n,r0,struct.unpack('<I',uc.mem_read(r1,4))[0],uc.reg_read(UC_ARM_REG_R3)))
                    uc.reg_write(UC_ARM_REG_R0,1 if scenario=='put_fail' else 0)
                else:
                    calls.append((n,r0,r1 if n=='flags_set' else None))
                    uc.reg_write(UC_ARM_REG_R0,2 if n=='count' else 8 if n=='capacity' else 0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_uart_thread_msg_rx_from_ble_48f12c'] if is_c else 0x48f12c
            u.emu_start(start|1,0x600000,count=420)
            traces.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20002000,16))))
        assert traces[0]==traces[1],(scenario,traces)
    print('PASS 5 compiled-C/native BLE receive transport cases')
