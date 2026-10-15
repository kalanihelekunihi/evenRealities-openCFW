#!/usr/bin/env python3
"""Native/C terminal bounded copy and record builder parity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-record-build-round1001';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_record_build_from_event.c'
base=root/'build/c-firmware/td-session-ring-append-round1000/apollo-main-td-session-ring-append.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'td_record_build_from_event.o';linked=out/'apollo-main-td-record-build.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('void *audio_queue_copy_bytes(void*a,const void*b,unsigned c){(void)b;(void)c;return a;}\n')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_record_build_from_event',
                    str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def one(compiled,builder,kind,length,capacity,dest_present,source_present,passthrough=0x89abcdef):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        dest=0x20010000;source=0x20011000
        u.mem_write(dest,b'\xaa'*0x600)
        data=bytearray(0x600);data[0]=kind
        data[2:4]=length.to_bytes(2,'little')
        for i in range(4,len(data)):data[i]=(i*7)&0xff
        u.mem_write(source,bytes(data))
        child=syms['audio_queue_copy_bytes'] if compiled else 0x439be4
        def hook(cpu,address,size,user):
            a=cpu.reg_read(A.UC_ARM_REG_R0);b=cpu.reg_read(A.UC_ARM_REG_R1)
            n=cpu.reg_read(A.UC_ARM_REG_R2)
            cpu.mem_write(a,bytes(cpu.mem_read(b,n)))
            cpu.reg_write(A.UC_ARM_REG_R0,a)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook,begin=child&~1,end=child&~1)
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.reg_write(A.UC_ARM_REG_R0,dest if dest_present else 0)
        u.reg_write(A.UC_ARM_REG_R1,(source if builder else capacity))
        u.reg_write(A.UC_ARM_REG_R2,(0x12345678 if builder else (source+2 if source_present else 0)))
        u.reg_write(A.UC_ARM_REG_R3,passthrough)
        if not builder:u.reg_write(A.UC_ARM_REG_R1,capacity)
        if builder and not source_present:u.reg_write(A.UC_ARM_REG_R1,0)
        entry=(syms['audio_td_record_build_from_event'] if compiled else 0x5972ce) if builder else (syms['audio_td_bounded_string_copy'] if compiled else 0x59722c)
        u.emu_start(entry|1,0x600000,count=2000)
        return (u.reg_read(A.UC_ARM_REG_R0),
                bytes(u.mem_read(dest,0x600)))
    cases=0
    for length in (0,1,10,512,513,1000,65535):
     for capacity in (0,1,2,10,0x201):
      for dest_present in (False,True):
       for source_present in (False,True):
        pair=[one(c,False,0,length,capacity,dest_present,source_present) for c in (False,True)]
        assert pair[0]==pair[1],('copy',length,capacity,dest_present,source_present,pair)
        cases+=1
    for kind in (0,1,2,3,4,5,255):
     for length in (0,1,10,512,513,1000):
      for dest_present in (False,True):
       for source_present in (False,True):
        for passthrough in (0,0x89abcdef):
         pair=[one(c,True,kind,length,0x201,dest_present,source_present,passthrough) for c in (False,True)]
         assert pair[0]==pair[1],('build',kind,length,dest_present,source_present,passthrough,pair)
         cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_record_build_from_event'} and not after-before
receipt={'round':1001,'status':'PASS_TD_RECORD_BUILD_AND_BOUNDED_COPY','component':'Apollo TD record builder 0x5972ce and text copy 0x59722c',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C field, text, clamp, null and entry-R3 return parity',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Absolute RAM placement and whole image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])
