#!/usr/bin/env python3
"""Native/C host status names, processing-state check, and data getters."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-host-helpers-round937';out.mkdir(parents=True,exist_ok=True)
sd=root/'components/audio/uart_thread_source_candidate'
src=sd/'terminal_host_helpers.c';state=sd/'td_state.c'
obj=out/'terminal_host_helpers.o'
base=root/'build/c-firmware/td-ring-write-round936/apollo-main-td-ring-write.o'
linked=out/'apollo-main-terminal-host-helpers.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for literal,label in zip((0x5e8c3c,0x5e8c40,0x5e8c44,0x5e8e40),(b'HOST_STATUS_NO_HOST',b'HOST_STATUS_OFFLINE',b'HOST_STATUS_STREAMING',b'HOST_STATUS_UNKNOWN')):
 ptr=int.from_bytes(blob[literal-0x438000:literal-0x438000+4],'little')
 assert blob[ptr-0x438000:].split(b'\0')[0]==label
assert int.from_bytes(blob[0x597c18-0x438000:0x597c1c-0x438000],'little')==0x20119284
entries={'name':('audio_terminal_host_status_name',0x5e82e6),'processing':('audio_terminal_state_is_processing',0x5e8294),'pointer':('audio_td_state_ptr_alias2',0x59734a),'counter':('audio_td_counter_b_get',0x5973dc)}
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_host_status_name',str(src),str(state),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(compiled,name,value,counter=0x12345678):
  uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
  uc.mem_map(0x100000,0x100000)
  for addr,data in segs:uc.mem_write(addr,data)
  uc.mem_map(0x20000000,0x200000)
  addr=syms['audio_td_state'] if compiled else 0x2010fd20
  uc.mem_write(addr+0x9564,counter.to_bytes(4,'little'))
  symbol,entry=entries[name]
  uc.reg_write(A.UC_ARM_REG_R0,value);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
  uc.emu_start(((syms[symbol] if compiled else entry)|1),0x600000,count=100)
  result=uc.reg_read(A.UC_ARM_REG_R0)
  if name=='name':return bytes(uc.mem_read(result,64)).split(b'\0')[0]
  if name=='pointer':return result-addr
  return result
 cases=[]
 for value in list(range(256))+[0x100,0x101,0x102,0xffffffff]:
  for name in ('name','processing'):
   n=run(False,name,value);c=run(True,name,value)
   assert n==c,(name,value,n,c)
   cases.append((name,value))
 for name in ('pointer','counter'):
  for counter in (0,1,0x12345678,0xffffffff):
   n=run(False,name,0,counter);c=run(True,name,0,counter)
   assert n==c,(name,counter,n,c)
   cases.append((name,counter))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
assert imports(base)==imports(linked)
receipt={'round':937,'status':'PASS_NATIVE_TERMINAL_HOST_HELPERS','component':'Apollo host-status name/processing and terminal-data getters','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_bodies_sha256':{k:hashlib.sha256(blob[a-0x438000:b-0x438000]).hexdigest() for k,a,b in [('processing',0x5e8294,0x5e82a4),('name',0x5e82e6,0x5e830c),('pointer',0x59734a,0x597350),('counter',0x5973dc,0x5973e4)]},'cases':len(cases),'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_after':len(imports(linked)),'whole_image_complete':False,'hardware_proof':False,'gates':['Host-status callback 0x5e8c48 and runtime-event helper 0x5e873e remain open','6 terminal callback bodies, runtime event-name array, ring-connect buffer, 49 registry callbacks and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(imports(linked)))
