from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-ring-register-emit-round207';S=D/'candidate.c';CELL=0x20073db0;P=0x20001000;ALT=0x20002000;DATA=0x20003000;W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('extern volatile uint32_t audio_uart_nema_ring_descriptor[];');S=Path(t)/'selected.c';S.write_text('#include <stdint.h>\n'+selected[a:])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_nema_register_emit_523e92','-Wl,--defsym=audio_uart_nema_ring_descriptor='+hex(CELL),'-Wl,--defsym=audio_uart_nema_buffer_flush_5140ea=0x101011','-Wl,--defsym=audio_uart_nema_reg_write_514046=0x101021',str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,capacity,index,reg,value,seed,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(P)+W(DATA)+W(0x40090000)+W(capacity));u.mem_write(P,bytes([seed])*64);u.mem_write(P+16,W(index));u.mem_write(ALT,bytes([90])*64);u.mem_write(ALT+16,W(9));u.mem_write(DATA,bytes([seed])*256);events=[];trace=[]
  def hook(uc,a,n,user):
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
   if a==(0x101010 if isc else 0x5140ea):
    events.append(('flush',r0,bytes(uc.mem_read(P,64)).hex(),bytes(uc.mem_read(DATA,256)).hex()))
    if mutation:uc.mem_write(CELL,W(ALT));uc.mem_write(CELL+8,W(0xfffffff0))
   elif a==(0x101020 if isc else 0x514046):events.append(('write',r0,r1))
   else:return
   uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,v,user):
   if CELL<=a<CELL+16 or P<=a<P+64 or ALT<=a<ALT+64 or DATA<=a<DATA+256:trace.append((access,a,n,v&((1<<(8*n))-1) if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,reg);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_nema_register_emit_523e92'] if isc else 0x523e92)|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CELL,16)),bytes(u.mem_read(P,64)),bytes(u.mem_read(ALT,64)),bytes(u.mem_read(DATA,256))
 cases=list(itertools.product([0,1,2,4,8,16,0x80000000,0xffffffff],[0,1,3,7,15],[0,0x388,0x1000000,0xff000000,0xffffffff],[0,0x12345678],[0,165],[0,1]))
 for c in cases:
  a=run(False,*c);b=run(True,*c)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':c,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_RING_REGISTER_EMIT','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':2,'limits':['Signed-capacity/wrap/tail-padding, high-byte submit policy, mutable descriptor reload after flush, wrapped physical writepointer, ordered accesses/full400bytes/SP compared.','Small valid data indexes; extreme pointer faults/real flush/MMIO/data ownership/hardware remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
