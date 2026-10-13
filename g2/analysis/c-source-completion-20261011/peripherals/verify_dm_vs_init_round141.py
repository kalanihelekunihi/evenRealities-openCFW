from pathlib import Path
import hashlib,json,subprocess,tempfile,random,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-dm-vs-init-round141';S=D/'candidate.c'
if '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_boot_public.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,DmDevVsInit',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];symbol=next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='DmDevVsInit');entry=symbol['st_value'];size=symbol['st_size'];section=elf.get_section(symbol['st_shndx']);body=section.data()[(entry&~1)-section['sh_addr']:(entry&~1)-section['sh_addr']+size]
 assert body==blob[0x4b308c-0x438000:0x4b3096-0x438000],body.hex()
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR];rng=random.Random(141);count=0
 for i in range(256):
  inputs=[rng.getrandbits(32) for _ in range(13)]+[0x200ff000,0x600001];outs=[]
  for native in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,data in segs:u.mem_write(a,data)
   u.mem_write(0x200fefe0,b'\xa5'*32);u.reg_write(UC_ARM_REG_CPSR,0x33)
   for reg,v in zip(regs,inputs):u.reg_write(reg,v)
   u.emu_start((0x4b308c if native else entry)|1,0x600000,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append(([u.reg_read(reg) for reg in regs],bytes(u.mem_read(0x200fefe0,32))))
  assert outs[0]==outs[1];assert outs[0][0][0]==inputs[7];count+=1
 receipt={'status':'PASS_DM_VS_INIT_NATIVE_REGISTER_STACK_AND_BODY_BYTES','cases':count,'function_body_byte_equal':True,'body_bytes':size,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['C file uses named native assembly,not portable C. All general registers/SP/LR and32stack bytes compared; incoming R7 returned.','Ten-byte function equality does not prove complete image coverage/layout/data/byte equality or hardware.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
