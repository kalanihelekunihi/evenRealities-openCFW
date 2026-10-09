from pathlib import Path
import json,struct,subprocess,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
nm=Path(rec['gcc']).with_name('arm-none-eabi-nm');syms={p[2]:int(p[0],16) for l in subprocess.check_output([str(nm),str(elf)],text=True).splitlines() if len(p:=l.split())==3};sections=[]
with elf.open('rb') as f:
 for s in ELFFile(f).iter_sections():
  if s['sh_flags']&2 and s['sh_size']:sections.append((s['sh_addr'],s.data()))
def run(thread,flags,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);events=[];done=[]
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(uc,pc,n,user):
  if pc==0x4490e2:events.append(['thread',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);ret(thread);return
  if pc==0x43d0ce:events.append(['flags',flags]);ret(flags);return
  if pc==0x43d574:
   sp=uc.reg_read(UC_ARM_REG_SP);events.append(['error',*[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)],*struct.unpack('<II',uc.mem_read(sp,8))]);ret();return
  if pc==0x43ce9e:events.append(['compressed',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)]);ret();return
  if pc==0x10ff00:done.append(1);uc.emu_stop();return
  if native:assert 0x100000<=pc<0x110000,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms['uart_instance_init'] if native else 0x541a2e)|1)
 for _ in range(5000):
  if done:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert done
 return {'return':u.reg_read(UC_ARM_REG_R0),'handle':int.from_bytes(u.mem_read(0x20074b0c,4),'little'),'events':events}
rows=[];diff=[]
for thread in (0,0x20061234):
 for flags in range(8):
  f={'thread':thread,'flags':flags};a=run(thread,flags,False);b=run(thread,flags,True);rows.append({'fixture':f,'observed':a,'matches':a==b})
  if a!=b:diff.append({'fixture':f,'stock':a,'source':b})
out={'status':'PASS' if not diff else 'DIFFERENCES','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'differences':diff,'limits':'Direct wrapper entry; CMSIS thread creation and log sinks supplied. No created task execution or scheduler handover.'}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('CASES',len(rows),'DIFFERENCES',len(diff))
