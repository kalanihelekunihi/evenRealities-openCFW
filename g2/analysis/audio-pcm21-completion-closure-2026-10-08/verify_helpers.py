from pathlib import Path
import itertools,json,hashlib,struct
D=Path(__file__).resolve().parent
exec(compile((D/'verify.py').read_text().split('rows=[];cases=[]')[0],str(D/'verify.py'),'exec'))
entries={'prepare':0x5a0c20,'change_state':0x5a0d44,'plan':0x5a13e8,'apply':0x5a0fc4}
providers={0x48d620:0,0x5a0d9c:2,0x5a0ae8:1,0x480240:1,0x48028a:1,0x4807a0:1,0x474efa:0,0x474eb4:0,0x4802ce:0,0x5a0b9c:0,0x5a0b54:1}
def test(native,kind,case):
 u=machine();w(u,0x2005665c,0x1f01600d)
 for i in range(20):w(u,0x20056660+4*i,(0x01040608+i*0x0102040b)&0xffffffff)
 u.mem_write(0x20074f60,b'\0'*32)
 for a,v in case.get('words',[]):w(u,a,v)
 for a,v in case.get('bytes',[]):u.mem_write(a,bytes([v]))
 request=case.get('request',[0,0,0,0,2,0,0]);u.mem_write(0x20006000,struct.pack('<4I3B',*request));w(u,0x20006040,0xa5a5a5a5);w(u,0x20006044,0x5a5a5a5a)
 args=case.get('args',[0x20006000] if kind=='prepare' else [0x20006000,0x20006040,0x20006044]);calls=[];writes=[]
 def hook(u,a,n,d):
  if native:a={sym['pcm21_ton']&~1:0x5a0d9c,sym['pcm21_timer_publish']&~1:0x5a0ae8,sym['pcm21_buck_complete']&~1:0x5a0b9c,sym['pcm21_boost_remove']&~1:0x5a0b54}.get(a,a)
  if a in providers:calls.append([hex(a),[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1][:providers[a]]]])
 def write(u,ac,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook)
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
 entry=sym['pcm21_'+kind] if native else entries[kind]
 try:u.emu_start(entry|1,0x2007f000,count=500000)
 except UcError as e:raise AssertionError((kind,case,native,hex(u.reg_read(UC_ARM_REG_PC)),e))
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,(kind,case,'instruction-limit')
 return dict(status=u.reg_read(UC_ARM_REG_R0) if kind=='plan' else None,outputs=bytes(u.mem_read(0x20006040,8)).hex(),globals=bytes(u.mem_read(0x20074f60,32)).hex(),calibration_targets=bytes(u.mem_read(0x200742c8,12)).hex(),cached=word(u,0x20000298),timer_ram=bytes(u.mem_read(0x20073270,64)).hex(),calls=calls,writes=writes)
cases=[]
for new,old,flag in itertools.product([0,1,2,3,4,256,257,258],[0,1,2,3,4,256,257,258],[0,1]):cases.append(('change_state',dict(args=[new,old],words=[[0x4002037c,0xffffffff]],bytes=[[0x20074f6d,flag],[0x20074f6b,0xa5]])))
for temp,dev,aud,pll in itertools.product([0,1,2,3,4,255],[0,1,0x40000000],[0,0x80,0x4c4],[0,0x20000000]):cases.append(('prepare',dict(request=[dev,aud,0,0,temp,0,0],words=[[0x400204d8,pll]],bytes=[[0x20074f7b,0xa5]])))
for index,clk,enable in itertools.product([0,7,15],[0,5,6,18,19,24,25,255,256,479,480,511],[0,1]):cases.append(('prepare',dict(request=[0,0,0,0,2,0,0],words=[[0x40008200+index*32,(clk<<8)|enable],[0x40008010,1<<index]],bytes=[[0x20074f7b,0xa5]])))
for temp,cpu,gpu,dev,flag,cpu_hw in itertools.product([0,1,2,3,4,15],[0,1,2,4],[0,1,2,3],[0,1,0xc00000],[0,1],[0,2]):cases.append(('plan',dict(request=[dev,0,0,0,temp,cpu,gpu],words=[[0x200742b0,flag],[0x40021000,cpu_hw]])))
for next,old,enabled,flag in itertools.product(range(20),range(20),[0,1],[0,1]):
 cases.append(('apply',dict(args=[next,old,2,6],words=[[0x20000298,(old+7)%20],[0x400083e0,enabled],[0x40020080,0xa5a5a5a5],[0x40020044,0x87654321],[0x4002004c,0x12345678]],bytes=[[0x20074f69,flag]])))
for clk,flags,running in itertools.product([0,1,2,3,15],[0,0x40000000,0x80000000],[0,1]):
 cases.append(('prepare',dict(request=[0,0,0,0,2,0,0],words=[[0x40008800,clk|flags]],bytes=[[537350010,running],[0x20074f7b,0xa5]])))
for coretrim,nf,nc,enabled,cached in itertools.product([1016,1017,1023],[1,100],[1,100],[0,1],[0,8]):
 cal=(nf<<21)|(3<<17)|(coretrim<<7)|nc
 cases.append(('apply',dict(args=[8,0,2,2],words=[[0x200001f4,0],[0x200001f4+32,1],[0x20000244,0],[0x20000244+32,1],[0x20056660+32,cal],[0x20056660,1],[0x20000298,cached],[0x400083e0,enabled],[0xe000ed14,0x20000]])))
for mem,ssram,temp in itertools.product([0,0xffffffff],[0,0xffffffff],[2,5]):
 cases.append(('plan',dict(request=[0,0,mem,ssram,temp,0,0])))
rows=[]
for kind,case in cases:
 original=test(False,kind,case);native=test(True,kind,case);assert original==native,(kind,case,original,native);rows.append(dict(function=kind,inputs=case,**original))
(D/'helper-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),counts={kind:sum(x['function']==kind for x in rows) for kind in entries},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Synthetic trim words and initialized SRAM; passive MMIO, not physical calibration or timing.','Common TON/timer/cache/completion providers execute actual original instructions.','Function calls, not architectural interrupt exception delivery.']),separators=(',',':'))+'\n');print('PASS',len(rows),'direct PCM2.1 helper comparisons')
