from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'verify_clock.py').read_text().split('rows=[]')[0],str(D/'verify_clock.py'),'exec'))
def common(native,major=0x21,revision=2,stored=0,trace=1,valid=1,shadow=0,flags=0,ref=0,ready=1,scratch=0,poa=0):
 u=machine();w(u,0x4002000c,major);w(u,0x200001e8,revision);w(u,0x20071948,0x1f01600d if valid else 0);w(u,0x400201bc,shadow<<3);w(u,0x40021108,3<<4);w(u,0x40008858,0x5af00000|flags|(ref<<6));w(u,0x4000885c,poa<<1)
 u.mem_write(0x20074f5e,bytes([trace]));u.mem_write(0x20074f63,bytes([stored]));w(u,0x2007197c,0);w(u,0x2007198c,0)
 if ready:w(u,0x40004030,0x1000000)
 writes=[];calls=[];events=[];pending_gpio=[]
 extra={0x4d403e:('trace_disable',0),0x47f954:('info_populate',0),0x47f90c:('peripheral_enabled',1),0x47ffc4:('cpdlp_config',1),0x47ef38:('revision',0),0x4d3f3c:('info_read',3),0x480434:('register_callbacks',0),0x47f204:('mcu_memory',1),0x47f46a:('sram_config',1),0x473940:('save_irq',0),0x4803c2:('ton_update',2)}
 def code(u,a,n,d):
  if pending_gpio and a==pending_gpio[-1][0]:
   _,index=pending_gpio.pop();calls[index]['return']=u.reg_read(UC_ARM_REG_R0)
  if native:a={sym['audio_gpio_pin_get']&~1:0x480eee,sym['audio_gpio_pin_set']&~1:0x480f0c}.get(a,a)
  entries=dict(providers,**{})
  entries.update(extra)
  if a in entries:
   name,count=entries[a];args=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3][:count]]
   if name=='mcuctrl':args[1]=bytes(u.mem_read(args[1],1)).hex()
   if name=='wait5':args.append(word(u,u.reg_read(UC_ARM_REG_SP)))
   calls.append(dict(name=name,args=args))
   if name in ['pin_get','pin_set']:pending_gpio.append((u.reg_read(UC_ARM_REG_LR)&~1,len(calls)-1))
 def write(u,ac,a,n,v,d):
  writes.append([a,n,v])
  if ready and a==0x40021004:w(u,0x40021008,v);events.append(['synthetic_device_status',v])
  if ready and a==0x4002100c:
   status=(v&~0xc0)|(0xc0 if v&0xc0 else 0);w(u,0x40021010,status);events.append(['synthetic_audio_status',status])
 def invalid(u,ac,a,n,v,d):raise AssertionError(('unmapped',native,hex(u.reg_read(UC_ARM_REG_PC)),hex(a),ac))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x4021ffff);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 u.reg_write(UC_ARM_REG_R5,scratch);u.reg_write(UC_ARM_REG_R0,scratch)
 try:u.emu_start((sym['pcm_common_low_power_initialize'] if native else 0x47fae8)|1,0x2007f000,count=7000000)
 except UcError as e:raise AssertionError(('runtime',native,hex(u.reg_read(UC_ARM_REG_PC)),[hex(u.reg_read(r)) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]],calls[-6:],e))
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',native,hex(u.reg_read(UC_ARM_REG_PC)))
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,events=events,retained=word(u,0x40008858),flags=bytes(u.mem_read(0x20074f60,32)).hex(),cache=bytes(u.mem_read(0x2007426c,64)).hex(),ton_cache=bytes(u.mem_read(0x2000453a,6)).hex(),callback_table=bytes(u.mem_read(0x20073270,60)).hex(),info1=bytes(u.mem_read(0x20071948,128)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for stored,scratch,ready,ref in itertools.product([0,1],[0,0x12345678,2<<10,3<<10,0xffffffff],[0,1],[0,1]):
 case=dict(stored=stored,scratch=scratch,ready=ready,ref=ref,flags=16);o=common(False,**case);n=common(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'prefix-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Full common initializer native control flow; original revision/INFO1/register/memory/clock providers remain.','Synthetic calibration/readiness and retained state; no real factory/physical boot proof.']),separators=(',',':'))+'\n');print('PASS',len(rows),'common initializer comparisons')
