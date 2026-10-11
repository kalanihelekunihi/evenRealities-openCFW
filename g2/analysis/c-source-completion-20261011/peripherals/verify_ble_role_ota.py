"""Compiled C/native OTA and local BLE role predicates, log-disabled."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t object[64];uint8_t *audio_ble_slave_connection_info=object;
volatile uint8_t audio_ota_transfer_flag;
volatile uint32_t role_value,self_value,peer_value;
uint8_t audio_uart_device_role_get(void){return (uint8_t)role_value;}
uint32_t audio_ota_self_status(void){return self_value;}
uint32_t audio_ota_peer_status(void){return peer_value;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ota_transfer_active',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_role_ota.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    pairs=[('audio_ota_transfer_active',0x4487ac),('audio_app_is_left_slave_role',0x46f258),('audio_app_is_local_slave_cmd_role',0x46f1d0)]
    def run(c,name,addr,role,pipe,self_status,peer_status,flag):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        for n,v in [('role_value',role),('self_value',self_status),('peer_value',peer_status)]:wr(syms[n],v)
        u.mem_write(syms['object']+31,bytes([pipe]));u.mem_write(syms['audio_ota_transfer_flag'],bytes([flag]))
        wr(0x20074330,0x20083000);u.mem_write(0x2008301f,bytes([pipe]));u.mem_write(0x20072730,bytes([flag]))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                result={0x43d0ce:0,0x45a568:role,0x47d8b8:self_status,0x47d8c2:peer_status}.get(a)
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms[name] if c else addr)|1,0x600000,count=3000)
        return u.reg_read(UC_ARM_REG_R0)
    for name,addr in pairs:
        for role,pipe,self_status,peer_status,flag in [(1,0,0,0,0),(1,1,0,0,1),(2,0,0,0,0),(2,1,1,0,0),(3,0,0,1,0)]:
            case=(role,pipe,self_status,peer_status,flag)
            a=run(False,name,addr,*case);b=run(True,name,addr,*case)
            assert a==b,(name,case,a,b)
        print('PASS BLE predicate',name,'5/5')
