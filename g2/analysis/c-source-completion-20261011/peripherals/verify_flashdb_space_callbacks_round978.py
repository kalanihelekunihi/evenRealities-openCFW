#!/usr/bin/env python3
"""Native/C FlashDB space-search count and match callbacks."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/flashdb-space-callbacks-round978';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/settings_flashdb_space_callbacks.c'
obj=out/'settings_flashdb_space_callbacks.o'
base=root/'build/c-firmware/flashdb-prepare-space-round977/apollo-main-flashdb-prepare-space.o'
linked=out/'apollo-main-flashdb-space-callbacks.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x5447b6-0x438000:0x544814-0x438000]
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_flashdb_space_count_callback',str(src),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for kind in ('count','match'):
  for present in (0,1):
   for type1 in (0,1,2,3):
    for type2 in (0,1,2,3):
     for dbflag in (0,1):
      outputs=[]
      for compiled in (False,True):
       uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
       uc.mem_map(0x100000,0x100000)
       for addr,data in segs:uc.mem_write(addr,data)
       uc.mem_map(0x20000000,0x200000)
       kv=0x20010000;arg1=0x20010100;arg2=0x20010200;db=0x20010300;dest=0x20010400
       uc.mem_write(kv,b'\0'*88);uc.mem_write(kv,bytes([present,type1,type2]))
       uc.mem_write(kv+16,(0x1000 if type2&1 else 0x50).to_bytes(4,'little'))
       uc.mem_write(kv+20,(0x12345678).to_bytes(4,'little'))
       uc.mem_write(arg1,b'\0'*16);uc.mem_write(arg2,(7).to_bytes(4,'little'))
       uc.mem_write(db+0x30,bytes([dbflag]));uc.mem_write(dest,(0xaaaaaaaa).to_bytes(4,'little'))
       if kind=='match':uc.mem_write(arg1,db.to_bytes(4,'little')+(0x100).to_bytes(4,'little')+dest.to_bytes(4,'little'))
       name='audio_flashdb_space_'+kind+'_callback';native_addr=0x5447b6 if kind=='count' else 0x5447e0
       for reg,val in ((A.UC_ARM_REG_R0,kv),(A.UC_ARM_REG_R1,arg1),(A.UC_ARM_REG_R2,arg2),(A.UC_ARM_REG_SP,0x201ff000),(A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,val)
       uc.emu_start((syms[name] if compiled else native_addr)|1,0x600000,count=100)
       outputs.append((uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(arg1,12)),bytes(uc.mem_read(arg2,4)),bytes(uc.mem_read(dest,4))))
      assert outputs[0]==outputs[1],(kind,present,type1,type2,dbflag,outputs)
      cases.append((kind,present,type1,type2,dbflag))
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before==after
receipt={'round':978,'status':'PASS_NATIVE_FLASHDB_SPACE_CALLBACKS','component':'Apollo FlashDB space count/match callbacks 0x5447b6 and 0x5447e0',
 'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),
 'cases':len(cases),'validation':'Native/C count and match callback RAM mutation and returns',
 'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
 'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
 'gates':['Space-search parent 0x544814 and iterator integration remain open','Other FlashDB write providers and DB row placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
