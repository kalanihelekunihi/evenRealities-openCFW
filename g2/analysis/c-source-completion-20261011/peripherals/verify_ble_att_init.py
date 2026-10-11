"""Actual compiled-C/native ATT state grids and callback registration."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
cases={'AttHandlerInit':0x4b511e,'AttsInit':0x5351dc,'AttsIndInit':0x533e40,'AttcInit':0x531b1c}
tables={'audio_ble_att_table_main':0x7851e0,'audio_ble_att_table_secondary':0x7851f0,'audio_ble_atts_ind_table':0x7852c0,'audio_ble_atts_table':0x7852f0,'audio_ble_attc_table':0x785250}
callbacks={'audio_ble_att_l2c_data_callback_4b4de0':0x4b4de1,'audio_ble_att_l2c_control_callback_4b4e08':0x4b4e09,'audio_ble_att_dm_conn_callback_4b4e50':0x4b4e51,'audio_ble_atts_callback_4b4ee6':0x4b4ee7}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_ble_att_l2c_data_callback_4b4de0(void){}void audio_ble_att_l2c_control_callback_4b4e08(void){}
void audio_ble_att_dm_conn_callback_4b4e50(void){}void audio_ble_atts_callback_4b4ee6(void){}
uint8_t audio_ble_att_table_main[1],audio_ble_att_table_secondary[1],audio_ble_atts_ind_table[1],audio_ble_atts_table[1],audio_ble_attc_table[1];
void L2cRegister(uint16_t a,void (*b)(void),void (*c)(void)){(void)a;(void)b;(void)c;}
void DmConnRegister(uint32_t a,void (*b)(void)){(void)a;(void)b;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,AttHandlerInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_att_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 translate={syms[k]:v for k,v in tables.items()};translate.update({syms[k]|1:v for k,v in callbacks.items()})
 for name,native in cases.items():
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   common,server,client=(syms[x] for x in ('audio_ble_att_common_state','audio_ble_atts_state','audio_ble_attc_state')) if c else (0x200610ac,0x2006e5f0,0x2006f904)
   u.mem_write(common,b'\xaa'*0x64);u.mem_write(server,b'\xaa'*0x268);u.mem_write(client,b'\xaa'*0x1b8);events=[]
   if c:
    for i in range(3):translate[common+i*0x14]=0x200610ac+i*0x14
   child={(syms['L2cRegister']&~1):0x530b5e,(syms['DmConnRegister']&~1):0x4b6c64} if c else {0x530b5e:0x530b5e,0x4b6c64:0x4b6c64}
   def cut(uc,a,size,_):
    if a not in child:return
    regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    regs=[translate.get(v,v) if c else v for v in regs]
    events.append((child[a],regs[:3 if child[a]==0x530b5e else 2]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,cut);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,5)
   u.emu_start((syms[name] if c else native)|1,0x600000,count=6000)
   def normalized(a,n,ptr_offsets):
    blob=bytearray(u.mem_read(a,n))
    if c:
     for off in ptr_offsets:
      val=struct.unpack_from('<I',blob,off)[0]
      struct.pack_into('<I',blob,off,translate.get(val,val))
    return bytes(blob)
   cp=[0x3c,0x40,0x44,0x48]
   sp=[g*0xc0+s*0x40+0x10 for g in range(3) for s in range(3)]+[0x260,0x264]
   cl=[g*0x84+s*0x2c for g in range(3) for s in range(3)]
   out.append((normalized(common,0x64,cp),normalized(server,0x268,sp),normalized(client,0x1b8,cl),events))
  assert out[0]==out[1],(name,out[0][-1],out[1][-1])
  print('PASS BLE ATT init',name)
