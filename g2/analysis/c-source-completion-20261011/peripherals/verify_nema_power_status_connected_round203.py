from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-power-status-connected-round203';S=B/'root-nema-power-control-round197/candidate.c';CELL=0x20074f04;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_power_status_47f90c','audio_power_peripheral_on','audio_power_peripheral_off','audio_uart_nema_get_error_4b128a','audio_uart_nema_vg_get_error_51564c','audio_uart_nema_reset_last_submission_514184','audio_uart_nema_gpu_reinit_4b11b0','audio_uart_nema_vg_reinit_5224b6','audio_uart_nema_reg_read_51403c'];native=[0x47f90c,0x47f5b8,0x47f7ae,0x4b128a,0x51564c,0x514184,0x4b11b0,0x5224b6,0x51403c];cuts=[0x101010+i*16 for i in range(len(names))]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native51419a..514238.');S=Path(t)/'selected.c';S.write_text((B/'root-nema-power-control-round197/candidate.c').read_text().split('/* Native51419a')[0]+selected[a:selected.index('#include <stdint.h>',a)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_power_control_51419a','-Wl,--defsym=audio_uart_nema_vg_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for i,(n,a) in enumerate(zip(names,cuts)) if i not in [0,3,4,5,8]]+['-Wl,--defsym=audio_uart_nema_context_cell=0x20074efc','-Wl,--defsym=audio_uart_nema_last_submission=0x20002e08','-Wl,--defsym=audio_uart_nema_register_base=0x78f2f4',str(S),str(B/'root-nema-error-get-round179/candidate.c'),str(B/'root-nema-vg-error-state-round193/candidate.c'),str(B/'root-nema-register-reset-round198/candidate.c'),str(B/'root-nema-power-status-round200/candidate.c'),str(B/'root-power-descriptor-round201/candidate.c'),str(R/'components/audio/uart_thread_source_candidate/byte_copy.c'),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,state,reinit,status,powered,on,off,busy,gfx,vg,present,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(0x20001000 if present else 0));u.mem_write(0x20074efc,W(0x20002000));u.mem_write(0x20001000,bytes([165])*256);u.mem_write(0x20002000,bytes([90])*48);u.mem_write(0x20001080,W(0x12345678));u.mem_write(0x20002020,W(0x12345678));u.mem_write(0x20002e08,W(37));u.mem_write(0x400900fc,W(busy));u.mem_write(0x40021008,W(0x40000 if powered else 0));events=[];trace=[];counts={3:0,4:0}
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses or addresses.index(a) in [0,3,4,5,8]:return
   i=addresses.index(a);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);events.append((i,r0 if i in [0,1,2,8] else None));ret=0xa5a5a5a5
   if i==0:uc.mem_write(r1,bytes([powered]));ret=status
   elif i==1:ret=on
   elif i==2:ret=off
   elif i==8:ret=busy
   elif i in [3,4]:counts[i]+=1;ret=0x12345678 if counts[i]==1 else (gfx if i==3 else vg)
   if i==6:uc.mem_write(0x20002020,W(gfx))
   if i==7:uc.mem_write(0x20001080,W(vg))
   if mutation and i==6:uc.mem_write(CELL,W(0 if present else 0x20001000))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+4 or 0x20074efc<=a<0x20074f00 or 0x20001000<=a<0x20001100 or 0x20002000<=a<0x20002030 or 0x20002e08<=a<0x20002e0c or 0x40021008<=a<0x4002100c or 0x400900fc<=a<0x40090100 or 0x78f2f4<=a<0x78f2f8:trace.append((access,a,n,v if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,state);u.reg_write(UC_ARM_REG_R1,reinit);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_power_control_51419a'] if isc else 0x51419a)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CELL,4)),bytes(u.mem_read(0x20001000,256)),bytes(u.mem_read(0x20002000,48)),bytes(u.mem_read(0x20002e08,4)),bytes(u.mem_read(0x400900fc,4))
 cases=set()
 for state in range(256):
  for high in [0,0xa5a50000]:
   for powered in [0,1,255]:cases.add((state|high,1,0,powered,0,0,0,0,0,1,0))
 for state in [0,1,2,3,256,257,258,0xffffffff]:
  for reinit in [0,1,255,256,257,0xffffffff]:
   for status,powered,on,off,busy,gfx,vg,present,mutation in [(0,0,0,0,0,0,0,1,0),(1,0,0,0,0,0,0,1,0),(0xffffffff,255,0,0,0,0,0,1,0),(0,0,6,0,0,0,0,1,0),(0,1,0,6,0,0,0,1,0),(0,1,0,0,1,0,0,1,0),(0,0,0,0,0,1,0,1,0),(0,0,0,0,0,0,1,1,0),(0,0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,1,1),(0,0,0,0,0,0,0,0,1)]:cases.add((state,reinit,status,powered,on,off,busy,gfx,vg,present,mutation))
 cases={c for c in cases if c[2]==0}
 for case in sorted(cases):
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native':a[:-1],'source':b[:-1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_CONNECTED_POWER_ACTUAL_STATUS_DESCRIPTOR_STATE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'support_candidate_hashes':{n:hashlib.sha256((B/n/'candidate.c').read_bytes()).hexdigest() for n in ['root-nema-error-get-round179','root-nema-vg-error-state-round193','root-nema-register-reset-round198','root-nema-power-status-round200','root-power-descriptor-round201']},'child_cuts':4,'limits':['All256state bytes/highbits, reinit lowbyte, real peripheral20 status plus controlled on/off/busy/GFX/VG error branches (status-error injection removed), context presence/child mutation, ordered calls/context reads/result/SP compared.','Actual GFX/VG error getters, last-submission reset, register-read execute; actual status/descriptor/copy execute; remaining on/off/GPU-reinit/VG-reinit cuts. Physical MMIO/driver/data ownership/hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
