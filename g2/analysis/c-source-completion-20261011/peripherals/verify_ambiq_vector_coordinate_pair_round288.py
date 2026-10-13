from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_ERR_WRITE_UNMAPPED
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-vector-coordinate-pair-round288';S=D/'candidate.c';ARRAY=0x20073cd4
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entry='audio_uart_ambiq_vector_data_pair_53d87c'
if '--selected' in sys.argv:assert S.read_text() in (R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-mfpu=fpv4-sp-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entry,'-Wl,--defsym=audio_uart_lv_array_push_488506=0x180001','-Wl,--defsym=audio_uart_lvgl_log=0x180011','-Wl,--defsym=audio_uart_ambiq_vector_path_data_20073cd4='+hex(ARRAY),str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,x,y,first,second,rounding,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  events=[];pushes=0;outputs=[]
  def string(a):
   out=bytearray()
   while True:
    c=u.mem_read(a,1)[0];a+=1
    if not c:return out.decode()
    out.append(c);assert len(out)<300
  def hook(u,a,size,unused):
   nonlocal pushes
   if a==(0x180000 if isc else 0x488506):
    assert u.reg_read(UC_ARM_REG_R0)==ARRAY;pointer=u.reg_read(UC_ARM_REG_R1);outputs.append(pointer);assert pointer%4==0 and len(set(outputs))==len(outputs);events.append(['append',ARRAY,bytes(u.mem_read(pointer,4)).hex()]);pushes+=1;ret=first if pushes==1 else second
    if mutation:u.reg_write(UC_ARM_REG_FPSCR,(u.reg_read(UC_ARM_REG_FPSCR)&~(3<<22))|(((rounding+1)&3)<<22))
    u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif a==(0x180010 if isc else 0x44d25c):
    regs=[u.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];stack=struct.unpack('<II',u.mem_read(u.reg_read(UC_ARM_REG_SP),8));events.append(['log',regs[0],string(regs[1]),regs[2],string(regs[3]),string(stack[0]),string(stack[1])]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,1<<30);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_FPSCR,rounding<<22);u.reg_write(UC_ARM_REG_R0,x);u.reg_write(UC_ARM_REG_R1,y);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym[entry] if isc else 0x53d87c)|1,0x600000,count=4000)
  except UcError as err:assert err.errno==UC_ERR_WRITE_UNMAPPED;fault='unmapped_fail_stop_store'
  assert bool(fault)==(first&255!=1 or second&255!=1)
  assert pushes==(1 if first&255!=1 else 2)
  if not fault:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_FPSCR),None if fault else u.reg_read(UC_ARM_REG_SP),fault
 count=0
 values=[0,1,0xffffffff,16777217,0xfeffffff,0x7fffffff,0x80000000,0x80000001]
 for c in itertools.product(values,values,[0,1,257],[0,1,257],range(4),[0,1]):
  n=run(False,*c);a=run(True,*c)
  if n!=a:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n');raise AssertionError(c)
  count+=1
 receipt={'status':'PASS_NATIVE_VECTOR_COORDINATE_PAIR','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'child_cuts':2,'limits':['Both signed32 conversions before first append; float bytes/finalFPSCR match allfourroundingmodes including childmodechanges,lowbyte result gates/diagnostics/fail-stop existence/returningSP. Real append/logger,FPUownership/othercontrolmodes,pointerfault/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
