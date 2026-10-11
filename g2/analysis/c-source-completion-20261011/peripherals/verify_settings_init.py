"""Bounded actual compiled C/native Settings_Init restore and call ordering."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[80];uint8_t *audio_settings_config_previous,*audio_settings_als_previous,*audio_settings_terminal_previous;
volatile uint32_t calls[8];
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
void *audio_queue_copy_bytes(void *p,const void *s,uint32_t n){uint8_t *d=p;const uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];return p;}
void audio_settings_apply_als(uint32_t v){calls[0]++;calls[1]=v;}
void SVC_Settings_DumpSettingConfig(void){calls[2]++;}
void SVC_Settings_BatteryCallback(uint32_t x,void *p){(void)x;(void)p;}
void audio_settings_register_battery_callback(void (*cb)(uint32_t,void *)){(void)cb;calls[3]++;}
void audio_settings_apply_display_levels(void){calls[4]++;}
void audio_settings_send_config_to_peer(void){calls[5]++;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SVC_Settings_Init',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_init.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        u.mem_write(0x20072da8,b'\xaa'*80);u.mem_write(symbols['audio_settings_config_live'],b'\xaa'*80)
        u.mem_write(0x20081000,bytes(range(28)))
        u.mem_write(0x20082000,b'\x31\x32\x33\x34')
        u.mem_write(0x20083000,bytes(range(12)))
        for cell,symbol,value in [(0x20003700,'audio_settings_config_previous',0x20081000),(0x20003714,'audio_settings_als_previous',0x20082000),(0x20003718,'audio_settings_terminal_previous',0x20083000)]:
            wr(cell,value);wr(symbols[symbol],value)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
                calls=symbols['calls'];inc=lambda i:wr(calls+i*4,struct.unpack('<I',uc.mem_read(calls+i*4,4))[0]+1)
                if address==0x43c0e4:uc.mem_write(r0,bytes([r2&255])*r1)
                elif address==0x439be4:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
                elif address==0x4ae8e8:inc(0);wr(calls+4,r0)
                elif address==0x46b458:inc(2)
                elif address==0x4aea56:inc(3)
                elif address==0x46b912:inc(4)
                elif address==0x46b930:inc(5)
                else:return
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['SVC_Settings_Init'] if candidate else 0x46be10)|1,0x600000,count=1000)
        return bytes(u.mem_read(symbols['audio_settings_config_live'] if candidate else 0x20072da8,80)),bytes(u.mem_read(symbols['calls'],24)),u.reg_read(UC_ARM_REG_R0)
    native=run(False);compiled=run(True)
    assert native==compiled,(native,compiled)
    print('PASS Settings_Init restore/calls')
