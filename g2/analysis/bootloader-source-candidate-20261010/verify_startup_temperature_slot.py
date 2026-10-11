#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
src=R/'g2/components/bootloader/initializer_callbacks/startup_runtime.c';provider=R/'g2/components/bootloader/initializer_callbacks/pcm22_runtime_native/pcm22_runtime_hooks.c'
elf=H/'startup-temperature-slot.elf';cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_startup_spot_dispatch','-Wl,--gc-sections','-Wl,--defsym=spotmgr_init_42abbc_native=0x10030001','-Wl,--defsym=opencfw_bl_mspi_mode_enter=0x10040001','-Wl,--defsym=opencfw_boot_startup_temperature=0x10040011','-Wl,--defsym=opencfw_boot_control_delay_status_change=0x10040021','-Wl,--unresolved-symbols=ignore-all',str(src),str(provider),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,rev,var,device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob);u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x100000)
 def w(p,x):u.mem_write(p,struct.pack('<I',x))
 def rd(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 w(0x4002000c,rev);w(0x20000098,var);w(0x40020028,0);w(0x40020060,0);w(0x40021008,device);w(0x40021010,audio);w(0x400083e0,0x110)
 u.mem_write(0x20026e38,b'\xa5'*60);u.reg_write(UC_ARM_REG_SP,0x2003eff0);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_FPSCR,0)
 calls=[];lower={0x41bf84:'mspi',0x41ca2c:'temperature',0x41d21c:'delay'} if not source else {0x10040000:'mspi',0x10040010:'temperature',0x10040020:'delay'}
 def hook(emu,pc,size,data):
  if pc in (0x42abbc,0x10030000):emu.reg_write(UC_ARM_REG_R0,first_ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR));return
  if pc in lower:
   name=lower[pc]
   if name=='mspi':args=(emu.reg_read(UC_ARM_REG_R0),);assert args==(29,);ret=mspi_ret
   elif name=='temperature':
    args=(emu.reg_read(UC_ARM_REG_S0),);assert args==(0xc2200000,);ret=temp_ret;ptr=emu.reg_read(UC_ARM_REG_R0);assert 0x2003e000<=ptr<0x2003f000;w(ptr,0x12345678);w(ptr+4,0xabcdef01)
   else:args=tuple(emu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3));assert args==(2500,0x400083e0,1,0);ret=delay_ret
   calls.append((name,args));emu.reg_write(UC_ARM_REG_R0,ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((sym['opencfw_boot_startup_spot_dispatch'] if source else 0x41ce52)|1,0x10000000,count=30000)
 target=rd(0x20026e40);assert target==((sym['opencfw_pcm22_temperature_init']|1) if source else 0x42ac55)
 result=[u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200271a9,6)).hex(),rd(0x40020028),rd(0x40020060)]
 before=bytes(u.mem_read(0x20026e38,60));calls.clear();u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.emu_start(target,0x10000000,count=200)
 assert bytes(u.mem_read(0x20026e38,60))==before
 result.extend((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_FPSCR),tuple(calls),rd(0x40021008),rd(0x40021010)))
 return result
cases=[]
for rev,var in ((35,2),(36,0)):
 for device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask in itertools.product((0,1),(0,2),(0,1),(0,1),(0,1),(0,7),(0,1)):
  a,b=run(False,rev,var,device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask),run(True,rev,var,device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask)
  assert a==b,(rev,var,device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask,a,b)
  cases.append((rev,var,device,audio,mspi_ret,temp_ret,delay_ret,first_ret,mask))
receipt=dict(status='PASS',cases=len(cases),stock_image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),provider_sha256=hashlib.sha256(provider.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Cortex-M33 model executes the locked VFP body and compiled M4 hard-float candidate. First callback and three lower providers are controlled boundaries. Compares installed pointer, branch/callee ABI including S0=-40, return, stack, PRIMASK and FPSCR. Lower effects, full sensor values and root startup remain open; M55 archive separate.')
(H/'startup-temperature-slot-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS startup temperature slot',len(cases))
