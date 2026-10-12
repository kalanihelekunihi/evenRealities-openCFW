from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-lru-remove-capacity-round108';SEL=ROOT/'components/audio/uart_thread_source_candidate';SOURCES=[DIR/'lru_remove_candidate.c',DIR/'lru_capacity_candidate.c',SEL/'display_font_lru_lookup.c',SEL/'display_font_cache_entry.c',SEL/'display_lv_style_list.c',SEL/'display_timer_children.c'];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,R,D,L,K=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000;SIZE,SIZE2,FREE=0x600100,0x600104,0x600108;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_remove',0x5c2fd4),('audio_uart_font_lru_evict',0x5c3098),('audio_uart_font_lru_get_victim',0x5c3222),('audio_uart_font_lru_reserve',0x5c328a)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_font_rb_find(void*a,const void*b){return 0;} void*audio_uart_font_rb_remove(void*a,void*b){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){} unsigned char audio_uart_lv_heap_pool[128]; int xQueueSemaphoreTake(void*a,unsigned b){return 0;} unsigned g2_tlsf_block_size(void*a){return 0;} void g2_file_pool_free(void*a,void*b){} int audio_uart_queue_send(void*a,const void*b,unsigned c,unsigned d){return 0;}');elf=td/'test.elf'
 # timer child owns canonical heap free; cut its body in both engines.
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={SIZE:'size',SIZE2:'size2',FREE:'destroy'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('find','audio_uart_font_rb_find',0x5c3594),('remove','audio_uart_font_rb_remove',0x5c3600),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,found=R,current=32,maximum=32,delta=1,mutate=0,refs=(0,0,0),tail=L+128):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   words=[0xa5a5a5a5]*17;words[1]=24;words[2]=maximum;words[3]=current;words[6]=FREE|1;words[12]=44;words[13]=4;words[14]=L;words[15]=tail;words[16]=SIZE|1;u.mem_write(C,W(*words));u.mem_write(R,bytes([0xa5])*192);u.mem_write(D,bytes([0xa5])*768);u.mem_write(L,bytes([0xa5])*192)
   for i in range(3):
    data=D+256*i;u.mem_write(R+64*i,W(0,0,0,0,data));u.mem_write(L+64*i,W(R+64*i,0 if i==0 else L+64*(i-1),0 if i==2 else L+64*(i+1)))
    for off in [24,64]:u.mem_write(data+off,W(0,refs[i],off,0))
    u.mem_write(data+40,W(L+64*i));u.mem_write(data+80,W(L+64*i))
   calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0xdeadbeef
    if op=='find':
     calls.append((op,*r[:2]));ret=found
     if mutate:uc.mem_write(C+16,W(0x12345678));uc.mem_write(C+64,W(SIZE2|1))
    elif op=='destroy':
     calls.append((op,*r[:2]))
     if mutate:uc.mem_write(C+4,W(64));uc.mem_write(C+48,W(84));uc.mem_write(C+64,W(SIZE2|1));uc.mem_write((found if found else R)+16,W(D+256))
    elif op.startswith('size'):
     calls.append((op,r[0]));ret=delta
     if mutate:uc.mem_write(C+8,W(0 if mutate==2 else 65));uc.mem_write(C+12,W(0xfedcba98))
    elif op=='remove':
     calls.append((op,*r[:2]));ret=D
     if mutate:uc.mem_write(C+12,W(0xabcdef01))
    elif op=='free':
     calls.append((op,r[0]));assert D<=r[0]<D+768 or L<=r[0]<L+192,(op,hex(r[0]));uc.mem_write(r[0],bytes([0xdd])*16)
     if mutate:uc.mem_write(C+64,W(SIZE2|1));uc.mem_write(C+12,W(0x87654321))
    else:
     fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt))
     if r[2]==450:item+=struct.unpack('<II',uc.mem_read(sp+4,8))
     else:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     calls.append(item);ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=5000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults or idx<2 else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,68)),bytes(u.mem_read(R,192)),bytes(u.mem_read(D,768)),bytes(u.mem_read(L,192))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,found,current,maximum,delta,mutate,refs,tail,outs);counts[s]+=1
 for idx,found,current,delta,mutate,context in itertools.product(range(2),[0,R,R+64],[0,32,0xffffffff],[0,1,0x100,0xffffffff],[0,1,2],[0,0xffffffff]):check(idx,[C,D+24 if idx==0 else K,context],found,current,delta=delta,mutate=mutate)
 for idx in range(2):
  for cache,key in [(0,0),(0,D+24),(C,0)]:check(idx,[cache,key,0])
 for tail,refs,context in itertools.product([0,L,L+64,L+128],[(0,0,0),(1,0,1),(1,1,0),(1,1,1),(0xffffffff,0x80000000,1)],[0,0xffffffff]):check(2,[C,context],refs=refs,tail=tail)
 check(2,[0,0])
 for data,maximum,current,delta,extra,mutate,context in itertools.product([0,K],[0,1,32,0xffffffff],[0,32,0xffffffff],[0,1,32,0xffffffff],[0,1,0xffffffff],[0,1,2],[0,0xffffffff]):check(3,[C,data,extra,context],current=current,maximum=maximum,delta=delta,mutate=mutate)
 check(3,[0,0,0,0])
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_LRU_REMOVE_EVICT_VICTIM_RESERVE','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual cache info/entry-at/delete/ref,link helper and list removal/head/tail/previous execute. RB find/remove,heap free,destroy/size callbacks/logger are controlled child cuts with field mutations.','Full32bit size/delta/ref and wrapped sums/subtractions tested; void scratch ignored.','Concrete insertion/RB/backend/heap/data/full-image/layout/byte equality/hardware remain open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
