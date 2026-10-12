from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-image-cache-startup-round104';SEL=ROOT/'components/audio/uart_thread_source_candidate'
SOURCES=[DIR/'image_cache_startup_candidate.c',DIR/'lru_init_candidate.c',SEL/'display_font_lru_vtable.c',SEL/'display_font_cache_create.c',SEL/'display_lv_init_mutex_children.c',SEL/'display_lv_init_children.c',SEL/'display_lv_global_init.c',SEL/'display_font_rb_core.c',SEL/'display_font_lru_alloc.c']
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,R=0x20001000,0x2006f548;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_lv_image_cache_init_4d4ad4',0x4d4ad4,0x134),('audio_uart_lv_image_header_cache_init_4d4bdc',0x4d4bdc,0x138)]
aliases={'audio_uart_font_cache_backend_vtable':0x73f478,'audio_uart_lv_cache_size_backend_vtable':0x73f4a4,'audio_uart_lv_image_cache_compare_4d4b94':0x4d4b95,'audio_uart_lv_image_cache_free_4d4ba4':0x4d4ba5,'audio_uart_lv_image_header_cache_compare_4d4c9c':0x4d4c9d,'audio_uart_lv_image_header_cache_free_4d4cac':0x4d4cad,'audio_uart_lv_cache_count_data_size_5c330c':0x5c330d,'audio_uart_lv_cache_size_data_size_5c3310':0x5c3311}
backend=['audio_uart_font_lru_allocate','audio_uart_font_lru_initialize','audio_uart_font_lru_destroy','audio_uart_font_lru_lookup','audio_uart_font_lru_add','audio_uart_font_lru_remove','audio_uart_font_lru_evict','audio_uart_font_lru_clear','audio_uart_font_lru_get_victim','audio_uart_font_lru_reserve'];native_backend=[0x5c2bef,0x5c2c55,0x5c2e0d,0x5c2e4d,0x5c2f33,0x5c2fd5,0x5c3099,0x5c315b,0x5c3223,0x5c328b];aliases.update(dict(zip(backend,native_backend)));aliases['audio_uart_lv_cache_size_lru_init_5c2d30']=0x5c2d31
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_lv_malloc(unsigned n){return 0;} void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){} void audio_uart_lv_mutex_ensure(void*a){} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){} void audio_uart_font_bitmap_release(void*a){} int audio_uart_font_path_compare(const char*a,const char*b){return 0;}\n'+'\n'.join('void '+s+'(){}' for s in backend[2:]));elf=td/'test.elf'
 children=td/'children.c';children.write_text((SEL/'display_lv_init_children.c').read_text().split('/* Native image and header cache startup bindings: round104. */')[0]);fixture_sources=[children if p==SEL/'display_lv_init_children.c' else p for p in SOURCES]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root='+hex(R),'-Wl,-e,'+providers[0][0],'-Wl,-u,'+providers[1][0],'-Wl,-u,audio_uart_lv_cache_set_name_4d5114']+[str(p) for p in fixture_sources]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 reverse={syms[s]|(n&1):n for s,n in aliases.items()};engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('malloc','audio_uart_lv_malloc',0x44f718),('clear','audio_uart_lv_basic_box_clear_454746',0x454746),('ensure','audio_uart_lv_mutex_ensure',0x4d47cc),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]};engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n,o in providers}
 for idx,capacity,initial,allocated,mutate in itertools.product(range(2),[0,1,32,0xffffffff],[0,C,0x20002000],[False,True],[0,1,2]):
  outs=[];s,n,offset=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(R,bytes([0xa5])*0x200);u.mem_write(R+offset,W(initial));u.mem_write(C,bytes([0xa5])*68);calls=[];faults=[]
   normalize=lambda value:reverse.get(value,value) if isc else value
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
    if op=='malloc':calls.append((op,r[0]));assert r[0]==68;ret=C if allocated else 0
    elif op=='clear':
     fields=[normalize(v) for v in struct.unpack('<7I',uc.mem_read(C,28))];calls.append((op,*r[:3],fields));assert r[:3] in [[C+40,0,12],[C,0,68]];uc.mem_write(r[0],bytes(r[2]))
     if mutate and r[0]==C+40:uc.mem_write(C+4,W(0xdeadbeef));uc.mem_write(R+offset,W(0x20003000));uc.mem_write(C+52,W(1,2,3))
    elif op=='ensure':
     calls.append((op,r[0]));uc.mem_write(C+28,W(1,0x87654321))
     if mutate==2:uc.mem_write(R+offset,W(0))
    elif op=='free':calls.append((op,r[0]))
    else:
     fmt=struct.unpack('<I',uc.mem_read(sp,4))[0];item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt))
     if r[2] in [51,190]:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     calls.append(item)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,capacity)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=5000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   fields=[normalize(v) for v in struct.unpack('<17I',u.mem_read(C,68))]
   if not initial and allocated:fields[9]=string(u,fields[9])
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),fields,bytes(u.mem_read(R,0x200))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,capacity,initial,allocated,rb_result,mutate,outs);counts[s]+=1
 # Full standalone native name setter, including NULL and arbitrary name words.
 counts['audio_uart_lv_cache_set_name_4d5114']=0
 for cache,name in itertools.product([0,C,C+4],[0,1,0x12345678,0xffffffff]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(C,bytes([0xa5])*68);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,cache);u.reg_write(UC_ARM_REG_R1,name)
   u.emu_start((syms['audio_uart_lv_cache_set_name_4d5114'] if isc else 0x4d5114)|1,0x600000,count=50);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((bytes(u.mem_read(C,68)),u.reg_read(UC_ARM_REG_SP)))
  assert outs[0]==outs[1],(cache,name,outs);counts['audio_uart_lv_cache_set_name_4d5114']+=1
 # Source-defined count/size class table identity checked against all ten native words.
 u=engines[1][0]
 for sym,native in [('audio_uart_font_cache_backend_vtable',0x73f478),('audio_uart_lv_cache_size_backend_vtable',0x73f4a4)]:
  got=[reverse.get(v,v) for v in struct.unpack('<10I',u.mem_read(syms[sym],40))];want=list(struct.unpack_from('<10I',BLOB,native-0x438000));assert got==want,(sym,got,want)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_STARTUP_CURRENT_VTABLE','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'class_words_compared':20,'limits':['Actual shared constructor,count/size initializers,array and mutex wrapper execute; Actual LRU allocator/zero wrapper and RB initializer/zero wrapper execute; malloc,clear,mutex ensure,free,logger controlled child cuts.','Source-owned callback/class/name pointers normalized by authenticated identities; no relocation/byte equality or hardware claim.','Cache name setter executes on startup successful/NULL paths plus standalone arbitrary-name-word cases. Concrete backend/tree/allocator/source-data/full-image gates remain.']};(DIR/'startup-current-vtable-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
