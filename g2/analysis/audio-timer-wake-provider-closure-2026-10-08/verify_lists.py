from pathlib import Path
import json,itertools,hashlib
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('for priority,suspended,kind,event_index,ready_existing,pending_existing in itertools.product')[0])
profiles=[[],[0],[1],[150],[0,1,1,100,0xffffffff],[0xffffffff],[0xffffffff,0xffffffff]];rows=[]
def run(native,kind,values,value,index,remove):
 u,w,word,append=fixture(54,1,'delayed');L=DL;w(L,0,L+8,0xffffffff,L+8,L+8);items=[]
 for i,v in enumerate(values):
  I=0x20006500+32*i;items.append(I);append(L,I,0x12340000+i,v)
 if items and index:w(L+4,items[0] if index==1 else items[-1])
 I=0x20006700;w(I,value,0,0,0xabcdef00,0)
 if kind=='remove':I=items[remove]
 original={'sorted':0x4560b2,'remove':0x4560e8}
 native_names={'sorted':'audio_public_list_insert','remove':'uxListRemove'}
 a=sym[native_names[kind]] if native else original[kind]
 args=[I] if kind=='remove' else [L,I]
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(state_digest=hashlib.sha256(bytes(u.mem_read(L,0x320))).hexdigest(),count=word(L),index=hex(word(L+4)),return_value=u.reg_read(UC_ARM_REG_R0) if kind=='remove' else None)
for values,value,index in itertools.product(profiles,[0,1,2,100,150,0xfffffffe,0xffffffff],[0,1,2]):
 c=dict(kind='sorted',values=values,value=value,index=index,remove=0);o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for values,index in itertools.product(profiles[1:],[0,1,2]):
 for remove in range(len(values)):
  c=dict(kind='remove',values=values,value=0,index=index,remove=remove);o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
(D/'list-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Valid intrusive sorted lists with initialized sentinel, uint32 values and selected movable index.','MAX sentinel insertion uses tail explicitly; equal-value insertion follows existing peers.','No concurrent mutation or invalid membership modeled.']},indent=2)+'\n');print('PASS',len(rows),'list-provider comparisons')
