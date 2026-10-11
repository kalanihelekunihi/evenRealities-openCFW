"""Compiled C versus native 0x475c1a across four live control paths."""
from pathlib import Path
import subprocess, tempfile, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
volatile uint32_t ota_value,left_value,cmd_value,calls,args[6];
uint32_t audio_ota_transfer_active(void){return ota_value;}
uint32_t audio_app_is_left_slave_role(void){return left_value;}
uint32_t audio_app_is_local_slave_cmd_role(void){return cmd_value;}
uint32_t audio_ble_msg_tx(uint8_t a,uint8_t b,uint8_t c,uint8_t d,const void *p,uint16_t n){calls++;args[0]=a;args[1]=b;args[2]=c;args[3]=d;args[4]=(uint32_t)p;args[5]=n;return 27;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_notify_ble',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_notify_ble.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f: segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,ota,left,cmd):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for a,data in segments:u.mem_write(a,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        for name,value in [('ota_value',ota),('left_value',left),('cmd_value',cmd)]:wr(symbols[name],value)
        u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,9);u.reg_write(UC_ARM_REG_R2,0x20081000);u.reg_write(UC_ARM_REG_R3,17)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not candidate:
            def cut(uc,address,size,_):
                result=None
                if address==0x4487ac:result=ota
                elif address==0x46f258:result=left
                elif address==0x46f1d0:result=cmd
                elif address==0x43d0ce:result=0
                elif address==0x47564e:
                    wr(symbols['calls'],1)
                    for i,r in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]):wr(symbols['args']+4*i,uc.reg_read(r))
                    sp=uc.reg_read(UC_ARM_REG_SP)
                    for i in range(2):wr(symbols['args']+4*(i+4),struct.unpack('<I',uc.mem_read(sp+4*i,4))[0])
                    result=27
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_notify_ble'] if candidate else 0x475c1a)|1,0x600000,count=3000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(symbols['calls'],28))
    for case in [(1,0,0),(0,1,0),(0,0,0),(0,0,1)]:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a,b)
        print('PASS notify BLE',case)
