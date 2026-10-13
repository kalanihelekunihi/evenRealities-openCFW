from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-program-startup-round231';S=D/'candidate.c';P=0x20001000;PTR=0x20002000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_child_514846'];native=[0x514846];cuts=[0x101010]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native522920');z=selected.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native522920')[0]+selected[a:z if z>=0 else len(selected)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_instruction_upload_522920']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,count,address,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([seed])*32);events=[];trace=[];modified=False
  def hook(uc,a,n,user):
   nonlocal modified
   if a!=(cuts[0] if isc else native[0]):return
   r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];events.append(r)
   if not modified and (mutation==1 and r[0]==196 or mutation==2 and r[0]==200):
    uc.mem_write(P,W(0x12345678)+W(0x87654321));modified=True
   uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if P<=a<P+32:trace.append((a,n,bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,address if mode else P);u.reg_write(UC_ARM_REG_R1,count);u.reg_write(UC_ARM_REG_R2,address);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);entry=sym['audio_uart_nema_rop_blend_mode_522956' if mode else 'audio_uart_nema_instruction_upload_522920'] if isc else 0x522956 if mode else 0x522920;u.emu_start(entry|1,0x600000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;return events,trace,bytes(u.mem_read(P,32)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=[(0,count,address,seed,m) for count,address,seed,m in itertools.product([0,1,2,3,4],[0,31,0xffffffff],[0,165],range(3))]
 cases += [(1,0,value,seed,m) for value,seed,m in itertools.product([0,1,0xffffffff],[0,165],range(3))]
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':b},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_NEMA_GENERIC_INSTRUCTION_UPLOAD_ROP_MODE','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Address command evenzero count,two fresh words per upload,pointer advance,count0..4,fullwidth address/value,child-mutated words,ordered reads/events/full32bytes/SP matched.','Generic uploader has no embedded GPU opcode array; startup5138a4 remains unselected pending instruction meaning. Actual emitter/program memory/ownership/faults/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
