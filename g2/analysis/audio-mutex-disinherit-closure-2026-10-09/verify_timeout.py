from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=b[32:];receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
CUR=0x20009000;OTHER=0x20009400;READY=0x2006a49c

def run(native,priority=47,base=12,held=1,null=False,wrong=False,peer=False,top=54,mask=0,highest=0,blocked=False,in_use=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def init(a):w(a,0,a+8,0xffffffff,a+8,a+8)
 def append(a,i,owner,value=0):
  tail=word(a+16);w(i,value,a+8,tail,owner,a);w(tail+4,i);w(a+16,i);w(a,word(a)+1)
 for i in range(56):init(READY+20*i)
 w(0x20074a20,CUR if wrong else OTHER);w(0x20074a38,top);w(CUR+44,priority);w(CUR+96,base,held);w(CUR+24,(0x80000000 if in_use else 0)|(56-priority),0,0,CUR,0);init(0x20009800);append(0x20009800 if blocked else READY+20*priority,CUR+4,CUR)
 if peer:append(READY+20*priority,OTHER+4,OTHER)
 boundary=[];seen=[]
 def hook(u,a,n,d):
  if a==0x5fa0a4:boundary.append('before_assert_mask_helper');u.emu_stop();return
  if native:assert 0x100000<=a<0x110000,hex(a);seen.append(a)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_R0,0 if null else CUR);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R1,highest);pc=sym['vTaskPriorityDisinheritAfterTimeout'] if native else 0x455a1d
 for i in range(10000):
  u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
  if pc==0x2007f000 or boundary:break
 else:raise AssertionError('step limit')
 valid=not boundary;target=max(base,highest);changed=not null and held==1 and priority!=target and not wrong
 if valid:
  assert word(CUR+100)==held
  assert word(CUR+44)==(target if changed else priority)
  assert word(CUR+24)==((0x80000000 if in_use else 0)|(56-priority) if in_use or not changed else 56-target)
  assert word(CUR+20)==(0x20009800 if blocked else READY+20*(target if changed else priority))
  pass # void return register is not part of contract
 digest=hashlib.sha256(bytes(u.mem_read(CUR,0x500))+bytes(u.mem_read(READY,1120))+bytes(u.mem_read(0x20074a38,4))).hexdigest()
 if native:assert seen
 return {'boundary':boundary,'result':None,'state_sha256':digest,'held':word(CUR+100),'priority':word(CUR+44),'event_value':word(CUR+24),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}

rows=[]
for priority,base,held,highest,blocked,in_use,peer in itertools.product([12,47,54],[0,12],[1,2],[0,12,46],[False,True],[False,True],[False,True]):
 if base>priority or highest>priority:continue
 c=dict(priority=priority,base=base,held=held,highest=highest,blocked=blocked,in_use=in_use,peer=peer);o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for c in [dict(null=True),dict(wrong=True),dict(held=0)]:
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
(D/'timeout-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Synthetic coherent owner/waiter/list state; timeout notification routine only, not resumed scheduler or full mutex-take transaction.']},indent=2)+'\n');print('PASS',len(rows),'timeout-disinherit comparisons')
