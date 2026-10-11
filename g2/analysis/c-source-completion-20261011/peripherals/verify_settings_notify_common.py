"""Actual C/native notify-common staging, sequence, encode, and BLE branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_notify_staging[104],audio_settings_notify_encode_buffer[256];
uint32_t audio_settings_notify_magic,role,encode_result;const uint8_t audio_settings_status_pb_descriptor[8]={0};
volatile uint32_t calls[4];
uint8_t audio_uart_device_role_get(void){return (uint8_t)role;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
void audio_uart_checksum_copy(void *p,const void *s,uint32_t n){volatile uint8_t *d=p;const volatile uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];}
void *audio_queue_copy_bytes(void *p,const void *s,uint32_t n){volatile uint8_t *d=p;const volatile uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];return p;}
uint32_t audio_pb_encode(uint32_t *s,const void *desc,const void *packet){(void)desc;(void)packet;calls[0]++;s[3]=17;return encode_result;}
uint32_t audio_settings_notify_ble(uint32_t t,uint32_t service,const void *buf,uint32_t n){(void)t;(void)service;(void)buf;calls[1]++;calls[2]=n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_notify_common',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_notify_common.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_pb_ostream_buffer.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,role,nonnull,encoded):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        wr(symbols['role'],role);wr(symbols['encode_result'],encoded);u.mem_write(0x20075024,bytes([role]))
        u.mem_write(0x200725a0,b'\xaa'*104);u.mem_write(symbols['audio_settings_notify_staging'],b'\xaa'*104)
        wr(0x2007486c,9);wr(symbols['audio_settings_notify_magic'],9)
        u.mem_write(0x20081000,bytes(range(104)))
        u.reg_write(UC_ARM_REG_R0,0x20081000 if nonnull else 0)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                calls=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(calls+4*i,4))[0];put=lambda i,v:wr(calls+4*i,v)
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
                if address==0x43d0ce:result=0
                elif address==0x490c32:
                    put(0,read(0)+1);wr(r0+12,17);result=encoded
                elif address==0x475c1a:
                    put(1,read(1)+1);put(2,uc.reg_read(UC_ARM_REG_R3));result=0
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_notify_common'] if candidate else 0x49bbfc)|1,0x600000,count=6000)
        cell=lambda name,addr,n:bytes(u.mem_read(symbols[name] if candidate else addr,n))
        return u.reg_read(UC_ARM_REG_R0),cell('audio_settings_notify_staging',0x200725a0,104),cell('audio_settings_notify_magic',0x2007486c,4),bytes(u.mem_read(symbols['calls'],12))
    for case in [(2,True,1),(1,False,1),(1,True,0),(1,True,1)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS notify common',case)
