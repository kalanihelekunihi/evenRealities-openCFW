"""Actual compiled-C/native DM, L2CAP, SMP and HCI init state/calls."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
cases=[('DmHandlerInit',0x4d2a46,'audio_ble_dm_handler_state',0x20073b78,0x18),('L2cSlaveHandlerInit',0x536f6a,'audio_ble_l2c_slave_state',0x20073bd8,0x14),('SmpHandlerInit',0x537cb2,'audio_ble_smp_handler_state',0x20070aec,0xf0),('HciSetMaxRxAclLen',0x52acce,'audio_ble_hci_state',0x20071478,0x80)]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_ble_dm_handler_lower_5367e4(void (*x)(void)){(void)x;}
void audio_ble_dm_handler_4d299c(void){}
void SmpDbInit(void){}
void L2cRegister(uint8_t a,void (*b)(void),void (*c)(void)){(void)a;(void)b;(void)c;}
void DmConnRegister(uint8_t a,void (*b)(void)){(void)a;(void)b;}
void audio_ble_smp_l2c_data_callback_537278(void){}
void audio_ble_smp_l2c_control_callback_537444(void){}
void audio_ble_smp_dm_conn_callback_537502(void){}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmHandlerInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_stack_handler_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 child={'audio_ble_dm_handler_lower_5367e4':0x5367e4,'SmpDbInit':0x542288,'L2cRegister':0x530b5e,'DmConnRegister':0x4b6c64}
 callbacks={'audio_ble_dm_handler_4d299c':0x4d299d,'audio_ble_smp_l2c_data_callback_537278':0x537279,'audio_ble_smp_l2c_control_callback_537444':0x537445,'audio_ble_smp_dm_conn_callback_537502':0x537503}
 canon={syms[k]&~1:v for k,v in callbacks.items()}
 for name,native,state,stock,size in cases:
  for value in [3,47]:
   out=[]
   for c in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_map(0x20000000,0x100000);a=syms[state] if c else stock;u.mem_write(a,b'\xaa'*size);events=[]
    targets={syms[k]&~1:v for k,v in child.items()} if c else {v:v for v in child.values()}
    def hook(uc,pc,n,_):
     if pc not in targets:return
     dest=targets[pc];regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
     for i,x in enumerate(regs):regs[i]=canon.get(x&~1,x) if c else x
     if dest==0x5367e4:args=regs[:1]
     elif dest==0x530b5e:args=regs[:3]
     elif dest==0x4b6c64:args=regs[:2]
     else:args=[]
     events.append((dest,args));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value)
    u.emu_start((syms[name] if c else native)|1,0x600000,count=3000)
    out.append((bytes(u.mem_read(a,size)),events))
   assert out[0]==out[1],(name,value,out)
   print('PASS BLE handler',name,value)
