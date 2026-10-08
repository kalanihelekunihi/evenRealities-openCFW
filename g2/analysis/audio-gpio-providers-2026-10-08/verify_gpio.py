from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def run(native,kind,pin,cfg,mask=0,null=False):
 u=machine();w(u,0x20006000,0xa5a5a5a5)
 for i in range(224):w(u,0x40010000+4*i,(cfg^i)&0xffffffff)
 w(u,0x40010400,0x12345678);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_R0,pin);u.reg_write(UC_ARM_REG_R1,(0 if null else 0x20006000) if kind=='get' else cfg);writes=[];calls=[]
 def write(u,ac,a,n,v,d):writes.append([a,n,v])
 def code(u,a,n,d):
  if a==0x473940:calls.append('save_irq')
 u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40010000,end=0x40010fff);u.hook_add(UC_HOOK_CODE,code)
 u.emu_start((sym['audio_gpio_pin_'+kind] if native else (0x480eee if kind=='get' else 0x480f0c))|1,0x2007f000,count=10000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 return dict(status=u.reg_read(UC_ARM_REG_R0),output=word(u,0x20006000),writes=writes,calls=calls,primask=u.reg_read(UC_ARM_REG_PRIMASK),padkey=word(u,0x40010400))
rows=[]
def compare(kind,pin,cfg,mask=0,null=False):
 o=run(False,kind,pin,cfg,mask,null);n=run(True,kind,pin,cfg,mask,null);assert o==n,(kind,pin,cfg,mask,null,o,n);rows.append(dict(kind=kind,pin=pin,cfg=cfg,mask=mask,null=null,output=o))
for pin,drive in itertools.product(range(224),range(4)):compare('set',pin,0x8000000a|(drive<<10),pin&1)
# Every extended-drive pad, all pull encodings; full-word preservation.
extended=[0,0x3fe0,0x3ff,0x1ffbfe00,0x7c000,0,0]
for pin,pull in itertools.product([p for p in range(224) if extended[p>>5]&(1<<(p&31))],range(8)):compare('set',pin,0x80001c0a|(pull<<13),pin&1)
for pin,mask,cfg in itertools.product([15,224,255,256,0xffffffff],[0,1],[0,0xffffffff,0x12345678,2<<10,3<<10,4<<10]):compare('set',pin,cfg,mask)
for pin,null,mask,cfg in itertools.product([0,15,223,224,0xffffffff],[False,True],[0,1],[0,0xffffffff,0x12345678]):compare('get',pin,cfg,mask,null)
(D/'gpio-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),counts={kind:sum(r['kind']==kind for r in rows) for kind in ['get','set']},comparisons=rows,limits=['Original IRQ-save executes; native and original restore PRIMASK.','Synthetic GPIO words/PADKEY; no electrical, mux-clock or real exception proof.']),separators=(',',':'))+'\n');print('PASS',len(rows),'GPIO provider comparisons')
