#!/usr/bin/env python3
"""Native/C callback-manager guarded node release."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/callback-mgr-delete-node-round989';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/display_callback_manager_delete_node.c'
obj=out/'display_callback_manager_delete_node.o'
base=root/'build/c-firmware/callback-mgr-unregister-round988/apollo-main-callback-mgr-unregister.o'
linked=out/'apollo-main-callback-mgr-delete-node.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5100fc-0x438000:0x510108-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''void audio_file_heap_free(void*a){(void)a;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_callback_mgr_delete_node',str(src),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for node in (0,0x20010000,0xffffffff):
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x200000)
   child=(syms['audio_file_heap_free'] if compiled else 0x474d16)&~1
   calls=[]
   def hook(cpu,address,size,user):
    if address!=child:return
    calls.append(cpu.reg_read(A.UC_ARM_REG_R0));cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,hook)
   uc.reg_write(A.UC_ARM_REG_R0,node);uc.reg_write(A.UC_ARM_REG_SP,0x201ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start((syms['audio_callback_mgr_delete_node'] if compiled else 0x5100fc)|1,0x600000,count=50)
   outputs.append(calls)
  assert outputs[0]==outputs[1],(node,outputs)
  cases.append(node)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_callback_mgr_delete_node'} and after-before==set()
receipt={'round':989,'status':'PASS_NATIVE_CALLBACK_MGR_DELETE_NODE','component':'Apollo callback-manager node release 0x5100fc',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C null guard and exact selected heap-free child argument',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Selected heap-free lower allocator and ownership remain bounded','Final RAM layout and full image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
