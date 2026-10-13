from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-font-metrics-dpi-round252';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=[];native=[];cuts=[]
entries=['font_metrics_dpi_252'];orig=[0x526ba4]
metrics_text=(R/'components/audio/uart_thread_source_candidate/display_font_face_metrics.c').read_text()
for axis,offset in [('x',4),('y',8)]:assert f'((int32_t)((uint32_t){axis}_dpi*word(r,{offset}u)+36u)/72)' in metrics_text
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,x,y,dx,dy):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CTX,b''.join(W(v) for v in [0,x,y,dx,dy]));u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R10,CTX);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,CTX);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  stop=0x600000 if isc else 0x526be4;u.emu_start((sym[entries[0]] if isc else orig[0])|1,stop,count=3000);assert u.reg_read(UC_ARM_REG_PC)==stop
  values=list(struct.unpack('<II',u.mem_read(P,8))) if isc else [u.reg_read(UC_ARM_REG_R8),u.reg_read(UC_ARM_REG_R9)]
  return values,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(CTX,20)).hex()
 cases=list(itertools.product([0,64,1024,0x40000000,0xffffffff],[0,64,1024,0x40000000,0xffffffff],[0,72,96,0x80000000,0xffffffff],[0,72,96,0x80000000,0xffffffff]))
 for c in cases:assert run(False,*c)==run(True,*c),c
 receipt={'status':'PASS_NATIVE_METRICS_DPI_ARITHMETIC_BLOCK','cases':len(cases),'selected_arithmetic_text_verified':True,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Arithmetic-only native526ba4..526be4 register outputs/SP/input-state matched with wrapped32bit products. Full metrics function,ordered accesses/concurrent mutations remain unqualified.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
