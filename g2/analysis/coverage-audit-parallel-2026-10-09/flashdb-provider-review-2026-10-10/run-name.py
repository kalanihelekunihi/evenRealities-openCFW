from pathlib import Path
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
import json,hashlib
D=Path('/repo/g2/analysis/flashdb-provider-execution-20261010-implementation');raw=Path('/repo/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';KEY=0x20020000;DB=0x20010000;SECTOR=DB+0x1000;SP=0x200ff000;STOP=0x800000
rows=[]
for n in [0,60,61,62,63,64,65,66]:
 for align in range(4):
  data=b'a'*n+b'\0'+b'\xa7'*8;u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_write(KEY+align,data);u.mem_write(SECTOR+20,b'\xff'*4);u.reg_write(UC_ARM_REG_R0,DB);u.reg_write(UC_ARM_REG_R1,SECTOR);u.reg_write(UC_ARM_REG_R2,KEY+align);u.reg_write(UC_ARM_REG_R3,0);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);out=[];length=[]
  def hook(u,a,size,d):
   if a in [0x544daa,0x4733ee]:out.append('accepted' if a==0x544daa else 'diagnostic');u.emu_stop();return
   if a==0x544d7e:length.append(u.reg_read(UC_ARM_REG_R0))
   assert 0x544d60<=a<0x544daa or 0x44a43c<=a<=0x44a470,hex(a)
  def write(u,acc,a,size,val,d):assert SP-128<=a and a+size<=SP
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x544d61,0,count=3000);assert length==[n] and out==['accepted' if n<=64 else 'diagnostic'];assert bytes(u.mem_read(KEY+align,len(data)))==data
  candidates={}
  for limit in range(61,66):
   with (D/f'name-{limit}.elf').open('rb') as f:
    e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];syms={s.name:s['st_value']&~1 for s in e.get_section_by_name('.symtab').iter_symbols()}
   v=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);v.mem_map(0x100000,0x10000);v.mem_map(STOP,0x1000);v.mem_map(0x20000000,0x100000);v.mem_write(KEY+align,data)
   for a,b in sections:v.mem_write(a,b)
   v.reg_write(UC_ARM_REG_R0,KEY+align);v.reg_write(UC_ARM_REG_SP,SP);v.reg_write(UC_ARM_REG_LR,STOP|1);state=[]
   def stop(v,a,size,d):
    if a==STOP:state.append('accepted');v.emu_stop()
    elif a==syms['diagnostic']:state.append('diagnostic');v.emu_stop()
   v.hook_add(UC_HOOK_CODE,stop);v.emu_start(syms['name_guard']|1,0,count=3000);assert len(state)==1;candidates[str(limit)]=state[0]
  assert candidates['64']==out[0];rows.append({'length':n,'alignment':align,'stock':out[0],'stock_strlen':length[0],'candidate_decisions':candidates})
matching=[l for l in range(61,66) if all(r['candidate_decisions'][str(l)]==r['stock'] for r in rows)];assert matching==[64]
Path('/tmp/flashdb-audit-name-results.json').write_text(json.dumps({'stock_cases':len(rows),'source_guard_cases':len(rows)*5,'matching_limits':matching,'cases':rows,'scope':'stock create_kv_blob prefix plus original strlen; stop before logging or subsequent create logic; source guard projection only'},indent=2)+'\n');print('32 stock name guards /160 source projections PASS; only limit64 matches')
