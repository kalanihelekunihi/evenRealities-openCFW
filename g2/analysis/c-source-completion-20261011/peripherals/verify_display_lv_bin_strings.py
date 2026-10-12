from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-strings-round61/strings_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned g2_log_module_length(const char*a){return 0;} int audio_uart_font_path_compare(const char*a,const char*b){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_extension_4c70e4','-Wl,-u,audio_uart_lv_string_compare_4547be',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[('ext',bytes(v),0) for n in range(5) for v in itertools.product(b'a./\\',repeat=n)]+[('cmp',b'a',r) for r in [0,1,255,256,0xffffffff,0xffffff01]];count=0
 for kind,value,result in cases:
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   ptr=0x20003000;u.mem_write(ptr,value+b'\0');calls=[];cut=(syms['g2_log_module_length' if kind=='ext' else 'audio_uart_font_path_compare'] if isc else (0x44a43c if kind=='ext' else 0x46cacc))&~1
   def hook(uc,a,size,user):
    if a!=cut:return
    args=[uc.reg_read(UC_ARM_REG_R0)]
    if kind=='cmp':args.append(uc.reg_read(UC_ARM_REG_R1))
    calls.append(args);uc.reg_write(UC_ARM_REG_R0,len(value) if kind=='ext' else result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,ptr+100)
   name='audio_uart_lv_fs_extension_4c70e4' if kind=='ext' else 'audio_uart_lv_string_compare_4547be';u.emu_start((syms[name] if isc else (0x4c70e4 if kind=='ext' else 0x4547be))|1,0x600000,count=10000);ret=u.reg_read(UC_ARM_REG_R0)
   if kind=='ext':ret=('source',ret-ptr) if ptr<=ret<=ptr+len(value)+1 else ('empty',bytes(u.mem_read(ret,1)))
   outputs.append((calls,ret,u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(kind,value,result,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_STRING_HELPERS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Length and compare lower providers are controlled cuts; selected production bodies are separate existing evidence.','Extension compares source-relative returned pointer or native empty string contents; full data placement is unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
