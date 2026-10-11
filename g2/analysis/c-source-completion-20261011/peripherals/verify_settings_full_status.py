"""Actual C/native 104-byte settings status packet and error branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[80],audio_settings_last_message_state[16];
const uint8_t audio_settings_right_version_text[11]="2.2.6.10";
volatile uint32_t calls[2];
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
void audio_settings_request_left_version(void){calls[0]++;}
uint32_t audio_settings_unread_message_count(void){calls[1]++;return 7;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_build_full_status',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_full_status.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_copy_text.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,nonnull,left_present,match_type):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        conf=bytearray(range(80));conf[0x44:0x4f]=b'LEFT.1.2\0\0\0' if left_present else b'\0'*11
        u.mem_write(0x20072da8,bytes(conf));u.mem_write(symbols['audio_settings_config_live'],bytes(conf))
        state=bytearray(16);state[8:10]=struct.pack('<H',4 if match_type else 3);state[12]=33
        u.mem_write(0x20072608,bytes(state));u.mem_write(symbols['audio_settings_last_message_state'],bytes(state))
        u.mem_write(0x20081000,b'\xaa'*104)
        u.reg_write(UC_ARM_REG_R0,0x20081000 if nonnull else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                calls=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(calls+4*i,4))[0];put=lambda i,v:uc.mem_write(calls+4*i,struct.pack('<I',v))
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
                if address==0x43d0ce:result=0
                elif address==0x43c0e4:uc.mem_write(r0,bytes([r2&255])*r1);result=r0
                elif address==0x46ba02:put(0,read(0)+1);result=0
                elif address==0x4974d4:put(1,read(1)+1);result=7
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_build_full_status'] if candidate else 0x49b4da)|1,0x600000,count=5000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20081000,104)),bytes(u.mem_read(symbols['calls'],8))
    for case in [(False,False,False),(True,False,False),(True,True,False),(True,True,True)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS full status',case)
