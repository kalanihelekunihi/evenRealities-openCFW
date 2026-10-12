from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-rb-remove-balance-round112'
SOURCES=[BASE/'root-cache-rb-insert-round111/rb_insert_candidate.c',ROOT/'components/audio/uart_thread_source_candidate/display_font_rb_core.c',DIR/'rb_balance_candidate.c',DIR/'rb_remove_candidate.c']
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
T=0x20001000;N=0x20002000;D=0x20004000;K=0x20006000;CB=0x600100;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_rb_remove',0x5c3600),('audio_uart_lv_cache_rb_leftmost_5c3798',0x5c3798),('audio_uart_lv_cache_rb_rotate_right_5c3860',0x5c3860),('audio_uart_lv_cache_rb_rotate_left_5c3896',0x5c3896),('audio_uart_font_rb_fix_insert',0x5c38cc),('audio_uart_font_rb_fix_remove',0x5c3976)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_lv_heap_alloc(unsigned n){return 0;} void audio_uart_lv_heap_free(void*p){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],*['-Wl,-u,'+name for name,address in providers]]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={CB:'compare'};cuts.update({(syms[s] if isc else a)&~1:op for op,s,a in [('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 counts={name:0 for name,address in providers}
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 def check(idx,args,variant=0,mutation=0):
  outs=[];name,address=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(T,W(N,CB|1,4));u.mem_write(N,bytes(4096));u.mem_write(D,bytes(4096))
   # Root black with black children and red grandchildren: bounded direct helper fixtures.
   for i in range(7):
    parent=0 if i==0 else N+((i-1)//2)*32
    left=N+(2*i+1)*32 if 2*i+1<7 else 0;right=N+(2*i+2)*32 if 2*i+2<7 else 0
    u.mem_write(N+i*32,W(parent,left,right,1 if i<3 else 0,D+i*32))
   if variant==1:u.mem_write(N,W(0,0,0,1,D))
   if variant==2:u.mem_write(T,W(0,CB|1,4))
   if variant==3:u.mem_write(N+32+12,bytes([2]));u.mem_write(N+64+12,bytes([255]))
   calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if op=='free':
     calls.append((op,r[0]))
     if mutation:uc.mem_write(r[0]+16,W(0x12345678))
    elif op=='log':
     sp=uc.reg_read(UC_ARM_REG_SP);fmt,expr,msg=struct.unpack('<III',uc.mem_read(sp,12));calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr),string(uc,msg)))
    else:raise AssertionError(op)
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((access,addr,size,value if access in [20,22] else None));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_INVALID,fault)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,value)
   try:u.emu_start((syms[name] if isc else address)|1,0x600000,count=20000)
   except UcError:assert faults,(name,args,variant,hex(u.reg_read(UC_ARM_REG_PC)))
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000,(name,args,variant)
   ret=u.reg_read(UC_ARM_REG_R0) if idx in [0,1] and not faults else None
   outs.append((calls,faults,ret,None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,12)),bytes(u.mem_read(N,4096))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(name,args,variant,mutation,outs);counts[name]+=1
 for idx in range(6):
  for variant in range(4):
   if idx==1:args=[N]
   elif idx==5:args=[T,N+96,N+32]
   elif idx==4:args=[T,N+96]
   else:args=[T,N]
   check(idx,args,variant)
  if idx==1:check(idx,[0])
  else:
   check(idx,[0,N,0]);check(idx,[T,0,0]);check(idx,[0,0,0])
 for node in [N,N+32,N+64,N+96,N+128,N+160,N+192]:
  check(0,[T,node],mutation=1);check(1,[node])
 for child,parent in [(0,0),(0,N+32),(N,0),(N+32,N),(N+96,N+32)]:check(5,[T,child,parent])
 receipt={'status':'PASS_COMPILED_ARM_RB_STANDALONE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Bounded direct fixtures plus null/malformed color/parent paths; native fault address/access/width and assertion log/fatal store compared.','Actual helper calls execute; heap free/logger are controlled cuts. Arbitrary aliasing, all malformed trees and hardware not proved.']};(DIR/'standalone-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
