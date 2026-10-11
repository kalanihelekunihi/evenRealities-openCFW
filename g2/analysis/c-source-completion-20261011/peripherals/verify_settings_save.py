"""Actual compiled C/native CRC and event-save paths at 0x46be7c."""
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
uint8_t audio_settings_config_live[26];uint8_t *audio_settings_config_previous;
uint32_t g2_audio_log_event_handle,flags;
uint32_t audio_log_flags(void){return flags;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_log_event_set_task(uint32_t handle,uint32_t mask){volatile uint32_t *out=(volatile uint32_t *)0x20090000u;out[0]++;out[1]=handle;out[2]=mask;return mask;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SVC_Settings_SaveSettingConfigToKVCheck',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_save_config.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,changed,event):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        live=bytes(range(24))+b'\0\0';old=bytearray(live);old[24:26]=b'\x12\x34' if changed else b'\xff\x5c'
        # Compute the actual original CRC so the equal case uses a native value.
        crc=0xffff;table=0x6c0b50-0x438000
        for x in live[:24]:crc=(int.from_bytes(BLOB[table+2*(x^(crc>>8)):table+2*(x^(crc>>8))+2],'little')^(crc<<8))&0xffff
        if not changed:old[24:26]=struct.pack('<H',crc)
        u.mem_write(0x20072da8,live);u.mem_write(symbols['audio_settings_config_live'],live)
        u.mem_write(0x20080000,bytes(old))
        u.mem_write(0x20003700,struct.pack('<I',0x20080000));u.mem_write(symbols['audio_settings_config_previous'],struct.pack('<I',0x20080000))
        u.mem_write(0x20074570,struct.pack('<I',event));u.mem_write(symbols['g2_audio_log_event_handle'],struct.pack('<I',event))
        u.mem_write(0x20004543,b'\0');u.mem_write(symbols['flags'],b'\0\0\0\0')
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,addr,size,_):
                if addr==0x43d0ce:result=0
                elif addr==0x4495e4:
                    out=struct.unpack('<I',uc.mem_read(0x20090000,4))[0]+1
                    uc.mem_write(0x20090000,struct.pack('<III',out,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
                    result=uc.reg_read(UC_ARM_REG_R1)
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['SVC_Settings_SaveSettingConfigToKVCheck'] if candidate else 0x46be7c)|1,0x600000,count=2000)
        return bytes(u.mem_read(symbols['audio_settings_config_live'] if candidate else 0x20072da8,26)),bytes(u.mem_read(0x20090000,12))
    for changed,event in [(False,0),(True,0),(True,0x20060100)]:
        native=run(False,changed,event);compiled=run(True,changed,event)
        assert native==compiled,((changed,event),native,compiled)
        print('PASS settings save',changed,hex(event))
