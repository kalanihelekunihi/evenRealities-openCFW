"""Actual ARM C/native radio context recovery branch and payload oracle."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_context_recover.c'
logs=[('start','774b64'),('read_fail','746eb4'),('compare','730eb4'),('match','746edc'),('skip','774b7c'),('stop_fail','768b54'),('set_fail','746f04'),('special_fail','768b70'),('commit_fail','768b8c'),('check_fail','784be0')]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('#include <stdint.h>\n'+''.join(f'int32_t audio_ble_radio_recover_{name}_{addr}(void*a,uint32_t*b){{return 0;}}\n' for name,addr in [('read','52f094'),('stop','52e8be'),('set','52ef74'),('special','52efba'),('commit','52efec')])+'int32_t audio_ble_radio_context_check_52e4b4(void*a){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*a,...){}\n'+''.join(f'const uint8_t audio_ble_radio_recover_log_{name}_{addr}[4]={{0}};\n' for name,addr in logs))
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_context_recover_52f0f8',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 child={'read':('audio_ble_radio_recover_read_52f094',0x52f094),'stop':('audio_ble_radio_recover_stop_52e8be',0x52e8be),'set':('audio_ble_radio_recover_set_52ef74',0x52ef74),'special':('audio_ble_radio_recover_special_52efba',0x52efba),'commit':('audio_ble_radio_recover_commit_52efec',0x52efec),'check':('audio_ble_radio_context_check_52e4b4',0x52e4b4),'log':('audio_ble_hci_boot_log_4733ee',0x4733ee)}
 cases=['read_fail','match','stop_fail','set_fail','special_fail','commit_fail','check_fail','success','skip']
 for name in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   calls=[];payload=[];cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in child.items()}
   logptr={((syms[f'audio_ble_radio_recover_log_{label}_{addr}']&~1) if is_c else int(addr,16)):label for label,addr in logs}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    if key=='log':calls.append((key,logptr.get(uc.reg_read(UC_ARM_REG_R0))))
    else:calls.append((key,))
    if key=='read':
     target=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(target,struct.pack('<II',0x00000380 if name=='match' else 0x12345678,0))
    if key in ('set','commit'):
     target=uc.reg_read(UC_ARM_REG_R1)
     if key=='set':uc.mem_write(target+4,struct.pack('<I',0xabcdef00))
     if key=='commit':payload.append(tuple(struct.unpack('<II',uc.mem_read(target,8))))
    uc.reg_write(UC_ARM_REG_R0,7 if name==f'{key}_fail' else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,7);u.reg_write(UC_ARM_REG_R2,1 if name=='skip' else 0);u.reg_write(UC_ARM_REG_R3,0)
   entry=syms['audio_ble_radio_context_recover_52f0f8'] if is_c else 0x52f0f8
   u.emu_start(entry|1,0x600000,count=500)
   results.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),calls,payload))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0])
