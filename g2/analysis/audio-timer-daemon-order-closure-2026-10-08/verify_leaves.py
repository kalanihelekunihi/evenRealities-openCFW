from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'verify.py').read_text().split('for static,aux_dynamic,command,now')[0],str(D/'verify.py'),'exec'))
leaf_rows=[]
for kind,count,expiry,now,last in [('next',count,expiry,0,0) for count,expiry in itertools.product([0,1],[0,150,0xffffffff])]+[('sample',0,0,now,last) for now,last in itertools.product([0,1,100,0xffffffff],[0,1,100,0xffffffff])]:
 outputs=[]
 for native in [False,True]:
  u=machine();S=L+8;OS=OVERFLOW+8;I=T+4
  w(u,L,count,S,0xffffffff,I if count else S,I if count else S);w(u,I,expiry,S,S,T,L);w(u,OVERFLOW,0,OS,0xffffffff,OS,OS);w(u,0x20074aa8,L);w(u,0x20074aac,OVERFLOW);w(u,0x20074a34,now);w(u,0x20074ab8,last);w(u,0x20074a3c,1);w(u,0x20074a30,0);w(u,0x20006500,0xa5a5a5a5,0x5a5a5a5a)
  at=sym['audio_timer_next_expiry' if kind=='next' else 'audio_timer_sample_time'] if native else 0x47e8f2 if kind=='next' else 0x47e916
  invoke(u,at,[0x20006500])
  outputs.append(dict(result=u.reg_read(UC_ARM_REG_R0),out=word(u,0x20006500),guard=word(u,0x20006504),last_tick=word(u,0x20074ab8),current_list=word(u,0x20074aa8),overflow_list=word(u,0x20074aac),basepri=u.reg_read(UC_ARM_REG_BASEPRI),primask=u.reg_read(UC_ARM_REG_PRIMASK),sp=u.reg_read(UC_ARM_REG_SP),lists=hashlib.sha256(bytes(u.mem_read(L,0x200))).hexdigest()))
 assert outputs[0]==outputs[1],(kind,count,expiry,now,last,outputs)
 if kind=='sample':assert outputs[0]['result']==now and outputs[0]['out']==int(now<last) and outputs[0]['last_tick']==now
 else:assert outputs[0]['result']==(expiry if count else 0) and outputs[0]['out']==int(not count)
 leaf_rows.append(dict(inputs=dict(kind=kind,count=count,expiry=expiry,now=now,last=last),**outputs[0]))
assert hashlib.sha256(elf.read_bytes()).hexdigest()==elfhash
(D/'leaf-results.json').write_text(json.dumps(dict(status='PASS',cases=len(leaf_rows),elf_sha256=elfhash,comparisons=leaf_rows,limits=['Next-expiry prefix read andactual empty-list switch through original tick/wrap helpers; no callback during empty-list wrap.','Synthetic tick values,not observedclock/task execution.']),indent=2)+'\n');print('PASS',len(leaf_rows),'timer leaf cases')
