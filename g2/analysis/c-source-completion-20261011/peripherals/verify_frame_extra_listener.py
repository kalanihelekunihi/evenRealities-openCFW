"""Actual compiled ARM C/native 0x4918c2 insertion and full-table diagnostics."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/frame_extra_listener.c'
SHIM='''#include <stdint.h>
volatile uint8_t flags;
uint32_t audio_log_flags(void){return flags;}
void audio_log_extended(uint32_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_frame_extra',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for free in (0,1,64,127,128):
        for flags in ((0,1,2,3,4,5,6,7) if free==128 else (0,)):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                state=0x20010000;frame=0x20020000
                u.mem_write(state,b'\x00'*0x7200)
                u.mem_write(frame,bytes(range(24)))
                for slot in range(free):u.mem_write(state+0x6434+slot*24,struct.pack('<I',0xdead0000+slot))
                u.mem_write(0x20004543,bytes([flags]))
                if is_c:u.mem_write(syms['flags'],bytes([flags]))
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                               (state,frame,0x12345678,0x87654321)):u.reg_write(r,v)
                u.mem_write(0x200ff000,struct.pack('<I',0x3456))
                logs=[]
                calls=({0x43d574:'extended',0x43ce9e:'compact'} if not is_c else
                       {syms['audio_log_extended']&~1:'extended',
                        syms['compressed_log_output']&~1:'compact'})
                def string(uc,p):return bytes(uc.mem_read(p,120)).split(b'\0',1)[0]
                def hook(uc,a,size,_):
                    if a not in calls:return
                    kind=calls[a]
                    if kind=='extended':
                        sp=uc.reg_read(UC_ARM_REG_SP)
                        logs.append((kind,uc.reg_read(UC_ARM_REG_R0),
                           *(string(uc,uc.reg_read(r)) for r in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)),
                           struct.unpack('<I',uc.mem_read(sp,4))[0],
                           string(uc,struct.unpack('<I',uc.mem_read(sp+4,4))[0])))
                    else:logs.append((kind,uc.reg_read(UC_ARM_REG_R0),
                        string(uc,uc.reg_read(UC_ARM_REG_R1)),string(uc,uc.reg_read(UC_ARM_REG_R2))))
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
                start=syms['audio_uart_frame_extra'] if is_c else 0x4918c2
                u.emu_start(start|1,0x600000,count=2000)
                region=bytes(u.mem_read(state+0x6430,128*24))+bytes(u.mem_read(state+0x7158,1))
                traces.append((u.reg_read(UC_ARM_REG_R0),region,logs))
            assert traces[0]==traces[1],(free,flags,traces[0][0],traces[1][0],traces[0][2],traces[1][2])
    print('PASS 12 compiled-C/native listener insert/full-table diagnostic cases')
