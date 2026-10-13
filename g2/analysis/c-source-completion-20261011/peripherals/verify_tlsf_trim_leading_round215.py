from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-trim-leading-round215';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['g2_tlsf_block_can_split','g2_tlsf_block_split','g2_tlsf_block_set_prev_free','g2_tlsf_block_link_next','g2_tlsf_block_insert'];native=[0x4d01bc,0x4d01d4,0x4cfde8,0x4cfe88,0x4d019a];cuts=[0x101010+i*16 for i in range(5)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d0444');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native4d0444')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,g2_tlsf_trim_free_leading_4d0444']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,size,can_split,overhead,remainder):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x78f4bc,W(overhead));events=[];trace=[]
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append((i,r[:[2,2,1,1,2][i]]));ret=can_split if i==0 else remainder if i==1 else 0xa5a5a5a5
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if a in [0x78f4bc]:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,P);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['g2_tlsf_trim_free_leading_4d0444'] if isc else 0x4d0444)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1,4,16,32,0xffffffff],[0,1,257,0xffffffff],[0,4,16,0xffffffff],[0,0x20003000,0xffffffe0]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_TLSF_TRIM_LEADING_CHILD_CONTRACTS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':5,'limits':['Conditional split, full-width size/overhead subtraction, exact child arguments/order/config read/result/SP matched.','Actual split/free-list arena integration and pointer faults remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
