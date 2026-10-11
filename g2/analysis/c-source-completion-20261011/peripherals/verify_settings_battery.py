"""Bounded actual C/native Settings battery callback branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_settings_config_live[80],audio_charger_state[32];volatile uint32_t calls[3];
void audio_settings_notify_device_status(void){calls[2]++;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SVC_Settings_BatteryCallback',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_battery_callback.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_charge_state.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,event,data):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,payload in segments:u.mem_write(addr,payload)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(0x20072da8,b'\x55'*80);u.mem_write(symbols['audio_settings_config_live'],b'\x55'*80)
        charger=bytearray(32);charger[16:20]=struct.pack('<I',87);charger[20]=255
        u.mem_write(0x20073b30,bytes(charger));u.mem_write(symbols['audio_charger_state'],bytes(charger))
        u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,0x20081000 if data else 0)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                out=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(out+i*4,4))[0];write=lambda i,v:uc.mem_write(out+i*4,struct.pack('<I',v))
                if address==0x43d0ce:result=0
                elif address==0x49be04:write(2,read(2)+1);result=0
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['SVC_Settings_BatteryCallback'] if candidate else 0x46b3e4)|1,0x600000,count=500)
        return bytes(u.mem_read(symbols['audio_settings_config_live'] if candidate else 0x20072da8,80)),bytes(u.mem_read(symbols['calls'],12))
    for case in [(0,0),(0,1),(1,1),(2,1)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS Settings_BatteryCallback',case)
