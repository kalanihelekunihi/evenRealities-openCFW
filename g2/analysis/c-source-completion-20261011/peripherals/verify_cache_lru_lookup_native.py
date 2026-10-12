from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-lru-lookup-round107';SEL=ROOT/'components/audio/uart_thread_source_candidate';SRC=DIR/'lru_lookup_candidate.c';SOURCES=[SRC,SEL/'display_font_cache_entry.c',SEL/'display_lv_style_list.c',SEL/'display_timer_children.c'];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,R,D,L,K=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000;CMP=0x600100;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_lookup',0x5c2e4c),('audio_uart_lv_cache_lru_link_5c2be4',0x5c2be4),('audio_uart_lv_list_move_before_482d22',0x482d22)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_font_rb_find(void*a,const void*b){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={CMP:'compare'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('find','audio_uart_font_rb_find',0x5c3594),('remove','audio_uart_lv_list_remove',0x482c0e),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,head=L,found=R,cmp=0,node_size=24,offset=4,mutate=0,link_offset=0,link_data=D):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(C,bytes([0xa5])*68);u.mem_write(C+4,W(node_size));u.mem_write(C+16,W(CMP|1));u.mem_write(C+48,W(node_size+20));u.mem_write(C+52,W(offset,head,L+128));u.mem_write(R,bytes([0xa5])*192);u.mem_write(D,bytes([0xa5])*768);u.mem_write(L,bytes([0xa5])*192)
   for i in range(3):
    u.mem_write(R+64*i,W(0,0,0,0,D+256*i));u.mem_write(L+64*i,W(R+64*i));u.mem_write(L+64*i+offset,W(0 if i==0 else L+64*(i-1),0 if i==2 else L+64*(i+1)))
    for k in [0,24,28,64]:u.mem_write(D+256*i+k+16,W(L+64*i))
   if idx==1:u.mem_write(C+48,W(link_offset));u.mem_write(R+16,W(link_data))
   calls=[];faults=[]
   def word(p):return struct.unpack('<I',u.mem_read(p,4))[0]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0xdeadbeef
    if op=='compare':
     calls.append((op,*r[:2]));ret=cmp
     if mutate:uc.mem_write(C+4,W(node_size+4));uc.mem_write(C+56,W(L+64));uc.mem_write(R+16,W(D+256))
    elif op=='find':
     calls.append((op,*r[:2]));ret=found
     if mutate:uc.mem_write(C+4,W(64));uc.mem_write(C+48,W(84));uc.mem_write(C+56,W(L+64))
    elif op=='remove':
     calls.append((op,*r[:2]))
     if mutate==0:return # actual native/selected list-removal body executes
     off=word(r[0]);previous=word(r[1]+off);nxt=word(r[1]+off+4)
     if word(r[0]+4)==r[1]:uc.mem_write(r[0]+4,W(nxt))
     if word(r[0]+8)==r[1]:uc.mem_write(r[0]+8,W(previous))
     if previous:uc.mem_write(previous+off+4,W(nxt))
     if nxt:uc.mem_write(nxt+off,W(previous))
     if mutate==2:uc.mem_write(r[0],W(16));uc.mem_write(C+4,W(68));uc.mem_write((found if found else R)+16,W(D+512))
    else:
     fmt,expr,msg=struct.unpack('<III',uc.mem_read(sp,12));calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr),string(uc,msg)));ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=3000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults or idx==2 else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,68)),bytes(u.mem_read(R,192)),bytes(u.mem_read(D,768)),bytes(u.mem_read(L,192))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,head,found,cmp,node_size,offset,mutate,outs);counts[s]+=1
 for head,found,cmp,node_size,mutate,context in itertools.product([0,L],[0,R,R+64,R+128],[0,1,0x100,0xffffffff],[0,24,64],[0,1,2],[0,0xffffffff]):check(0,[C,K,context],head,found,cmp,node_size,mutate=mutate)
 for cache,key in [(0,0),(0,K),(C,0)]:check(0,[cache,key,0])
 for off,data in itertools.product([0,4,20,0x7fffffff,0x80000000,0xffffffff],[0,D,0xffffffff]):check(1,[C,R],link_offset=off,link_data=data)
 for node,before,offset,mutate in itertools.product([L,L+64,L+128],[0,L,L+64,L+128],[0,4,16],[0,1,2]):check(2,[C+52,node,before],offset=offset,mutate=mutate)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_LRU_LOOKUP_LINK_LIST_MOVE','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual entry-at,head/tail/previous list leaves execute; actual list removal executes for mutation0; controlled find/comparator/logger and mutation1/2 removal cuts.','Fast entry capture precedes comparator; fresh head/data/node size and post-remove link-offset writes compared.','Concrete RB/tree/heap/backend/data/layout/byte equality/hardware open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
