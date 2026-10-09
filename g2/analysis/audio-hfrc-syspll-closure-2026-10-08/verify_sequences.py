from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'verify.py').read_text().split('rows=[]')[0],str(D/'verify.py'),'exec'))
def capture(u):return dict(status=u.reg_read(UC_ARM_REG_R0),table=bytes(u.mem_read(0x20073324,56)).hex(),flags=bytes(u.mem_read(0x20074f55,7)).hex(),handle=word(u,0x2007425c),driver=bytes(u.mem_read(0x200740f4,8)).hex(),pointers=[norm(word(u,a)) for a in [0x20074260,0x20074264,0x20074268]],force=word(u,0x40004044),hfadj=word(u,0x40004020),pll=word(u,0x400204d8),primask=u.reg_read(UC_ARM_REG_PRIMASK))
def sequence(native,c):
 family=c['kind'].split('_')[0];u=run(native,**c,expose=True);states=[capture(u)]
 for n in [family+'_request',family+'_release']:
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,52);u.emu_start((sym['audio_'+n] if native else entries[n])|1,0x2007f000,count=12000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;states.append(capture(u))
 return states
scenarios=[dict(kind='hfrc_request',adjusted=1),dict(kind='hfrc_request',adjusted=0),dict(kind='hfrc2_request',adjusted=0),dict(kind='hfrc2_request',adjusted=1,ref=1),dict(kind='hfrc2_request',adjusted=1,ref=0),dict(kind='syspll_request',ref=1,lock=1),dict(kind='syspll_request',ref=1,lock=0),dict(kind='syspll_request',ref=0)]
rows=[]
for base,other,mask in itertools.product(scenarios,[0,1],[0,1]):
 case=dict(base,other=other,mask=mask);o=sequence(False,case);n=sequence(True,case);assert o==n,(case,o,n)
 if not other and case['kind']=='syspll_request' and case.get('ref')==1 and case.get('lock')==0:assert [x['status'] for x in o]==[4,0,0] and o[0]['handle'] and o[1]['handle'] and not o[2]['handle']
 if not other and case['kind']=='hfrc_request' and case['adjusted']:assert o[2]['hfadj']&1 and not(o[2]['force']&1) and bytes.fromhex(o[2]['flags'])[4]==1
 rows.append(dict(inputs=case,states=o))
(D/'sequence-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Native/original repeated request/release fixtures, not live scheduler or physically observed states.','Other-user fixture may omit a corresponding driver handle; it tests branch preservation rather than declaring reachable production state.','SYSPLL lock timeout is synthetic lockbit0 with actual stock polling.']),indent=2)+'\n');print('PASS',len(rows),'repeated request/release comparisons')
