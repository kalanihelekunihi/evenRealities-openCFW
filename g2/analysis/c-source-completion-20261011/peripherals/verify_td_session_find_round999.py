#!/usr/bin/env python3
"""Native/C ring wrapping and session lookup parity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-session-find-round999';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_session_find_by_id.c'
base=root/'build/c-firmware/terminal-data-append-round998/apollo-main-terminal-data-append.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'td_session_find_by_id.o';linked=out/'apollo-main-td-session-find.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_session_find_by_id',
                    str(src),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,kind,shift,count,logical,session,null_ring,null_index):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        ring=0x20010000;output=0x2001f000
        u.mem_write(ring+0x8500,count.to_bytes(2,'little'))
        u.mem_write(ring+0x8502,shift.to_bytes(2,'little'))
        if count and logical < count:
            physical=(logical+shift)%64
            u.mem_write(ring+physical*0x214+0x208,(0x12345678).to_bytes(4,'little'))
        u.mem_write(output,b'\xaa\xbb')
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        if kind=='wrap':
            u.reg_write(A.UC_ARM_REG_R0,ring)
            u.reg_write(A.UC_ARM_REG_R1,logical)
            entry=syms['audio_td_ring_index_wrap'] if compiled else 0x5970a8
        else:
            u.reg_write(A.UC_ARM_REG_R0,0 if null_ring else ring)
            u.reg_write(A.UC_ARM_REG_R1,session)
            u.reg_write(A.UC_ARM_REG_R2,0 if null_index else output)
            entry=syms['audio_td_session_find_by_id'] if compiled else 0x59726e
        u.emu_start(entry|1,0x600000,count=1000)
        return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(output,2))
    cases=0
    for shift in (0,1,31,63,64,65535):
        for logical in (0,1,2,63,64,65535):
            pair=[run(c,'wrap',shift,0,logical,0,False,False) for c in (False,True)]
            assert pair[0]==pair[1],('wrap',shift,logical,pair)
            cases+=1
    for shift in (0,1,31,63):
     for count in (0,1,2,4):
      for logical in (0,1,3):
       for session in (0,0x12345678,0x87654321):
        for null_ring,null_index in ((False,False),(True,False),(False,True)):
            pair=[run(c,'find',shift,count,logical,session,null_ring,null_index) for c in (False,True)]
            assert pair[0]==pair[1],('find',shift,count,logical,session,null_ring,null_index,pair)
            cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_session_find_by_id','audio_td_ring_index_wrap'} and not after-before
receipt={'round':999,'status':'PASS_TD_SESSION_FIND_AND_WRAP','component':'Apollo session ring index and lookup 0x5970a8/0x59726e',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C lookup/index/return parity for nonnegative counts',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Negative signed ring counts are outside validated state and remain unverified',
                  'Record build and append providers, RAM placement and whole image remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])
