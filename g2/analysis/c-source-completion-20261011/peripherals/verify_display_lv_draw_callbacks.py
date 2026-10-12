from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/callbacks_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_malloc(unsigned n){return 0;} void audio_uart_lv_heap_free(void*a){} unsigned audio_uart_lv_color_bpp_440f44(unsigned a){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_malloc_cb_48b80c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for name,native in [('audio_uart_lv_draw_buf_malloc_cb_48b80c',0x48b80c),('audio_uart_lv_draw_buf_free_cb_48b816',0x48b816),('audio_uart_lv_draw_buf_align_cb_48b81e',0x48b81e),('audio_uart_lv_draw_width_stride_cb_48b82a',0x48b82a)]:
  for value,cf,child in itertools.product([0,1,7,8,0xfffffff8,0xffffffff],[0,255,256,0x87654321],[0,1,32,0xffffffff]):
   outputs=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    calls=[];cuts={(syms[n] if isc else a)&~1:n for n,a in [('audio_uart_lv_malloc',0x44f718),('audio_uart_lv_heap_free',0x44f758),('audio_uart_lv_color_bpp_440f44',0x440f44)]}
    def hook(uc,a,size,user):
     if a not in cuts:return
     calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,child);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,cf);u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000);outputs.append((calls,None if native==0x48b816 else u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)))
   assert outputs[0]==outputs[1],(name,value,cf,child,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_FOUR_CALLBACKS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Malloc/free/BPP child cuts verify callback contracts and unsigned boundary arithmetic; BPP provider remains genuine import.','Void free scratch return not qualified; image layout/byte equality/hardware unproven.']};(SRC.parent/'callbacks-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
