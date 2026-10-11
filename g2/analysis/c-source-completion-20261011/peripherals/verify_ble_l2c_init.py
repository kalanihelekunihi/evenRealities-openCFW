"""Actual compiled-C/native L2CAP init and registration table transitions."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callbacks={'audio_ble_l2c_default_data_530538':0x530539,'audio_ble_l2c_rx_signaling_53076e':0x53076f,'audio_ble_l2c_default_control_53076c':0x53076d,'audio_ble_l2c_default_cid_530640':0x530641,'audio_ble_l2c_hci_acl_5308e6':0x5308e7,'audio_ble_l2c_hci_flow_530aa4':0x530aa5,'audio_ble_l2c_slave_rx_536c5c':0x536c5d,'audio_ble_l2c_master_rx_536fbc':0x536fbd}
cases=[('L2cInit',0x530b34,0),('L2cRegister',0x530b5e,4),('L2cRegister',0x530b5e,6),('L2cSlaveInit',0x536e78,0),('L2cMasterInit',0x537200,0)]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_l2c_slave_state[24];
void audio_ble_l2c_default_data_530538(void){}void audio_ble_l2c_rx_signaling_53076e(void){}void audio_ble_l2c_default_control_53076c(void){}
void audio_ble_l2c_default_cid_530640(void){}void audio_ble_l2c_hci_acl_5308e6(void){}void audio_ble_l2c_hci_flow_530aa4(void){}
void audio_ble_l2c_slave_rx_536c5c(void){}void audio_ble_l2c_master_rx_536fbc(void){}
void audio_ble_l2c_hci_register(void (*a)(void),void (*b)(void)){(void)a;(void)b;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,L2cInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_l2c_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 translate={syms[k]:v for k,v in callbacks.items()}
 for name,native,cid in cases:
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);state=syms['audio_ble_l2c_state'] if c else 0x200737d8;slave=syms['audio_ble_l2c_slave_state'] if c else 0x20073bd8
   u.mem_write(state,b'\xaa'*0x30);u.mem_write(slave,b'\xaa'*0x18);events=[]
   child=(syms['audio_ble_l2c_hci_register']&~1) if c else 0x5367f0
   def cut(uc,a,size,_):
    if a!=child:return
    p,q=uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)
    events.append((translate.get(p,p) if c else p,translate.get(q,q) if c else q))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   if name=='L2cRegister':
    u.reg_write(UC_ARM_REG_R0,cid);u.reg_write(UC_ARM_REG_R1,0x20081001);u.reg_write(UC_ARM_REG_R2,0x20082001)
   u.emu_start((syms[name] if c else native)|1,0x600000,count=2000)
   rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
   fields=[translate.get(rd(state+i),rd(state+i)) if c else rd(state+i) for i in (0,4,8,12,16,20,24,28,32)]
   out.append((fields,bytes(u.mem_read(state+36,3)),bytes(u.mem_read(slave+0x14,3)),events))
  assert out[0]==out[1],(name,cid,out)
  print('PASS BLE L2CAP',name,cid)
