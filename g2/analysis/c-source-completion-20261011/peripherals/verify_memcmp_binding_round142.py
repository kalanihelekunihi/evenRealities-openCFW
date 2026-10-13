import hashlib,json,sys
#!/usr/bin/env python3
"""Stock/source ARM memcmp exact return oracle across alignment paths."""
from pathlib import Path
import subprocess,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
O=D/'root-memcmp-binding-round142/memcmp-m4.o';E=D/'root-memcmp-binding-round142/memcmp-m4.elf'
S=R/'g2/analysis/c-source-completion-20261011/peripherals/root-memcmp-binding-round142/candidate.c'
if '--selected' in sys.argv:S=R/'g2/components/audio/file_sync_candidate/byte_compare.c'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,a,b,n,ao,bo):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for x,s in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(x,s)
 if stock:u.mem_write(0x438000,B)
 else:
  for x,d in seg:u.mem_write(x,d)
 u.mem_write(0x20011000+ao,bytes(a));u.mem_write(0x20012000+bo,bytes(b))
 for reg,v in ((A.UC_ARM_REG_R0,0x20011000+ao),(A.UC_ARM_REG_R1,0x20012000+bo),
               (A.UC_ARM_REG_R2,n),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4751c8 if stock else sy['memcmp'])|1,0,count=1000)
 assert done[0]
 v=u.reg_read(A.UC_ARM_REG_R0)
 return v if v<0x80000000 else v-0x100000000
random.seed(452)
cases=0
for ao in range(4):
 for bo in range(4):
  for n in (0,1,2,3,4,5,7,8,13,31):
   for variant in (0,1,2,3):
    a=bytearray(random.randrange(256) for _ in range(40));b=bytearray(a)
    if variant and n:
     i=min(n-1,variant-1);b[i]=(b[i]+variant)&255
    x=run(True,a,b,n,ao,bo);y=run(False,a,b,n,ao,bo)
    assert x==y,(ao,bo,n,variant,x,y)
    cases+=1
print('PASS_PUBLIC_MEMCMP',cases)

D=R/'g2/analysis/c-source-completion-20261011/peripherals/root-memcmp-binding-round142';blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';(D/'receipt.json').write_text(json.dumps({'status':'PASS_PUBLIC_MEMCMP_NATIVE_EXACT_RETURN','cases':cases,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Native4751c8 exactreturn acrossalignments,lengths,equal/mismatch cases; existingcanonicalCbody reused.','Nine SMP callers nativebound; twoBda dependency callers use standardAPIcontract and nativebinding remainsunmapped. Fullimages/hardware gatesopen.']},indent=2)+'\n')
