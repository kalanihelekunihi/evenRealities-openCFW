from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-connected-heap-round115';DIR.mkdir(exist_ok=True)
SOURCES=[ROOT/'components/audio/uart_thread_source_candidate'/name for name in ['display_font_rb_insert.c','display_font_rb_core.c','display_font_rb_balance.c','display_font_rb_remove.c','display_font_alloc.c']]+[ROOT/'components/audio/file_pool_free_candidate'/name for name in ['tlsf_leaf.c','tlsf_absorb_leaves.c']]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
T=0x20001000;N=0x20002000;D=0x20004000;K=0x20006000;CB=0x600100;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_rb_alloc_insert',0x5c34e4),('audio_uart_font_rb_remove',0x5c3600)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*g2_file_pool_allocate(void*p,unsigned n){return 0;} void g2_file_pool_free(void*p,void*d){} int xQueueSemaphoreTake(void*p,unsigned n){return 0;} int audio_uart_queue_send(void*p,void*d,unsigned n,unsigned m){return 0;} void audio_uart_lv_basic_box_clear_454746(void*p,unsigned n,unsigned m){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],'-Wl,-u,'+providers[1][0],'-Wl,--defsym,audio_uart_lv_heap_pool=0x20000338','-Wl,--defsym,audio_uart_lv_static_slot=0x2006f5ac']+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={CB:'compare'};cuts.update({(syms[s] if isc else a)&~1:op for op,s,a in [('alloc','g2_file_pool_allocate',0x4d0722),('free','g2_file_pool_free',0x4d0808),('take','xQueueSemaphoreTake',0x441c44),('send','audio_uart_queue_send',0x4417ee),('zero','audio_uart_lv_basic_box_clear_454746',0x454746),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 counts={'insert':0,'remove':0};coverage=set()
 for seed in range(100):
  rng=random.Random(seed);keys=list(range(24));rng.shuffle(keys);removal=list(keys);rng.shuffle(removal);allocated={};nextalloc=0
  for u,_,_ in engines:
   u.mem_write(T,W(0,CB|1,4));u.mem_write(N-16,bytes(4112));u.mem_write(D-16,bytes(4112));u.mem_write(0x20000338,W(0x20007000,0x20008000,0,0));u.mem_write(0x78f4c0,W(8));u.mem_write(0x78f4b4,W(1));u.mem_write(0x78f4b8,W(2))
  for phase,sequence in [(0,keys),(1,removal)]:
   for key in sequence:
    outs=[]
    for u,cuts,isc in engines:
     calls=[]
     def read(p):return struct.unpack('<I',u.mem_read(p,4))[0]
     def hook(uc,addr,size,user):
      if not isc and 0x5c3600<=addr<0x5c3abc:coverage.add(addr)
      if addr not in cuts:return
      op=cuts[addr];a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);ret=0
      if op=='compare':ret=(read(a)>read(b))-(read(a)<read(b));calls.append((op,read(a),read(b)))
      elif op=='alloc':
       ix=sum(1 for c in calls if c[0]=='alloc');ret=N+nextalloc*32 if ix==0 else D+nextalloc*32;calls.append((op,a,b,ret));uc.mem_write(ret-4,W((b+3)&~3))
      elif op=='free':calls.append((op,a,b))
      elif op=='take':calls.append((op,a,b));ret=1
      elif op=='send':calls.append((op,a,b,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)));ret=1
      elif op=='zero':
       length=uc.reg_read(UC_ARM_REG_R2);calls.append((op,a,b,length));uc.mem_write(a,bytes([b&255])*length)
      else:raise AssertionError(('unexpected log',seed,phase,key))
      uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     h=u.hook_add(UC_HOOK_CODE,hook);u.mem_write(K,W(key));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_R1,K if phase==0 else allocated[key]);s,a=providers[phase]
     u.emu_start((syms[s] if isc else a)|1,0x600000,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
     ret=u.reg_read(UC_ARM_REG_R0)
     if phase==0:assert ret==N+nextalloc*32;u.mem_write(read(ret+16),W(key))
     outs.append((calls,ret,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,12)),bytes(u.mem_read(N,4096)),bytes(u.mem_read(D,4096)),bytes(u.mem_read(0x20000338,16))));u.hook_del(h)
    assert outs[0]==outs[1],(seed,phase,key,outs)
    counts['insert' if phase==0 else 'remove']+=1
    if phase==0:allocated[key]=N+nextalloc*32;nextalloc+=1
  assert struct.unpack('<I',engines[0][0].mem_read(T,4))[0]==0
 receipt={'status':'PASS_COMPILED_ARM_CONNECTED_RB_ACTUAL_HEAP_WRAPPERS','cases':sum(counts.values()),'by_operation':counts,'random_seeds':100,'nodes_per_seed':24,'native_executed_instruction_addresses':len(coverage),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual RB chain and selected heap alloc/free/pool/size-query/pointer-to-block/block-size wrappers execute. TLSF allocation/free,semaphores,canonical memset and comparator are controlled cuts.','Valid constructed trees only; malformed/null/fatal and standalone helper cases remain unqualified. No full image or hardware claim.']};(DIR/'connected-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
