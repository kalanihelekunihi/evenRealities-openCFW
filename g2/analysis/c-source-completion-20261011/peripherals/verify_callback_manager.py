"""Actual compiled C/native callback manager valid and failure paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t alloc;volatile uint32_t calls[2];
void *codec_allocate(uint32_t n){calls[0]++;calls[1]=n;return (void *)alloc;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_callback_mgr_register',str(ROOT/'components/audio/uart_thread_source_candidate/display_callback_manager.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,manager,callback,alloc,existing,init=False):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda address,value:u.mem_write(address,struct.pack('<I',value))
        mgr=0x20071000 if manager else 0
        wr(symbols['alloc'],alloc)
        u.mem_write(0x20071000,struct.pack('<III',0x20072000 if existing else 0,1 if existing else 0,0x20073000))
        u.mem_write(0x20072000,struct.pack('<II',callback if existing else 0,0))
        u.mem_write(0x20074000,b'\xaa'*8)
        u.reg_write(UC_ARM_REG_R0,mgr);u.reg_write(UC_ARM_REG_R1,callback)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                if address==0x43d0ce:result=0
                elif address==0x474cd2:
                    calls=symbols['calls'];count=struct.unpack('<I',uc.mem_read(calls,4))[0]
                    uc.mem_write(calls,struct.pack('<II',count+1,uc.reg_read(UC_ARM_REG_R0)))
                    result=alloc
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        entry=(symbols['audio_callback_mgr_init'] if candidate else 0x510108) if init else (symbols['audio_callback_mgr_register'] if candidate else 0x510240)
        u.emu_start(entry|1,0x600000,count=2000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20071000,12)),bytes(u.mem_read(0x20074000,8)),bytes(u.mem_read(symbols['calls'],8))
    cases=[(0,0x100101,0x20074000,0),(1,0,0x20074000,0),(1,0x100101,0,0),
           (1,0x100101,0x20074000,0),(1,0x100101,0x20074000,1)]
    for case in cases:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS callback manager',case)
    for case in [(0,0x20073000,0,0),(1,0x20073000,0,1)]:
        native=run(False,*case,init=True);compiled=run(True,*case,init=True)
        assert native==compiled,(case,native,compiled)
        print('PASS callback manager init',case)
