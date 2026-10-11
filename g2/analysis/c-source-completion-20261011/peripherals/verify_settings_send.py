"""Actual compiled C/native settings display and peer packet paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[80];const uint8_t audio_settings_version_text[9]="2.2.6.10";
uint32_t role,audio_settings_display_brightness_cell,audio_settings_display_profile_cell;volatile uint32_t calls[4];
uint8_t audio_uart_device_role_get(void){return (uint8_t)role;}
uint32_t audio_settings_device_role(void){return role;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
void audio_uart_checksum_copy(void *p,const void *s,uint32_t n){volatile uint8_t *d=p;const volatile uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];}
void audio_settings_send_peer_packet(uint32_t cmd,const void *p,uint32_t n,uint32_t x,uint32_t type){(void)x;calls[0]++;calls[1]=cmd;calls[2]=n;calls[3]=type;const uint8_t *s=p;volatile uint8_t *d=(volatile uint8_t *)0x20090000u;for(unsigned i=0;i<48;i++)d[i]=s[i];}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_send_config_to_peer',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_apply_send.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_level_tables.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_copy_text.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,kind,role,level=8,index=9):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,payload in segments:u.mem_write(addr,payload)
        u.mem_map(0x20000000,0x100000)
        live=bytearray(range(80));live[8]=level;live[9]=index
        u.mem_write(0x20072da8,bytes(live));u.mem_write(symbols['audio_settings_config_live'],bytes(live))
        u.mem_write(symbols['role'],struct.pack('<I',role))
        u.mem_write(0x20075024,bytes([role]))
        for name,address in [('audio_settings_display_brightness_cell',0x2000064c),('audio_settings_display_profile_cell',0x20000648)]:
            u.mem_write(symbols[name],struct.pack('<I',999));u.mem_write(address,struct.pack('<I',999))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
                out=symbols['calls'];get=lambda i:struct.unpack('<I',uc.mem_read(out+4*i,4))[0];put=lambda i,v:uc.mem_write(out+4*i,struct.pack('<I',v))
                if address==0x45a568:result=role
                elif address==0x43c0e4:uc.mem_write(r0,bytes([r2&255])*r1);result=r0
                elif address==0x439c04:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));result=r0
                elif address==0x465480:
                    uc.mem_write(0x20090000,bytes(uc.mem_read(r1,48)))
                    put(0,get(0)+1);put(1,r0);put(2,r2);put(3,struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]);result=0
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        n={'send':'audio_settings_send_config_to_peer','apply':'audio_settings_apply_display_levels'}
        a={'send':0x46b930,'apply':0x46b912}
        u.emu_start((symbols[n[kind]] if candidate else a[kind])|1,0x600000,count=1000)
        cells=tuple(bytes(u.mem_read(symbols[name] if candidate else address,4)) for name,address in [('audio_settings_display_brightness_cell',0x2000064c),('audio_settings_display_profile_cell',0x20000648)])
        return bytes(u.mem_read(0x20090000,48)),bytes(u.mem_read(symbols['calls'],16)),cells
    for case in [('apply',1,0,0),('apply',2,12,1),('apply',1,13,2),('apply',2,8,9),('send',1,8,9),('send',2,8,9)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS settings send/apply',case)
