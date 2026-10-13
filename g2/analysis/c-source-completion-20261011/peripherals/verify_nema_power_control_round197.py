from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-power-control-round197';S=D/'candidate.c';CELL=0x20074f04;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_power_status_47f90c','audio_power_peripheral_on','audio_power_peripheral_off','audio_uart_nema_get_error_4b128a','audio_uart_nema_vg_get_error_51564c','audio_uart_nema_reset_last_submission_514184','audio_uart_nema_gpu_reinit_4b11b0','audio_uart_nema_vg_reinit_5224b6','audio_uart_nema_reg_read_51403c'];native=[0x47f90c,0x47f5b8,0x47f7ae,0x4b128a,0x51564c,0x514184,0x4b11b0,0x5224b6,0x51403c];cuts=[0x101010+i*16 for i in range(len(names))]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native51419a..514238.');S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native51419a')[0]+selected[a:selected.index('#include <stdint.h>',a)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_power_control_51419a','-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,state,reinit,status,powered,on,off,busy,gfx,vg,present,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(0x20001000 if present else 0));events=[];trace=[];counts={3:0,4:0}
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);events.append((i,r0 if i in [0,1,2,8] else None));ret=0xa5a5a5a5
   if i==0:uc.mem_write(r1,bytes([powered]));ret=status
   elif i==1:ret=on
   elif i==2:ret=off
   elif i==8:ret=busy
   elif i in [3,4]:counts[i]+=1;ret=0x12345678 if counts[i]==1 else (gfx if i==3 else vg)
   if mutation and i==6:uc.mem_write(CELL,W(0 if present else 0x20001000))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,state);u.reg_write(UC_ARM_REG_R1,reinit);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_power_control_51419a'] if isc else 0x51419a)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CELL,4))
 cases=set()
 for state in range(256):
  for high in [0,0xa5a50000]:
   for powered in [0,1,255]:cases.add((state|high,1,0,powered,0,0,0,0,0,1,0))
 for state in [0,1,2,3,256,257,258,0xffffffff]:
  for reinit in [0,1,255,256,257,0xffffffff]:
   for status,powered,on,off,busy,gfx,vg,present,mutation in [(0,0,0,0,0,0,0,1,0),(1,0,0,0,0,0,0,1,0),(0xffffffff,255,0,0,0,0,0,1,0),(0,0,6,0,0,0,0,1,0),(0,1,0,6,0,0,0,1,0),(0,1,0,0,1,0,0,1,0),(0,0,0,0,0,1,0,1,0),(0,0,0,0,0,0,1,1,0),(0,0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,1,1),(0,0,0,0,0,0,0,0,1)]:cases.add((state,reinit,status,powered,on,off,busy,gfx,vg,present,mutation))
 for case in sorted(cases):
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native':a[:-1],'source':b[:-1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_POWER_CONTROL_CHILD_CONTRACTS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':9,'limits':['All256state bytes/highbits, reinit lowbyte, status/on/off/busy/GFX/VG error branches, context presence/child mutation, ordered calls/context reads/result/SP compared.','Actual child providers/register access/driver/hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
