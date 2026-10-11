"""Actual compiled-C/native Cordio DM table placement and lock call order."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
cases={'DmAdvInit':0x4bac2c,'DmPhyInit':0x4c584a,'DmConnMasterInit':0x536a98,'DmConnSlaveInit':0x536b18,'DmSecInit':0x4d250c,'DmSecLescInit':0x53496a,'DmPrivInit':0x4d27e0}
tables={'audio_ble_dm_adv_table':0x78a808,'audio_ble_dm_phy_table':0x78a85c,'audio_ble_dm_master_table_a':0x78d424,'audio_ble_dm_master_table_b':0x78d41c,'audio_ble_dm_slave_table_a':0x785be0,'audio_ble_dm_slave_table_b':0x78d42c,'audio_ble_dm_security_table':0x78a898,'audio_ble_dm_security_state_table':0x7856b0,'audio_ble_dm_lesc_table':0x78a8a4,'audio_ble_dm_priv_table_a':0x78a868,'audio_ble_dm_priv_table_b':0x78a874}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_dm_config[64];
uint8_t audio_ble_dm_adv_table[1],audio_ble_dm_phy_table[1],audio_ble_dm_master_table_a[1],audio_ble_dm_master_table_b[1];
uint8_t audio_ble_dm_slave_table_a[1],audio_ble_dm_slave_table_b[1],audio_ble_dm_security_table[1],audio_ble_dm_security_state_table[1];
uint8_t audio_ble_dm_lesc_table[1],audio_ble_dm_priv_table_a[1],audio_ble_dm_priv_table_b[1];
void WsfTaskLock(void){}void WsfTaskUnlock(void){}
void audio_ble_dm_adv_lower(void){}void HciSetLeSupFeat(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmAdvInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_dm_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 translate={syms[k]:v for k,v in tables.items()}
 source_child={syms[k]&~1:v for k,v in {'WsfTaskLock':0x52b8c8,'WsfTaskUnlock':0x52b8d0,'audio_ble_dm_adv_lower':0x4b30e4,'HciSetLeSupFeat':0x52acd6}.items()}
 for name,native in cases.items():
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   config,mastera,masterb,sec,adv=(syms[x] for x in ('audio_ble_dm_config','audio_ble_dm_master_state_a','audio_ble_dm_master_state_b','audio_ble_dm_security_state','audio_ble_dm_adv_ready_cell')) if c else (0x20000694,0x20073fe4,0x20073fd8,0x20074114,0x200744f4)
   for a,n in ((config,64),(mastera,12),(masterb,12),(sec,8),(adv,4)):u.mem_write(a,b'\xaa'*n)
   events=[];targets=source_child if c else {v:v for v in source_child.values()}
   def hook(uc,a,size,_):
    if a not in targets:return
    dest=targets[a];args=[]
    if dest==0x52acd6:args=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    events.append((dest,args));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms[name] if c else native)|1,0x600000,count=2000)
   rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
   normalize=lambda v:translate.get(v,v) if c else v
   fields=[normalize(rd(config+i)) for i in (0,0x14,0x18,0x20,0x24,0x3c)]
   fields += [normalize(rd(a+i)) for a in (mastera,masterb) for i in (4,8)]
   fields += [normalize(rd(sec+i)) for i in (0,4)];fields +=[rd(adv)]
   out.append((fields,events))
  assert out[0]==out[1],(name,out)
  print('PASS BLE DM init',name)
