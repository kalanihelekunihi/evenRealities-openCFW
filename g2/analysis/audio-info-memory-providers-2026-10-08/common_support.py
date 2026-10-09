from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
providers={0x4807a0:('delay',1),0x480826:('wait5',4),0x4809c4:('mcuctrl',2),0x480eee:('pin_get',1),0x480f0c:('pin_set',2),0x480058:('syspll_enable',0),0x48009e:('syspll_disable',0),0x47f5b8:('enable',1),0x47f7ae:('disable',1),0x475014:('bus_flush',2)}
def run(native,flags=1,ref=0,ready=1,scratch=0,pattern=0,poa=0,signature=0x5af0):
 u=machine();w(u,0x40008858,(signature<<16)|(ref<<6)|flags);w(u,0x4000885c,poa<<1)
 for a in [0x400200c0,0x400204e8,0x40004044,0x400204d8,0x40201000,0x40208100,0x40209100,0x400b2000,0x40210000]:w(u,a,pattern)
 if ready:w(u,0x40004030,0x1000000)
 writes=[];calls=[];events=[];pending=[]
 def code(u,a,n,d):
  if native:a={sym['audio_gpio_pin_get']&~1:0x480eee,sym['audio_gpio_pin_set']&~1:0x480f0c,sym['audio_oscillator_control']&~1:0x4809c4}.get(a,a)
  if pending and a==pending[-1][0]:
   _,index=pending.pop();calls[index]['return']=u.reg_read(UC_ARM_REG_R0)
  if a in providers:
   name,count=providers[a];args=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3][:count]]
   if name=='mcuctrl':args[1]=bytes(u.mem_read(args[1],1)).hex()
   if name=='wait5':args.append(word(u,u.reg_read(UC_ARM_REG_SP)))
   calls.append(dict(name=name,args=args));pending.append((u.reg_read(UC_ARM_REG_LR)&~1,len(calls)-1))
 def write(u,ac,a,n,v,d):
  writes.append([a,n,v])
  if ready and a==0x40021004:w(u,0x40021008,v);events.append(['synthetic_device_status',v])
  if ready and a==0x4002100c:
   status=(v&~0xc0)|(0xc0 if v&0xc0 else 0);w(u,0x40021010,status);events.append(['synthetic_audio_status',status])
 def invalid(u,ac,a,n,v,d):raise AssertionError(('unmapped',native,hex(u.reg_read(UC_ARM_REG_PC)),hex(a),ac))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x4021ffff);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 u.reg_write(UC_ARM_REG_R5,scratch);u.reg_write(UC_ARM_REG_R0,scratch)
 try:u.emu_start((sym['clock_reset_recover'] if native else 0x44b158)|1,0x2007f000,count=5000000)
 except UcError as e:raise AssertionError(('runtime',native,flags,ref,hex(u.reg_read(UC_ARM_REG_PC)),e))
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',native,flags,ref,hex(u.reg_read(UC_ARM_REG_PC)))
 for c in calls:
  # Void/scratch returns are outside interface semantics.
  if c['name'] in ['delay','syspll_enable','syspll_disable','bus_flush']:c.pop('return',None)
 return dict(writes=writes,calls=calls,events=events,retained=word(u,0x40008858),primask=u.reg_read(UC_ARM_REG_PRIMASK))
