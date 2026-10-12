from pathlib import Path
import tempfile,subprocess,json,hashlib,itertools,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-cache-insert-round88/insert_candidate.c';GETTER=ROOT/'components/audio/uart_thread_source_candidate/display_font_cache_entry.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
DATA,ENTRY,KEY,CACHE,SOURCE,DUP=0x20001000,0x20001040,0x20002000,0x20003000,0x20004000,0x20005000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_cache_add_4d4eea(void*a,const void*b,void*c){return 0;} char *audio_uart_font_path_duplicate(const char*a){return 0;} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,const char*e,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_decoder_add_cache_48911a',str(SRC),str(GETTER),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for kind,entry,dup,mutate in itertools.product([0,1,2,255],[False,True],[0,DUP,0xffffffff],[False,True]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x2006f548+0x134,W(CACHE));u.mem_write(DATA,W(0xa5a5a5a5,SOURCE,0xabcdef00|kind,0x11111111,0x22222222,0x33333333));u.mem_write(ENTRY,W(0,0,64));u.mem_write(KEY,W(1,SOURCE,kind));u.mem_write(SOURCE,b'asset.bin\0');calls=[];cuts={(syms['audio_uart_lv_cache_add_4d4eea'] if isc else 0x4d4eea)&~1:'add',(syms['audio_uart_font_path_duplicate'] if isc else 0x4547c6)&~1:'dup'}
   def hook(uc,a,size,user):
    if a not in cuts:return
    op=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];calls.append((op,*args[:3 if op=='add' else 1]));value=ENTRY if entry else 0
    if op=='add':assert args==[CACHE,KEY,0]
    else:
     value=dup
     if mutate:uc.mem_write(DATA+12,W(0x77777777));uc.mem_write(DATA+16,W(0x88888888));uc.mem_write(DATA+20,W(0x99999999))
    uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x12345678,KEY,0x87654321,0xffffffff]):u.reg_write(reg,v)
   u.emu_start((syms['audio_uart_lv_decoder_add_cache_48911a'] if isc else 0x48911a)|1,0x600000,count=1000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(DATA,24))))
  assert outputs[0]==outputs[1],(kind,entry,dup,mutate,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_CACHE_INSERT','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'getter_sha256':hashlib.sha256(GETTER.read_bytes()).hexdigest(),'limits':['Actual native/compiled getter executes; cache-add and strdup are child cuts. Cache-add provider remains genuine import.','Full cache ownership/tree behavior, image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
