"""Bounded actual C/native HUB resource and timer callback comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
void *audio_hub_send_queue,*audio_hub_timer_handle;
uint8_t audio_hub_timer_control_block[44],audio_hub_timeout_message_template[8];
uint32_t queue_result,timer_result;
void *audio_queue_new(uint32_t n,uint32_t size,const void *a){(void)n;(void)size;(void)a;return (void *)queue_result;}
void *audio_uart_timer_new(void (*cb)(void *),uint32_t type,void *arg,const void *attr){(void)cb;(void)type;(void)arg;(void)attr;return (void *)timer_result;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
const void *audio_hub_send_message(const void *p){const uint8_t *s=p;volatile uint8_t *d=(volatile uint8_t *)0x20090000u;for(unsigned i=0;i<8;i++)d[i]=s[i];return p;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_hub_resource_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_hub_resource_init.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_hub_timer_callback.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,kind,queue,timer,oldtimer):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for address,data in segments:u.mem_write(address,data)
        u.mem_map(0x20000000,0x100000)
        write=lambda address,value:u.mem_write(address,struct.pack('<I',value))
        write(0x20003670,0);write(0x20074908,oldtimer)
        write(symbols['audio_hub_send_queue'],0);write(symbols['audio_hub_timer_handle'],oldtimer)
        write(symbols['queue_result'],queue);write(symbols['timer_result'],timer)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                if address==0x449a32:result=queue
                elif address==0x4493b0:result=timer
                elif address==0x43d0ce:result=0
                elif address==0x4a6a1a:
                    uc.mem_write(0x20090000,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),8)))
                    result=uc.reg_read(UC_ARM_REG_R0)
                else:return
                uc.reg_write(UC_ARM_REG_R0,result)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        entry=(symbols['audio_hub_resource_init'] if candidate else 0x4a66ee) if kind=='init' else (symbols['audio_hub_timer_callback'] if candidate else 0x4a696c)
        u.emu_start(entry|1,0x600000,count=1000)
        if kind=='callback':return bytes(u.mem_read(0x20090000,8))
        base=symbols['audio_hub_send_queue'] if candidate else 0x20003670
        tbase=symbols['audio_hub_timer_handle'] if candidate else 0x20074908
        return bytes(u.mem_read(base,4)),bytes(u.mem_read(tbase,4))
    cases=[('init',0,0,0),('init',0x20060000,0,0),('init',0x20060000,0x20060100,0),('init',0x20060000,0x20060100,0x20060200),('callback',0,0,0)]
    for case in cases:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS',case)
