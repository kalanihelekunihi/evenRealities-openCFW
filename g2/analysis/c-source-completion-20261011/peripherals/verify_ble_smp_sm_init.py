"""Actual compiled-C/native SMP initiator/responder table setup."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
cases={'SmpiInit':0x537eec,'SmpiScInit':0x537f14,'SmprInit':0x5380dc,'SmprScInit':0x538104}
tables={'audio_ble_smpi_legacy_table':0x78c344,'audio_ble_smpi_sc_table':0x78c320,'audio_ble_smpr_legacy_table':0x78c4ac,'audio_ble_smpr_sc_table':0x78c470,'audio_ble_smp_pairing_callback_56e6e0':0x56e6e1,'audio_ble_smp_auth_callback_56e84c':0x56e84d}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xf8];
uint8_t audio_ble_smpi_legacy_table[1],audio_ble_smpi_sc_table[1],audio_ble_smpr_legacy_table[1],audio_ble_smpr_sc_table[1];
void audio_ble_smp_pairing_callback_56e6e0(void){}void audio_ble_smp_auth_callback_56e84c(void){}void SmpScInit(void){}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpiInit',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_smp_sm_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 translated={syms[k]|(1 if 'callback' in k else 0):v for k,v in tables.items()}
 for name,native in cases.items():
  out=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);state=syms['audio_ble_smp_handler_state'] if c else 0x20070aec
   u.mem_write(state,b'\xaa'*0xf8);calls=[0];target=(syms['SmpScInit']&~1) if c else 0x56cf74
   def hook(uc,a,size,_):
    if a==target:calls[0]+=1;uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms[name] if c else native)|1,0x600000,count=1500)
   rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
   fields=[translated.get(rd(state+i),rd(state+i)) if c else rd(state+i) for i in (0xe4,0xe8,0xf0,0xf4)]
   out.append((fields,calls[0]))
  assert out[0]==out[1],(name,out)
  print('PASS SMP SM init',name)
