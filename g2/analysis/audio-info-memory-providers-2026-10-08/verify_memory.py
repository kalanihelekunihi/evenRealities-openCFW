from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
def run(native,kind,cfg,old=0,mode=2,callback=0,otp_mismatch=0,pattern=0,mask=0):
 u=machine();u.mem_write(0x20006000,bytes(cfg)+b'\xa5'*3);u.reg_write(UC_ARM_REG_R0,0x20006000);u.reg_write(UC_ARM_REG_PRIMASK,mask);w(u,0x40021108,3<<4);w(u,0x2005665c,0);w(u,0x20073274,0x5a490d if callback else 0)
 w(u,0x40021018,old if kind=='mcu' else 0);w(u,0x40021014,(old&7)|(old&8)|((old>>2)&16)|((old>>2)&32));w(u,0x40021024,old if kind=='sram' else 0);w(u,0x40021028,old if kind=='sram' else 0)
 w(u,0x40021008,otp_mismatch<<27);w(u,0x40021004,0)
 for a in [0x4002101c,0x4002102c,0x40021040,0x40020284]:w(u,a,pattern)
 writes=[];calls=[];events=[];changes=0;pending=[]
 def code(u,a,n,d):
  if pending and a==pending[-1][0]:_,index=pending.pop();calls[index]['return']=u.reg_read(UC_ARM_REG_R0)
  if a==0x480826:
   calls.append(dict(name='wait',args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+[word(u,u.reg_read(UC_ARM_REG_SP))]));pending.append((u.reg_read(UC_ARM_REG_LR)&~1,len(calls)-1))
  if a==0x480312:
   ptr=u.reg_read(UC_ARM_REG_R2);calls.append(dict(name='dispatch',args=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),word(u,ptr) if ptr else None]));pending.append((u.reg_read(UC_ARM_REG_LR)&~1,len(calls)-1))
 def write(u,ac,a,n,v,d):
  nonlocal changes
  writes.append([a,n,v&((1<<(8*n))-1)])
  if a in [0x40021014,0x40021024]:
   changes+=1
   if mode==2 or (mode==1 and changes==1):
    if a==0x40021014:status=(v&7)|(v&8)|((v&16)<<2)|((v&32)<<2);w(u,0x40021018,status)
    else:status=v&7;w(u,0x40021028,status)
    events.append(['synthetic_memory_status',a,status])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40020000,end=0x40021fff);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x20074f62,end=0x20074f62)
 u.emu_start((sym['audio_'+('mcu_memory_config' if kind=='mcu' else 'sram_config')] if native else (0x47f204 if kind=='mcu' else 0x47f46a))|1,0x2007f000,count=3000000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',kind,native)
 return dict(status=u.reg_read(UC_ARM_REG_R0),writes=writes,calls=calls,events=events,rom_cached=bytes(u.mem_read(0x20074f62,1)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK),force_axi=word(u,0x40020284))
rows=[]
def compare(kind,case):
 o=run(False,kind,**case);n=run(True,kind,**case);assert o==n,(kind,case,o,n);rows.append(dict(function=kind,inputs=case,**o))
for rom,dtcm,nvm,old in itertools.product([0,1],[0,1,7],[0,1,3],[0,7,8,72,128,207]):compare('mcu',dict(cfg=[rom,dtcm,0,nvm,0],old=old))
for mode,callback,retain,keep,otp in itertools.product([0,1,2],[0,1],[0,1,2],[0,1],[0,1]):compare('mcu',dict(cfg=[1,0,retain,3,keep],old=139,mode=mode,callback=callback,otp_mismatch=otp,mask=1))
for rom,nvm in itertools.product([2,255],[2,255]):compare('mcu',dict(cfg=[rom,255,2,nvm,255],old=207,pattern=0xffffffff))
for active,old,retain,callback,mode in itertools.product([0,1,3,7,8,255],[0,1,3,7],[0,1,3,7,2],[0,1],[0,2]):compare('sram',dict(cfg=[active,1,3,7,retain],old=old,callback=callback,mode=mode,mask=1))
(D/'memory-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=verified_elf_sha256(),comparisons=rows,limits=['Actual wait/dispatcher/control provider executes; optional real control returns calibration error1.','Memory status translation/write response is synthetic; first/second phase readiness are explicit fixtures.','No physical power gating or usable executing-memory placement proof.']),separators=(',',':'))+'\n');print('PASS',len(rows),'memory provider comparisons')
