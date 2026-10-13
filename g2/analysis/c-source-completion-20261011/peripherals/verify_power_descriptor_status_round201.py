from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-power-descriptor-round201';P=0x20001000;W=lambda x:struct.pack('<I',x)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
rows=json.loads((D/'provenance.json').read_text())['rows'];sources=[D/'candidate.c',B/'root-nema-power-status-round200/candidate.c',R/'components/audio/uart_thread_source_candidate/byte_copy.c']
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Source-owned configuration recovered from authenticated table6becb0.');z=selected.index('#include <stdint.h>',a);f=Path(t)/'selected-descriptor.c';f.write_text(sources[0].read_text().split('/* Source-owned')[0]+selected[a:z]);a=selected.index('/* Native47f90c..47f942:');g=Path(t)/'selected-status.c';g.write_text(sources[1].read_text().split('/* Native47f90c')[0]+selected[a:]);sources=[f,g,sources[2]]
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_power_status_47f90c']+[str(p) for p in sources]+['-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,status,index,present,bits,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*64);trace=[]
  for row in rows:
   address=int(row['words'][2],16)
   if address:u.mem_write(address,W(bits))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+64 or 0x40000000<=a<0x40100000:trace.append((access,a,n,(v&((1<<(8*n))-1)) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if status:u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,P if present else 0);native=0x47f90c;name='audio_uart_nema_power_status_47f90c'
  else:u.reg_write(UC_ARM_REG_R0,P if present else 0);u.reg_write(UC_ARM_REG_R1,index);native=0x47ef18;name='audio_uart_power_peripheral_descriptor_47ef18'
  u.emu_start((sym[name] if isc else native)|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return trace,bytes(u.mem_read(P,64)),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)
 indexes=list(range(36))+[255,256,257,0xa5a50014,0xffffffff];cases=list(itertools.product([0,1],indexes,[0,1],[0,0xffffffff,0x40000,1],[0,165]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_trace':a[0],'source_trace':b[0]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_DESCRIPTOR_STATUS_REAL_COPY','cases':len(cases),'selected':'--selected' in sys.argv,'child_cuts':0,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'limits':['All34table rows, invalid and highbit indexes, lowbyte status truncation, NULL output, four status patterns, initial seeds; full64outputbytes, ordered output/MMIO accesses/result/SP matched. Actual selected copy executes.','RAM-backed MMIO has no peripheral side effects; source table relocation/layout and invalid descriptor register faults/physical hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
