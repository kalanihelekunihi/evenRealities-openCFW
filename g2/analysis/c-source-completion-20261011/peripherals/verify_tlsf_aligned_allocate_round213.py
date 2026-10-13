from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-aligned-allocate-round213';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['g2_tlsf_adjust_request','g2_tlsf_find_suitable','g2_tlsf_block_to_ptr','g2_tlsf_align_ptr','g2_tlsf_trim_free_leading_4d0444','g2_tlsf_prepare_allocation','g2_file_close_error'];native=[0x4cff42,0x4d0484,0x4cfe10,0x4cff18,0x4d0444,0x4d04e6,0x4d09b4];cuts=[0x101010+i*16 for i in range(7)]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d0744');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native4d0744')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_tlsf_aligned_allocate_4d0744']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,size,adjusted,alignment,present,gap,secondgap,config):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x78f4c4,W(12 if config else 0));events=[];trace=[];counts={0:0,3:0}
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];events.append((i,string(r[0]),string(r[1]),r[2]) if i==6 else (i,r[:[2,2,1,2,3,3,3][i]]));ret=0xa5a5a5a5
   if i==0:counts[0]+=1;ret=adjusted if counts[0]==1 else 0x1234
   elif i==1:ret=P if present else 0
   elif i==2:ret=PTR
   elif i==3:counts[3]+=1;ret=(PTR+(gap if counts[3]==1 else secondgap))&0xffffffff
   elif i==4:ret=0x20003000
   elif i==5:ret=0x20004000 if r[1] else 0
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if a in [0x78f4c4,0x78f4bc]:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,alignment);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_lv_tlsf_aligned_allocate_4d0744'] if isc else 0x4d0744)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1,0xfffffff0],[0,64],[0,4,8,32],[0,1],[0,1,15,16,17,0xfffffff0],[1,16],[0,1]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_TLSF_ALIGNMENT_CHILD_CONTRACTS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':7,'limits':['Zero/nonzero adjusted sizes, small/full alignment inputs, block NULL/present, leading gap0/small/large/wrapped, second alignment correction, configuration and gap assertions/messages, ordered child calls/config reads/result/SP matched.','All TLSF helpers controlled; actual block splitting/free lists/arena/data ownership and hardware/full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
