from pathlib import Path
import json,struct
from unicorn import *
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;P=H/'check.py';ns={'__file__':str(P)};exec(P.read_text().split('# Negative controls')[0],ns);saved=ns['raw'];cases=[]
def check(label,words,pc,r,expected,oracle=False):
 data=struct.pack('<'+'H'*len(words),*words);ns['raw']=data;fn={'body_start':'08000000','body_end_inclusive':hex(0x8000000+len(data)-1)};v,_=ns['analyze'](fn,0x8000000+pc,r);assert v==expected,(label,v,expected)
 actual=None
 if oracle:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x8000000,0x1000);u.mem_write(0x8000000,data);u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000)
  if oracle=='entry3':u.reg_write(UC_ARM_REG_R0,1)
  def hook(uc,address,size,user):
   if address==0x8000000+pc:uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x8000001,0,count=100);actual=u.reg_read([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4][r]);assert actual in v,(label,v,actual)
 cases.append(dict(label=label,inferred=[None if x is None else hex(x) for x in v],Unicorn_M0_value=None if actual is None else hex(actual)))
pool=[0,0,0,0,0x1234,0x2000]
check('Transparent loop preserves R4 without invented flags',[0x4c03,0x2800,0xd1fd,0x6821,0x4770]+[0]*3+[0x1234,0x2000],6,4,{0x20001234})
check('Changing-register loop remains uncertain',[0x4c03,0x3401,0xd1fd,0x6821,0x4770]+[0]*3+[0x1234,0x2000],6,4,{None,0x20001235})
check('Unknown entry-register loop stays unknown',[0x2800,0xd1fd,0x6821,0x4770],4,4,{None})
check('UXTB R0 does not clobber R4',[0x4c03,0xb2c0,0x6821,0x4770]+pool,4,4,{0x20001234},True)
check('SP ADR R0 does not clobber R4',[0x4c03,0xa808,0x6821,0x4770]+pool,4,4,{0x20001234},True)
check('SP ADR R4 changes R4 to unknown',[0x4c03,0xac08,0x6821,0x4770]+pool,4,4,{None})
check('STM R3 writeback advances its base',[0x4b03,0xc307,0x6819,0x4770]+pool,4,3,{0x20001240},True)
check('Unpredictable STM base-in-list rejected',[0x4c03,0xc30b,0x6821,0x4770]+pool,4,4,{None})
check('Empty LDM list rejected',[0x4c03,0xc900,0x6821,0x4770]+pool,4,4,{None})
check('Reserved REV encoding rejected',[0x4c03,0xba80,0x6821,0x4770]+pool,4,4,{None})
for word,label,value in [(0xb201,'SXTH',0xffffabcd),(0xb241,'SXTB',0xffffffcd),(0xb281,'UXTH',0xabcd),(0xb2c1,'UXTB',0xcd),(0xba01,'REV',0xcdab3412),(0xba41,'REV16',0x3412cdab),(0xbac1,'REVSH',0xffffcdab)]:
 check(label+' raw semantic',[0x4803,word,0xbf00,0x4770]+[0]*4+[0xabcd,0x1234],4,1,{value},True)
# LDM R1 containing base in list restores R1 instead of writeback.
check('ROM LDM base-in-list loads R1',[0x4903,0xc903,0xbf00,0x4770]+[0]*4+[0x10,0x0800,0x4321,0x2000],4,1,{0x20004321},True)
check('Transparent SCC cache must retain both definitions',[0x2800,0xd003,0x2403,0x2503,0xe002,0xbf00,0x2501,0x462c,0x2900,0xd1fc,0x432c,0x6820,0x4770],22,4,{1,3},True)
check('Same SCC counterexample takes alternative entry',[0x2800,0xd003,0x2403,0x2503,0xe002,0xbf00,0x2501,0x462c,0x2900,0xd1fc,0x432c,0x6820,0x4770],22,4,{1,3},'entry3')
ns['raw']=saved
(H/'controls.json').write_text(json.dumps(dict(status='PASS_20_RAW_MODEL_CONTROLS',cases=cases,limits=['Loop checks remain flag-unconstrained abstract controls, not hardware feasibility tests','Unpredictable/reserved instruction controls require conservative unknown; do not execute these as valid native behavior']),indent=2)+'\n');assert len(cases)==20;print('PASS',len(cases))
