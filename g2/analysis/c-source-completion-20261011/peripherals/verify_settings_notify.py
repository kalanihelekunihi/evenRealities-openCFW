"""Actual C/native status notification role/build/success branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t role,build_result;volatile uint32_t calls[3];
uint8_t audio_uart_device_role_get(void){return (uint8_t)role;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
uint32_t audio_settings_build_full_status(uint8_t *p){calls[0]++;p[0]=42;p[103]=77;return build_result;}
uint32_t audio_settings_notify_common(uint8_t *p){calls[1]++;calls[2]=p[0]+p[103];return 17;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_notify_device_status',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_notify_status.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,role,build):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        wr(symbols['role'],role);wr(symbols['build_result'],build);u.mem_write(0x20075024,bytes([role]))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                calls=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(calls+i*4,4))[0];write=lambda i,v:wr(calls+i*4,v)
                if address==0x43d0ce:result=0
                elif address==0x48949c:uc.mem_write(uc.reg_read(UC_ARM_REG_R0),b'\0'*104);result=0
                elif address==0x49b4da:
                    p=uc.reg_read(UC_ARM_REG_R0);uc.mem_write(p,b'*');uc.mem_write(p+103,b'M');write(0,read(0)+1);result=build
                elif address==0x49bbfc:
                    p=uc.reg_read(UC_ARM_REG_R0);write(1,read(1)+1);write(2,sum([uc.mem_read(p,1)[0],uc.mem_read(p+103,1)[0]]));result=17
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_notify_device_status'] if candidate else 0x49be04)|1,0x600000,count=1000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(symbols['calls'],12))
    for case in [(2,1),(1,0),(1,1)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS notify status',case)
