from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-cache-entry-acquire-round98/cache_entry_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
E=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cache_acquire_data',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for name,native,void in [('audio_uart_font_cache_retain',0x4d5278,True),('audio_uart_font_cache_acquire_data',0x4d53c6,False)]:
  for null,ref,offset in itertools.product([False,True],[0,1,0x7fffffff,0xffffffff],[0,4,16,0xffffffff]):
   outs=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_write(E,W(0,ref,offset,0));calls=[];faults=[];log=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1
    def string(p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
    def hook(uc,addr,size,user):
     if addr!=log:return
     r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];args=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));calls.append((r[0],string(r[1]),r[2],string(r[3]),*[string(p) for p in args]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
    u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if null else E)
    try:u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000)
    except UcError:assert faults==[(0xffffffff,4,0)]
    if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
    outs.append((calls,faults,None if void or faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(E,16))))
   assert outs[0]==outs[1],(name,null,ref,offset,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_RETAIN_ACQUIRE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['4d5278..4d52b2','4d53c6..4d5400'],'limits':['Actual retain and getter execute for acquire; logger cut, exact first UINT32_MAX zero-store.','Other cache accessors unchanged and not newly qualified; full-image/hardware gates remain.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
