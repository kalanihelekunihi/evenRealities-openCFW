from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-alignment-connected-round219';S=B/'root-tlsf-aligned-allocate-round213/candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['g2_tlsf_find_suitable','g2_file_close_error'];native=[0x4d0484,0x4d09b4];cuts=[0x101010,0x101020]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4d0744');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((B/'root-tlsf-aligned-allocate-round213/candidate.c').read_text().split('/* Native4d0744')[0]+selected[a:z if z>=0 else len(selected)])
 trim=Path(t)/'trim.c';trim.write_text((B/'root-tlsf-trim-leading-round215/candidate.c').read_text())
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_tlsf_aligned_allocate_4d0744']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),str(trim)]+[str(R/'components/audio'/p) for p in ['tlsf_adjust_request_candidate/adjust.c','tlsf_split_block_candidate/split.c','tlsf_prepare_allocation_candidate/prepare.c','file_pool_free_candidate/tlsf_align.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_block_next.c','file_pool_free_candidate/tlsf_mark_free.c','file_pool_free_candidate/tlsf_leaf.c','file_pool_free_candidate/tlsf_lists.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_free_lists.c']]+['-ffunction-sections','-Wl,--gc-sections','-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,size,alignment,present,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(0x20005000,bytes(4096));u.mem_write(0x20005074,W(0x20005000)*900);u.mem_write(P,bytes([seed])*1024);u.mem_write(P+4,W(513));events=[];trace=[]
  def string(a):
   v=bytearray()
   while True:
    c=bytes(u.mem_read(a+len(v),1))
    if c==b'\0':return v.decode()
    v.extend(c)
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append((i,r if i==0 else [string(r[0]),string(r[1]),uc.reg_read(UC_ARM_REG_R2)]));ret=(P if present and r[1]!=0 else 0) if i==0 else 0xa5a5a5a5
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if 0x78f4b4<=a<=0x78f4c8:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,alignment);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_lv_tlsf_aligned_allocate_4d0744'] if isc else 0x4d0744)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,1024)).hex(),bytes(u.mem_read(0x20005000,4096)).hex()
 cases=list(itertools.product([0,1,16,64,128],[4,8,16,32,64],[0,1],[0,165]))
 for c in cases:
  try:a=run(False,*c);b=run(True,*c)
  except Exception:
   print('FAULT_CASE',c);raise
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_TLSF_TRIM_LEADING_CONNECTED','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':2,'limits':['Actual size/split/align/mark-free/prev-free/link-next bodies, real insert/mapping/free-list bodies, assertion calls/full1024byte arena/full4096byte pool/flash configuration trace/result/SP matched.','Suitable-block lookup and diagnostic handler controlled; full allocator ownership/pointer faults/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
