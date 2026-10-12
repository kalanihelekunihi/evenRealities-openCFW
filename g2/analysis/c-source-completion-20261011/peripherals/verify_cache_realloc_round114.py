from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-realloc-round114';SRC=DIR/'realloc_candidate.c';HEAP=ROOT/'components/audio/uart_thread_source_candidate/display_font_alloc.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
POOL=0x20000338;SLOT=0x2006f5ac;P=0x20002000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_lv_pool_realloc_484234',0x484234),('audio_uart_lv_pool_realloc_48432a',0x48432a),('audio_uart_lv_realloc_44f76a',0x44f76a)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('int xQueueSemaphoreTake(void*a,unsigned b){return 0;} int audio_uart_queue_send(void*a,void*b,unsigned c,unsigned d){return 0;} void*g2_file_pool_allocate(void*a,unsigned b){return 0;} void g2_file_pool_free(void*a,void*b){} void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){} void*g2_tlsf_reallocate_4d0868(void*a,void*b,unsigned c){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'fixture.elf'
 leaves=[ROOT/'components/audio/file_pool_free_candidate/tlsf_leaf.c',ROOT/'components/audio/file_pool_free_candidate/tlsf_absorb_leaves.c']
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],'-Wl,--defsym,audio_uart_lv_heap_pool='+hex(POOL),'-Wl,--defsym,audio_uart_lv_static_slot='+hex(SLOT)]+['-Wl,-u,'+s for s,n in providers]+[str(SRC),str(HEAP),*[str(p) for p in leaves],str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('take','xQueueSemaphoreTake',0x441c44),('send','audio_uart_queue_send',0x4417ee),('allocate','g2_file_pool_allocate',0x4d0722),('free','g2_file_pool_free',0x4d0808),('realloc','g2_tlsf_reallocate_4d0868',0x4d0868),('log','audio_uart_lvgl_log',0x44d25c)]};query=(syms['audio_uart_lv_allocation_size_4d05e4'] if isc else 0x4d05e4)&~1;engines.append((u,cuts,isc,query))
 counts={s:0 for s,n in providers}
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 def check(idx,ptr,size,take,result,used,offset,mutate):
  outs=[];name,address=providers[idx];observe_query=idx!=2 or (size!=0 and ptr!=SLOT)
  for u,cuts,isc,query in engines:
   u.mem_write(POOL,W(0x20007000,0x20008000,used,48));u.mem_write(P-128,bytes([0xa5])*512);u.mem_write(P-offset+4,W(27));u.mem_write(P+64-offset+4,W(43));u.mem_write(0x78f4c0,W(offset));u.mem_write(0x78f4b4,W(1));u.mem_write(0x78f4b8,W(2));calls=[];queries=0
   def hook(uc,addr,n,user):
    nonlocal queries
    r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if addr==query:
     if not observe_query:return
     calls.append(('size-query',r[0],bytes(uc.mem_read(POOL,16)).hex()));queries+=1
     if mutate==3 and queries==2:uc.mem_write(POOL+8,W(100))
     return
    if addr not in cuts:return
    op=cuts[addr];ret=0
    if op=='take':calls.append((op,*r[:2]));ret=take
    elif op=='send':calls.append((op,*r));ret=1
    elif op=='allocate':calls.append((op,*r[:2]));ret=result
    elif op=='realloc':calls.append((op,*r[:3]));ret=result
    elif op=='free':calls.append((op,*r[:2]))
    elif op=='zero':calls.append((op,*r[:3]));uc.mem_write(r[0],bytes([r[1]&255])*r[2])
    elif op=='log':
     fmt=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0];calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt)));ret=0x12345678
    if mutate in [1,2] and op in ['take','allocate','free','realloc']:uc.mem_write(POOL,W(0x20007100,0x20008100,0xfffffff0 if mutate==2 else 64,80))
    uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   args=[POOL,ptr,size] if idx==0 else [ptr,size]
   for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
   u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(POOL,16)),bytes(u.mem_read(P-128,512))));u.hook_del(h)
  assert outs[0]==outs[1],(name,ptr,size,take,result,used,offset,mutate,outs);counts[name]+=1
 for idx in range(3):
  for ptr,size,take,result,used,offset,mutate in itertools.product([0,P,SLOT],[0,1,64],[0,1,2],[0,P,P+64],[0,32,0xfffffff0],[0,8,16],[0,1,2,3]):
   if idx!=2 and ptr==SLOT:continue
   check(idx,ptr,size,take,result,used,offset,mutate)
 receipt={'status':'PASS_COMPILED_ARM_REALLOC_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'selected_heap_sha256':hashlib.sha256(HEAP.read_bytes()).hexdigest(),'selected_leaf_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in leaves},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual heap malloc/free/pool,size-query,pointer/block helpers execute. TLSF alloc/free/realloc,semaphore/logger controlled cuts.','Accounting state observed at actual size-query entry and mutated there; header offsets0/8/16,word wrap,NULL/static slot,failures,log result preservation compared. Full TLSF heap/scheduler/image/hardware gates open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
