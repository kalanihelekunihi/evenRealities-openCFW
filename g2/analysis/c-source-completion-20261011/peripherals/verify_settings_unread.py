"""Actual C/native protected ANCC count cases."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_settings_ancc_mutex;uint8_t audio_settings_ancc_count;uint32_t acquire_result;
volatile uint32_t calls[2];
int32_t audio_file_mutex_acquire(void *m,uint32_t t){(void)m;(void)t;calls[0]++;return (int32_t)acquire_result;}
int32_t audio_file_mutex_release(void *m){(void)m;calls[1]++;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_unread_message_count',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_unread_count.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,mutex,status,count):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        h=0x20081000 if mutex else 0
        wr(0x2007491c,h);wr(symbols['audio_settings_ancc_mutex'],h)
        u.mem_write(0x2007500d,bytes([count]));u.mem_write(symbols['audio_settings_ancc_count'],bytes([count]))
        wr(symbols['acquire_result'],status&0xffffffff)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                c=symbols['calls'];r=lambda i:struct.unpack('<I',uc.mem_read(c+4*i,4))[0];w=lambda i,v:wr(c+4*i,v)
                if address==0x43d0ce:result=0
                elif address==0x4497b6:w(0,r(0)+1);result=status&0xffffffff
                elif address==0x44981c:w(1,r(1)+1);result=0
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_unread_message_count'] if candidate else 0x4974d4)|1,0x600000,count=500)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(symbols['calls'],8))
    for case in [(0,0,9),(1,-1,9),(1,0,0),(1,0,255)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS unread count',case)
