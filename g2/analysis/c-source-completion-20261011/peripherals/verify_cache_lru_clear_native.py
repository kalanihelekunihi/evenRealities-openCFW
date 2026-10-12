from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-lru-clear-round109';SEL=ROOT/'components/audio/uart_thread_source_candidate';SOURCES=[DIR/'lru_clear_candidate.c',SEL/'display_font_cache_entry.c',SEL/'display_font_rb_core.c',SEL/'display_timer_children.c'];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,R,D,L=0x20001000,0x20002000,0x20003000,0x20004000;FREE,FREE2,CUSTOM=0x600100,0x600104,0x600108;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_clear',0x5c315a),('audio_uart_lv_list_clear_custom_482c9a',0x482c9a),('audio_uart_font_lru_list_clear',0x482da4)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){} unsigned char audio_uart_lv_heap_pool[128]; int xQueueSemaphoreTake(void*a,unsigned b){return 0;} unsigned g2_tlsf_block_size(void*a){return 0;} void g2_file_pool_free(void*a,void*b){} int audio_uart_queue_send(void*a,const void*b,unsigned c,unsigned d){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={FREE:'destroy',FREE2:'destroy2',CUSTOM:'custom'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('ref','audio_uart_font_cache_has_owner',0x4d5312),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,count=3,refs=(0,0,0),mutate=0):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   words=[0xa5a5a5a5]*17;words[1]=24;words[3]=0x12345678;words[6]=FREE|1;words[10]=R if count else 0;words[13]=4;words[14]=L if count else 0;words[15]=L+64*(count-1) if count else 0;u.mem_write(C,W(*words));u.mem_write(R,bytes([0xa5])*192);u.mem_write(D,bytes([0xa5])*768);u.mem_write(L,bytes([0xa5])*192)
   for i in range(count):
    u.mem_write(R+64*i,W(0 if i==0 else R,R+64 if i==0 and count>1 else 0,R+128 if i==0 and count>2 else 0,0,D+256*i));u.mem_write(L+64*i,W(R+64*i))
    for off in [4,16]:u.mem_write(L+64*i+off,W(L+64*(i-1) if i else 0,L+64*(i+1) if i+1<count else 0))
    for off in [24,64]:u.mem_write(D+256*i+off,W(0,refs[i],off,0))
   calls=[];faults=[];ref_calls={}
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0xdeadbeef
    if op=='ref':
     calls.append((op,r[0]));ref_calls[r[0]]=ref_calls.get(r[0],0)+1
     if mutate and ref_calls[r[0]]==2:uc.mem_write(r[0]+4,W(0x87654321))
     return # actual accessor executes, including this changed second read
    if op.startswith('destroy'):
     calls.append((op,*r[:2]))
     if mutate:uc.mem_write(C+4,W(64));uc.mem_write(C+24,W(FREE2|1))
    elif op=='custom':
     calls.append((op,r[0]))
     if mutate:uc.mem_write(r[0]+8,W(0));uc.mem_write(C+52,W(16));uc.mem_write(r[0]+16,W(0x12345678))
    elif op=='free':
     calls.append((op,r[0]));assert R<=r[0]<R+192 or D<=r[0]<D+768 or L<=r[0]<L+192
     uc.mem_write(r[0],bytes([0xdd])*16)
     if mutate:uc.mem_write(C+12,W(0xabcdef01))
    else:
     fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt))
     if r[2]==401:item+=struct.unpack('<II',uc.mem_read(sp+4,8))
     elif r[2]==406:item+=(struct.unpack('<I',uc.mem_read(sp+4,4))[0],)
     else:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     calls.append(item);ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=10000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,68)),bytes(u.mem_read(R,192)),bytes(u.mem_read(D,768)),bytes(u.mem_read(L,192))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,count,refs,mutate,outs);counts[s]+=1
 for count,refs,mutate,context in itertools.product(range(4),[(0,0,0),(1,0,1),(1,1,1),(0xffffffff,0x80000000,1)],[0,1,2],[0,0xffffffff]):check(0,[C,context],count,refs,mutate)
 check(0,[0,0])
 for count,callback,mutate in itertools.product(range(4),[0,CUSTOM|1],[0,1,2]):check(1,[C+52,callback],count,mutate=mutate)
 for callback in [0,CUSTOM|1]:check(1,[0,callback])
 for count,mutate in itertools.product(range(4),[0,1,2]):check(2,[C+52],count,mutate=mutate)
 check(2,[0])
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_LRU_CLEAR_CUSTOM_LIST_CLEANUP','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual tree clear,cache-entry accessors and list first/next/removal execute. Free/logger/custom callbacks controlled cuts; second ref accessor executes after memory mutation.','Empty/one/two/three node trees/lists,full-width refs,context forwarding,saved-next custom cleanup verified; void scratch ignored.','Concrete insert/remove/rotation/heap/data/full-image/layout/byte equality/hardware remain open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
