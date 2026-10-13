from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-list-state-round234';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=[];native=[];cuts=[]
entries=['audio_uart_nema_last_cl_id_51418e','audio_uart_nema_last_submission_id_514194','audio_uart_nema_cl_get_bound_5144fa'];orig=[0x51418e,0x514194,0x5144fa]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('/* Native51418e');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('/* Native51418e')[0]+text[a:z if z>=0 else len(text)])
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL),'-Wl,--defsym=audio_uart_nema_last_submission=0x20002e08','-Wl,--defsym=audio_uart_nema_command_state_20073bf0=0x20073bf0']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,mode,value,ctx):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(CELL,W(ctx));u.mem_write(ctx+4,W(value));u.mem_write(0x20002e08,W(value));u.mem_write(0x20073bf0+20,W(value))
  u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[mode]] if isc else orig[mode])|1,0x600000,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(ctx,32)).hex()
 cases=list(itertools.product(range(3),[0,1,0x7fffffff,0x80000000,0xffffffff,0x20001001],[CTX,CTX+512]))
 for c in cases:assert run(False,*c)==run(True,*c),c
 receipt={'status':'PASS_NATIVE_LIST_STATE_ACCESSORS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Native pointer/word load return,SP,state match. Data placement/lifecycle and pointer faults/full-image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
