from pathlib import Path
import tempfile,subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-color-map-round168';S=D/'candidate.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_color_format_src_4b05a4',str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  engines.append((u,isc))
 count=0
 for high in [0,0x100,0x80000000,0xffffff00]:
  for low in range(256):
   outs=[]
   for u,isc in engines:
    u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,high|low);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_color_format_src_4b05a4'] if isc else 0x4b05a4)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000;outs.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)))
   assert outs[0]==outs[1],(high,low,outs);count+=1
 receipt={'status':'PASS_NATIVE_AMBIQ_COLOR_FORMAT_MAP','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual mapper executes with no child cuts; allbytevalues plusfourhighbitpatterns,exactreturn/SP compared.','Formatmapping alone doesnotprovehardware rendering orfullimagecoverage.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
