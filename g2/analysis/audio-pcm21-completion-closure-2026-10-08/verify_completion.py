from pathlib import Path
import itertools,json,hashlib,struct
D=Path(__file__).resolve().parent
exec(compile((D/'verify.py').read_text().split('rows=[];cases=[]')[0],str(D/'verify.py'),'exec'))
entries={'ton':0x5a0d9c,'timer_publish':0x5a0ae8,'boost_remove':0x5a0b54,'buck_complete':0x5a0b9c,'timer_isr':0x5a0bcc,'before_override':0x5a1bbc,'before_enable':0x5a1bcc,'after_enable':0x5a1bec,'initialize':0x5a1c18}
providers={0x4d3f3c:3,0x4801fc:0,0x48d620:0,0x5a0d9c:2,0x5a0ae8:1,0x480240:1,0x48028a:1,0x4807a0:1,0x474efa:0,0x474eb4:0,0x4802ce:0,0x5a0b9c:0,0x5a0b54:1}
info_fixtures={}
def test(native,kind,case):
 u=machine();u.mem_map(0x42000000,0x8000)
 seed=case.get('seed',0x12345678)
 if seed not in info_fixtures:info_fixtures[seed]=b''.join(struct.pack('<I',(seed+i*0x0102040b)&0xffffffff) for i in range(0x2000))
 u.mem_write(0x42000000,info_fixtures[seed])
 w(u,0x2005665c,0x1f01600d)
 for i in range(20):w(u,0x20056660+4*i,(0x01040608+i*0x0102040b)&0xffffffff)
 u.mem_write(0x20074f60,b'\0'*32)
 for a,v in case.get('words',[]):w(u,a,v)
 for a,v in case.get('bytes',[]):u.mem_write(a,bytes([v]))
 request=case.get('request',[0,0,0,0,2,0,0]);u.mem_write(0x20006000,struct.pack('<4I3B',*request));w(u,0x20006040,0xa5a5a5a5);w(u,0x20006044,0x5a5a5a5a)
 args=case.get('args',[0x20006000] if kind=='prepare' else [0x20006000,0x20006040,0x20006044]);calls=[];writes=[]
 def hook(u,a,n,d):
  if native:a={sym['pcm21_ton']&~1:0x5a0d9c,sym['pcm21_timer_publish']&~1:0x5a0ae8,sym['pcm21_buck_complete']&~1:0x5a0b9c,sym['pcm21_boost_remove']&~1:0x5a0b54}.get(a,a)
  if a in providers:calls.append([hex(a),[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][:providers[a]]]])
 def write(u,ac,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook)
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_PRIMASK,case.get('mask',0))
 entry=sym['pcm21_'+kind] if native else entries[kind]
 try:u.emu_start(entry|1,0x2007f000,count=500000)
 except UcError as e:raise AssertionError((kind,case,native,hex(u.reg_read(UC_ARM_REG_PC)),e))
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,(kind,case,'instruction-limit')
 return dict(primask=u.reg_read(UC_ARM_REG_PRIMASK),calibration=bytes(u.mem_read(0x2005665c,108)).hex(),status=u.reg_read(UC_ARM_REG_R0) if kind in ['initialize','before_override','before_enable','after_enable'] else None,outputs=bytes(u.mem_read(0x20006040,8)).hex(),globals=bytes(u.mem_read(0x20074f60,32)).hex(),calibration_targets=bytes(u.mem_read(0x200742c8,12)).hex(),cached=word(u,0x20000298),timer_ram=bytes(u.mem_read(0x20073270,64)).hex(),calls=calls,writes=writes)
cases=[]
for selector,profile,core,mem,cal in itertools.product([0,1,2,3,4,5,6,7,8,255,256],range(20),[0,1010,1023],[0,63],[0,0xffffffff]):
 words=[[0x40020080,0xa5a5a400|core],[0x40020088,0x12345640|mem],[0x40020380,0xffffffff],[0x40020344,0x56789abc],[0x40020354,0xaabbccdd],[0x40020358,0x87654321],[0x4002034c,0x11223344]]+[[a,cal] for a in [0x200566b0,0x200566b4,0x200566b8,0x200566bc]]
 cases.append(('ton',dict(args=[selector,profile],words=words)))
for boost,core,cal in itertools.product([0,1,2,256,257],[0,1016,1017,1022,1023],[0,0x12345678,0xffffffff]):
 cases.append(('timer_publish',dict(args=[boost],words=[[0x40020080,0xabcdfc00|core],[0x40020088,0x12345678],[0x400201b0,0x98765432],[0x200566c4,cal]])))
for remove,core,delta,cal in itertools.product([0,1,2,256,257],[0,1016,1017,1022,1023],[0,7,1023],[0,0x12345678,0xffffffff]):
 cases.append(('boost_remove',dict(args=[remove],words=[[0x40020080,0xabcdfc00|core],[0x40020088,0x12345678],[0x400201b0,0x98765432],[0x200566c4,cal],[0x200742c8,delta]])))
for flag,target in itertools.product([0,1,2,255],[0,1,127,128,0xffffffff]):
 cases.append(('buck_complete',dict(args=[],words=[[0x40020044,0xaabbccdd],[0x4002004c,0x87654321],[0x200742cc,target],[0x200742d0,target^0x5a]],bytes=[[0x20074f69,flag]])))
for profile,switch,flag,mask in itertools.product([0,3,8,12,15,19],[0,1],[0,1],[0,1]):
 cases.append(('timer_isr',dict(args=[],mask=mask,words=[[0x20000294,profile],[0x40020080,1017],[0x4002037c,0x87654321],[0x200742c8,7],[0x200742cc,42],[0x200742d0,69],[0x400083e0,1],[0x200566c4,0x12345678]],bytes=[[0x20074f6d,switch],[0x20074f69,flag]])))
for kind,sig,cal in itertools.product(['before_override','before_enable','after_enable'],[0,0x1f01600d],[0,0x12345678,0xffffffff]):
 cases.append((kind,dict(args=[],words=[[0x2005665c,sig],[0x2005667c,cal],[0x200566c4,cal],[0x40020080,0xabcdef12],[0x40020088,0x76543210],[0x400201b0,0x11223344],[0x4002034c,0xffffffff]])))
for cfg,power,seed in itertools.product([0,8],[0,0x8000000],[0,0x12345678,0xffffffff]):
 cases.append(('initialize',dict(args=[],seed=seed,words=[[0x400201bc,cfg],[0x40021008,power]])))
rows=[]
for kind,case in cases:
 original=test(False,kind,case);native=test(True,kind,case);assert original==native,(kind,case,original,native);rows.append(dict(function=kind,inputs=case,**original))
(D/'completion-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),counts={kind:sum(x['function']==kind for x in rows) for kind in entries},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Synthetic calibration words, passive MMIO and direct ISR function entry.','Original timer-stop, IRQ-save and delay providers execute, no success-return stubs.','ISR PRIMASK restoration is checked; real NVIC exception delivery and live task/IRQ timing are unverified.']),separators=(',',':'))+'\n');print('PASS',len(rows),'PCM2.1 TON/completion comparisons')
