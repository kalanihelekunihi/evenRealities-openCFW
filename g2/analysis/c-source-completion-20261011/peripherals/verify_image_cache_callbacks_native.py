from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-image-cache-callbacks-round103/image_cache_callbacks_candidate.c';LEAVES=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
W=lambda *v:struct.pack('<'+'I'*len(v),*v)
A,B,D=0x20001000,0x20001100,0x20001200
providers=[('audio_uart_lv_image_source_compare_4d4b32',0x4d4b32),('audio_uart_lv_image_header_source_compare_4d4c3a',0x4d4c3a),('audio_uart_lv_image_cache_compare_4d4b94',0x4d4b94),('audio_uart_lv_image_header_cache_compare_4d4c9c',0x4d4c9c),('audio_uart_lv_image_cache_free_4d4ba4',0x4d4ba4),('audio_uart_lv_image_header_cache_free_4d4cac',0x4d4cac)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_font_bitmap_release(void*a){} void audio_uart_lv_heap_free(void*a){} int audio_uart_font_path_compare(const char*a,const char*b){return 0;}')
 elf=td/'test.elf';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(SRC),str(LEAVES),str(shim),'-o',str(elf)]
 # Selected string wrapper delegates to compiler helper: inspect its name below.
 subprocess.run(cmd,check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('strcmp','audio_uart_lv_string_compare_4547be',0x4547be),('destroy','audio_uart_font_bitmap_release',0x48b216),('free','audio_uart_lv_heap_free',0x44f758)]};engines.append((u,cuts,isc))
 counts={s:0 for s,n in providers}
 def check(idx,args,entry,draw,cmp=0,mutate=0):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(A,entry);u.mem_write(B,bytes(24));u.mem_write(D,draw);calls=[]
   if idx in [2,3]:u.mem_write(B,W(args[2],args[3]&255,0,0,0,0) if idx==3 else W(0,args[2],args[3]&255,0,0,0))
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);calls.append((op,r0,r1) if op=='strcmp' else (op,r0))
    if op=='destroy' and mutate:
     uc.mem_write(A+8,bytes([1 if mutate==1 else 0]));uc.mem_write(A+4,W(0x87654321));uc.mem_write(A+12,W(0xabcdef01))
    uc.reg_write(UC_ARM_REG_R0,cmp if op=='strcmp' else 0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   r=args if idx<2 else [A,B] if idx<4 else [A]
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],r):u.reg_write(reg,value)
   u.emu_start((syms[s] if isc else n)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0) if idx<4 else None,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(A,24)),bytes(u.mem_read(D,24))));u.hook_del(h)
  assert outs[0]==outs[1],(s,args,cmp,mutate,outs);counts[s]+=1
 kinds=[0,1,2,3,127,128,254,255,0x100,0x101,0xffffffff]
 for idx in range(4):
  for ak,bk,a,b in itertools.product(kinds,kinds,[0,0x20004000,0xffffffff],[0,0x20004000,0xffffffff]):
   results=[0,1,-1,0x100,-0x100,0x7fffffff,-0x80000000] if (ak&255)==(bk&255)==1 else [0]
   for cmp in results:
    entry=W(a,ak&255,a,bk&255,0,0) if idx==3 else W(0,a,ak&255,0,0,0)
    # header layout is source0/kind4; second header source/kind above.
    check(idx,[a,ak,b,bk],entry,bytes(24),cmp)
 for kind,flags,mutate in itertools.product(range(256),[0,16,0xffff],[0,1,2]):check(4,[],W(0,0x12345678,kind,D,0,0),W(flags<<16,0,0,0,0,0),mutate=mutate)
 for kind in range(256):check(5,[],W(0x12345678,kind,0,0,0,0),bytes(24))
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_IMAGE_CACHE_CALLBACKS','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'selected_leaf_source_sha256':hashlib.sha256(LEAVES.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual flag leaf executes. String compare,draw destroy,heap free are controlled child cuts; signed compare boundaries and destroy mutation tested.','Image/header startup,concrete LRU class/tree/allocator/data bindings and full-image/hardware remain open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
