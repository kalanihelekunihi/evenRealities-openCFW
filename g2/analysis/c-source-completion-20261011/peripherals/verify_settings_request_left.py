"""Actual C/native left-version request rate limit and transport outcomes."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[80];uint32_t audio_settings_left_version_last_request_tick,role,tick,send_result;
volatile uint32_t calls[2];
uint8_t audio_uart_device_role_get(void){return (uint8_t)role;}
uint32_t g2_flashdb_candidate_tick(void){return tick;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
int32_t audio_settings_send_peer_packet(uint16_t a,const void *p,uint32_t n,uint32_t x,uint32_t type){(void)a;(void)n;(void)x;(void)type;calls[0]++;calls[1]=*(const uint8_t *)p;return (int32_t)send_result;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_request_left_version',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_request_left_version.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,role,left,prior,now,status):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v&0xffffffff))
        conf=bytearray(80);conf[0x44]=left
        u.mem_write(0x20072da8,bytes(conf));u.mem_write(symbols['audio_settings_config_live'],bytes(conf))
        u.mem_write(0x20075024,bytes([role]))
        for name,value in [('audio_settings_left_version_last_request_tick',prior),('role',role),('tick',now),('send_result',status)]:wr(symbols[name],value)
        wr(0x20074994,prior)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                calls=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(calls+4*i,4))[0];put=lambda i,v:wr(calls+4*i,v)
                if address==0x4490cc:result=now
                elif address==0x43d0ce:result=0
                elif address==0x43c0e4:
                    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(r0,b'\0'*r1);result=r0
                elif address==0x465480:
                    put(0,read(0)+1);put(1,uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1)[0]);result=status&0xffffffff
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_request_left_version'] if candidate else 0x46ba02)|1,0x600000,count=1500)
        return bytes(u.mem_read(symbols['audio_settings_left_version_last_request_tick'] if candidate else 0x20074994,4)),bytes(u.mem_read(symbols['calls'],8))
    cases=[(2,0,0,1000,0),(1,1,0,1000,0),(1,0,900,1000,0),(1,0,500,1000,0),
           (1,0,0,1000,-1),(1,0,0,1000,0),(1,0,0xffffff00,300,0)]
    for case in cases:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS left version',case)
