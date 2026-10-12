from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-goto-xy-round96/goto_candidate.c';PROVIDERS=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
A=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_goto_xy_48b2aa',str(SRC),str(PROVIDERS),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  engines.append((u,(syms['audio_uart_lv_draw_buf_goto_xy_48b2aa'] if isc else 0x48b2aa)|1,(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 count=0
 cases=list(itertools.product(range(256),[0,1,7,0x80000001,0xffffffff],[0,1,0xffffffff],[0,17,65535],[0,0x20002000,0xffffffff]));cases.append((None,0,0,0,0))
 for cf,x,y,stride,data in cases:
  outs=[]
  for u,entry,log in engines:
   u.mem_write(A,W(0xabcd0000|((cf or 0)<<8)|0xaa,0xffff0001,0xbeef0000|stride,0,data));calls=[];faults=[]
   def hook(uc,address,size,user):
    if address!=log:return
    r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];args=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));calls.append((r[0],string(uc,r[1]),r[2],string(uc,r[3]),*[string(uc,p) for p in args]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[0 if cf is None else A,x,y]):u.reg_write(reg,v)
   try:u.emu_start(entry,0x600000,count=1000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(A,20))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(cf,x,y,stride,data,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_GOTO_XY','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'providers_sha256':hashlib.sha256(PROVIDERS.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'48b2aa..48b34e','limits':['Actual BPP provider executes; logger cut only. All256 formats plus bounded wrapping coordinates/strides/data addresses.','Exact null assertion/log and first UINT32_MAX zero-store; full-image/hardware gates open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
