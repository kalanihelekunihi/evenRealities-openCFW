from pathlib import Path
import json,hashlib,itertools
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def reset_run(native,dev=0,aud=0,ready=1,callback=1,signature=0x1f01600d,gate=3,timer=0,release=3,mask=0):
 u=machine();w(u,0x40021008,dev);w(u,0x40021010,aud);w(u,0x40021108,gate<<4);w(u,0x2005665c,signature);w(u,0x20000294,3);w(u,0x20000298,3);w(u,0x2000029c,6);w(u,0x400083e0,timer)
 for i in range(20):w(u,0x20056660+i*4,(0x01040608+i*0x0102040b)&0xffffffff)
 u.mem_write(0x20074f60,b'\0'*32);u.mem_write(0x20074f75,bytes([2,0]));w(u,0x20073274,0x5a490d if callback else 0);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 calls=[];writes=[];waiting=False;reads=0;events=[]
 def code(u,a,n,d):
  nonlocal waiting
  if a==0x47f5b8:calls.append(['peripheral_enable',u.reg_read(UC_ARM_REG_R0)])
  if a==0x480028:calls.append(['temperature_request_float_bits',u.reg_read(UC_ARM_REG_S0)])
  if a==0x4807fc:
   waiting=True;calls.append(['wait_status',[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]])
 def write(u,ac,a,n,v,d):
  writes.append([hex(a),n,v])
  if a==0x40021004 and (v&0x8000000) and ready:
   w(u,0x40021008,word(u,0x40021008)|0x8000000);events.append(['synthetic_otp_status_ready'])
 def read(u,ac,a,n,v,d):
  nonlocal reads
  if waiting and a==0x400083e0:
   reads+=1
   if release and reads==release:
    w(u,0x400083e0,word(u,0x400083e0)&~1);events.append(['synthetic_timer_release_on_wait_read',reads])
 u.hook_add(UC_HOOK_CODE,code)
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 u.hook_add(UC_HOOK_MEM_READ,read,begin=0x400083e0,end=0x400083e3)
 try:u.emu_start((sym['pcm22_reset'] if native else 0x5a4e0c)|1,0x2007f000,count=3000000)
 except UcError as e:raise AssertionError((native,hex(u.reg_read(UC_ARM_REG_PC)),e))
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('instruction-limit',native,hex(u.reg_read(UC_ARM_REG_PC)))
 return dict(status=u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,events=events,timer_wait_reads=reads,globals=bytes(u.mem_read(0x20074f60,32)).hex(),targets=bytes(u.mem_read(0x200742c8,12)).hex(),profile_ton=[word(u,0x20000294),word(u,0x2000029c)],device_status=word(u,0x40021008),timer_status=word(u,0x400083e0),primask=u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for dev,aud,mask in itertools.product([1,0x8000000],[0,1],[0,1]):cases.append(dict(dev=dev,aud=aud,mask=mask))
for ready,callback,signature,gate,timer,release,mask in itertools.product([0,1],[0,1],[0,0x1f01600d],[0,3],[0,1],[0,1,3],[0,1]):cases.append(dict(ready=ready,callback=callback,signature=signature,gate=gate,timer=timer,release=release,mask=mask))
rows=[]
for case in cases:
 o=reset_run(False,**case);n=reset_run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'reset-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),return_counts={str(k):sum(x['status']==k for x in rows) for k in [0,1,4]},comparisons=rows,limits=['Real peripheral-enable, temperature wrapper, generic dispatch, wait and delay execute original instructions.','Both sides register original PCM2.2 control at0x5A490D; reset is native, control/provider dependencies remain original.','OTP-ready write response and timer release on wait-read are explicit synthetic MMIO events, not hardware traces.','Never-release fixtures exercise actual2500-loop timeout; physical elapsed time and live ISR delivery unverified.']),separators=(',',':'))+'\n');print('PASS',len(rows),'PCM2.2 reset comparisons')
