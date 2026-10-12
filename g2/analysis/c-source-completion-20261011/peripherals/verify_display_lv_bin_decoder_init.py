from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
CALLBACKS={'info':0x4c79d0,'open':0x4c7b24,'get_area':0x4c7e4c,'close':0x4c7e28}
with tempfile.TemporaryDirectory() as td:
 td=Path(td);shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512]; void *audio_uart_lv_list_prepend_482b12(void*p){(void)p;return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){(void)a;(void)b;(void)c;(void)d;} void audio_uart_lv_basic_box_clear_454746(void*p,unsigned f,unsigned n){(void)p;(void)f;(void)n;}'+''.join('void audio_uart_lv_bin_decoder_'+n+'_'+format(a,'x')+'(void){}' for n,a in CALLBACKS.items()))
 count=0
 for cut_mode in ['prepend','creator']:
  oracle_src=SRC
  call_shim=td/(cut_mode+'-shim.c')
  call_shim.write_text(shim.read_text()+('void *audio_uart_lv_image_decoder_create_4890c8(void){return 0;}' if cut_mode=='creator' else ''))
  if cut_mode=='creator':
   oracle_src=td/'init-only.c'
   oracle_src.write_text('#include <stdint.h>\nextern void *audio_uart_lv_image_decoder_create_4890c8(void);\nextern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);\n/* Address-only callback declarations */'+SRC.read_text().split('/* Address-only callback declarations',1)[1].split('*/',1)[1])
  elf=td/'decoder.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_init_4c794c',str(oracle_src),str(call_shim),'-o',str(elf)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  with elf.open('rb') as fp:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(fp).iter_segments() if s['p_type']=='PT_LOAD']
  for allocated in [0,0x20002000]:
   for pattern in [0,0xa5,0xff]:
    outputs=[]
    for isc in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segs:u.mem_write(a,d)
     root=syms['audio_uart_display_lv_root'] if isc and cut_mode=='prepend' else 0x2006f548;u.mem_write(root,bytes([pattern])*512);u.mem_write(0x20002000,bytes([pattern])*32);calls=[];faults=[]
     allocation=((syms['audio_uart_lv_list_prepend_482b12'] if isc else 0x482b12) if cut_mode=='prepend' else (syms['audio_uart_lv_image_decoder_create_4890c8'] if isc else 0x4890c8))&~1
     log=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1;clear=((syms['audio_uart_lv_basic_box_clear_454746'] if isc else 0x454746)&~1) if cut_mode=='prepend' else -1
     def string(uc,a):
      out=bytearray()
      while True:
       x=bytes(uc.mem_read(a+len(out),1))
       if x==b'\x00':return out.decode('ascii')
       out.extend(x);assert len(out)<300
     def hook(uc,address,size,user):
      if address==allocation:
       args=('allocate',uc.reg_read(UC_ARM_REG_R0)-root) if cut_mode=='prepend' else ('create',);calls.append(args);uc.reg_write(UC_ARM_REG_R0,allocated);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      elif address==clear:
       args=tuple(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]);calls.append(('clear',*args));uc.mem_write(args[0],bytes([args[1]&255])*args[2]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      elif address==log:
       sp=uc.reg_read(UC_ARM_REG_SP);args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+[int.from_bytes(uc.mem_read(sp+i*4,4),'little') for i in range(3)]
       calls.append(('log',args[0],string(uc,args[1]),args[2],string(uc,args[3]),*[string(uc,a) for a in args[4:]]));uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
     u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     try:u.emu_start((syms['audio_uart_lv_bin_decoder_init_4c794c'] if isc else 0x4c794c)|1,0x600000,count=1000)
     except UcError:assert faults
     record=bytearray(u.mem_read(0x20002000,32))
     if allocated:
      for i,(n,a) in enumerate(CALLBACKS.items()):
       got=int.from_bytes(record[i*4:i*4+4],'little');expected=(syms['audio_uart_lv_bin_decoder_'+n+'_'+format(a,'x')]|1) if isc else a|1;assert got==expected,(n,hex(got),hex(expected));record[i*4:i*4+4]=(a|1).to_bytes(4,'little')
      name=int.from_bytes(record[20:24],'little');assert string(u,name)=='BIN';record[20:24]=(0x4c7b1c).to_bytes(4,'little')
     outputs.append((calls,bytes(u.mem_read(root,512)),bytes(record),faults,u.reg_read(UC_ARM_REG_SP) if allocated else None))
    assert outputs[0]==outputs[1],(cut_mode,allocated,pattern,outputs)
    assert outputs[0][3]==([(0xffffffff,4,0)] if allocated==0 else [])
    if allocated and cut_mode=='prepend':assert outputs[0][0]==[('allocate',0x128),('clear',0x20002000,0,28)]
    count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_BIN_DECODER_CREATION_AND_INIT','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'callback_identities':{n:hex(a|1) for n,a in CALLBACKS.items()},'limits':['Oracle ARM build disables inlining so prepend/creator, byte-clear and logger child cuts remain observable.','Outer initializer failure is checked as a separate exact source-body translation unit; integrated compiler can eliminate it because creator fails fatally.','Four callback bodies and invocation signatures remain genuine imports.','Failure comparison stops at first faulting store; hardware fault handling and image layout are unverified.']}
 (Path(__file__).parent/'root-bin-decoder-round57/receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
