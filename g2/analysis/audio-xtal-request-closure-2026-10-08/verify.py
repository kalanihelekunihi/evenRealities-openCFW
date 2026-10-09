from pathlib import Path
import itertools,json
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def invoke(u,a,args):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(a|1,0x2007f000,count=3000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;return u.reg_read(UC_ARM_REG_R0)
def norm(v):return 'local_stack' if 0x2007dc00<=v<0x2007e000 else v
addresses={'request':0x4c3d9e,'wait':0x4c3d70,'counter':0x4c387e,'board':0x4c45e2}
names={'request':'audio_xtal_request','wait':'audio_xtal_wait','counter':'audio_clock_counter_wait','board':'audio_clock_board_set'}
def run(native,kind='request',user=52,board_mode=0,hz=24000000,control=0,already=0,flag=0,counter=3,mask=0,clear_delay=0,pattern=0,nonnull=1):
 u=machine();u.reg_write(UC_ARM_REG_PRIMASK,mask);u.mem_write(0x20073324,b'\0'*56);u.mem_write(0x200001cc,bytes([board_mode])+b'\0'*3);w(u,0x200001d0,hz);w(u,0x4002012c,control);w(u,0x40020128,0x12345678);u.mem_write(0x20074f56,bytes([flag]));w(u,0x20074260,0x20006100);w(u,0x20006100,counter)
 if already and (user&255)<64:w(u,0x20073334+4*((user&255)>>5),1<<(user&31))
 writes=[];delays=[];events=[]
 def code(u,a,n,d):
  if a==0x4807a0:
   delays.append(u.reg_read(UC_ARM_REG_R0))
   if clear_delay and len(delays)==clear_delay:u.mem_write(0x20074f56,b'\0');events.append(['synthetic_flag_clear',clear_delay])
 def wr(u,ac,a,n,v,d):
  if a==0x20074260:v=norm(v)
  writes.append([a,n,v])
 u.hook_add(UC_HOOK_CODE,code)
 for a,b in [(0x20073324,0x2007335b),(0x20074f56,0x20074f56),(0x20074260,0x20074263),(0x40020128,0x4002012f)]:u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=a,end=b)
 if kind=='request':args=[user]
 elif kind=='wait':args=[0x20006100]
 elif kind=='counter':args=[0x20074f56,0x20006100]
 else:
  u.mem_write(0x20006000,bytes((i^pattern)&255 for i in range(24)));u.mem_write(0x200001cc,b'\xa5'*24);args=[0x20006000 if nonnull else 0]
 status=invoke(u,sym[names[kind]] if native else addresses[kind],args)
 return dict(status=status if kind in ['request','board'] else None,writes=writes,delays=delays,events=events,table=bytes(u.mem_read(0x20073324,56)).hex(),flag=bytes(u.mem_read(0x20074f56,1)).hex(),pointer=norm(word(u,0x20074260)),counter=word(u,0x20006100),board=bytes(u.mem_read(0x200001cc,24)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
def compare(c):
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for board_mode,control,user,already,flag,mask in itertools.product([0,1,2],[0,1,256,257],[0,52,56],[0,1],[0,1],[0,1]):compare(dict(board_mode=board_mode,control=control,user=user,already=already,flag=flag,mask=mask))
for user,flag,hz in itertools.product([52,57,256],[0,1],[0,24000000]):compare(dict(user=user,flag=flag,hz=hz))
for kind,flag,counter,mask,clear_delay in itertools.product(['wait','counter'],[0,1],[0,1,3,150],[0,1],[0,1,3]):compare(dict(kind=kind,flag=flag,counter=counter,mask=mask,clear_delay=clear_delay))
for nonnull,pattern,mask in itertools.product([0,1],[0,255],[0,1]):compare(dict(kind='board',nonnull=nonnull,pattern=pattern,mask=mask))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Original oscillator/delay/IRQ-save providers execute without return stubs.','Local stack pointer identity normalized; local frame addresses and void return scratch registers are not compared.','Software flag clear occurs synchronously at a chosen delay entry and is synthetic, not IRQ concurrency.','No physical-ready check or measured clock settling.']),separators=(',',':'))+'\n');print('PASS',len(rows),'XTAL/request/wait/board comparisons')
