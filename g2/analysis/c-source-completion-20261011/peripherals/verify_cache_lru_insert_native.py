from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-lru-insert-round110';SEL=ROOT/'components/audio/uart_thread_source_candidate';SRC=DIR/'lru_insert_candidate.c';SOURCES=[SRC,SEL/'display_font_lru_lookup.c',SEL/'display_font_cache_entry.c',SEL/'display_font_rb_core.c'];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,R,D,L,K=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_insert',0x5c2b00),('audio_uart_lv_list_prepend_482b12',0x482b12)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_lv_malloc(unsigned n){return 0;} void*audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;} void*audio_uart_font_rb_alloc_insert(void*a,const void*b){return 0;} void*audio_uart_font_rb_remove(void*a,void*b){return 0;} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],'-Wl,-u,'+providers[1][0]]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('malloc','audio_uart_lv_malloc',0x44f718),('copy','audio_uart_lv_grid_copy_454738',0x454738),('insert','audio_uart_font_rb_alloc_insert',0x5c34e4),('remove','audio_uart_font_rb_remove',0x5c3600),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]};engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,rb_result=R,allocated=L,size=24,head=0,offset=4,mutate=0,removed=D):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   words=[0xa5a5a5a5]*17;words[1]=size;words[12]=size+20;words[13]=offset;words[14]=head;words[15]=head;u.mem_write(C,W(*words));u.mem_write(R,W(0,0,0,0,D));u.mem_write(D,bytes([0xa5])*512);u.mem_write(L,bytes([0xa5])*192);u.mem_write(K,bytes(range(128)));calls=[];faults=[];copies=0
   def hook(uc,addr,width,user):
    nonlocal copies
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0xdeadbeef
    if op=='insert':calls.append((op,*r[:2]));ret=rb_result
    elif op=='malloc':
     calls.append((op,r[0]));ret=allocated
     if mutate:uc.mem_write(C+52,W(16));uc.mem_write(C+56,W(L+64));uc.mem_write(C+60,W(L+64))
    elif op=='copy':
     payload=bytes(uc.mem_read(r[1],r[2]));stack=0x200fe000<=r[1]<0x20100000;calls.append((op,r[0],'stack_word' if stack else r[1],r[2],payload.hex()));uc.mem_write(r[0],payload);ret=r[0];copies+=1
     if mutate==1 and copies==1:uc.mem_write(C+4,W(64));uc.mem_write(C+48,W(84));uc.mem_write(R+16,W(D+256))
     if mutate==2 and copies==2:uc.mem_write(C+48,W(84));uc.mem_write(R+16,W(D+256))
     if mutate and copies==3:uc.mem_write(C+4,W(68))
    elif op=='remove':calls.append((op,*r[:2]));ret=removed
    elif op=='free':calls.append((op,r[0]));assert r[0]==D;uc.mem_write(D,bytes([0xdd])*16)
    else:
     fmt,expr,msg=struct.unpack('<III',uc.mem_read(sp,12));calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr),string(uc,msg)));ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=5000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,68)),bytes(u.mem_read(R,20)),bytes(u.mem_read(D,512)),bytes(u.mem_read(L,192))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,rb_result,allocated,size,head,offset,mutate,removed,outs);counts[s]+=1
 for rb,alloc,size,head,mutate,removed in itertools.product([0,R],[0,L],[0,1,24,64],[0,L+64],[0,1,2],[0,D]):check(0,[C,K],rb,alloc,size,head,mutate=mutate,removed=removed)
 for cache,key in [(0,0),(0,K),(C,0)]:check(0,[cache,key])
 for alloc,head,offset,mutate in itertools.product([0,L],[0,L+64],[0,4,16,0xfffffff8],[0,1,2]):
  # Wrapped allocation length is valid; only successful mapped link offsets execute.
  if alloc and offset==0xfffffff8:continue
  check(1,[C+52],allocated=alloc,head=head,offset=offset,mutate=mutate)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_LRU_INSERT_LIST_PREPEND','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual entry-at/init,link helper,list-prepend and RB erase execute; RB allocate/remove,malloc,copy,heap free,logger controlled cuts.','All three copies retain native call order; stack pointer words normalized by contents,callback field changes and allocation-failure rollback tested.','Concrete RB insertion/removal/rotations,heap/data/layout/byte equality/hardware remain open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
