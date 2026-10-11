#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2]
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
src=R/'g2/components/bootloader/initializer_callbacks/startup_runtime.c';provider=R/'g2/components/bootloader/source_candidate_20261010/pcm22_timer_service.c'
elf=H/'startup-timer-slot.elf';cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_boot_startup_spot_dispatch','-Wl,--gc-sections','-Wl,--defsym=spotmgr_init_42abbc_native=0x10030001','-Wl,--defsym=opencfw_boot_control_critical_save=0x10040001','-Wl,--defsym=opencfw_pcm22_spot_timer_stop=0x10040011','-Wl,--defsym=opencfw_hal_delay_us=0x10040021','-Wl,--defsym=opencfw_hal_status_poll=0x10040031','-Wl,--unresolved-symbols=ignore-all',str(src),str(provider),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
msr_sites={a+i for a,b in segs for i in range(len(b)-3) if b[i:i+2] in (b'\x84\xf3',b'\x80\xf3') and b[i+2:i+4]==b'\x10\x88'}
def run(source,rev,var,mode,seed,first_ret,saved):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x100000)
 def w(p,x):u.mem_write(p,struct.pack('<I',x))
 def rd(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 w(0x4002000c,rev);w(0x20000098,var);w(0x40020028,seed);w(0x40020060,seed);u.mem_write(0x2000055a,bytes([mode]))
 u.mem_write(0x20026e38,b'\xa5'*60);u.reg_write(UC_ARM_REG_SP,0x2003eff0);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[];trace=[]
 u.mem_write(0x42a072,b'\x00\xbf\x00\xbf')
 for site in msr_sites:u.mem_write(site,b'\x00\xbf\x00\xbf')
 lower={0x41b8ec:'critical',0x428378:'mode2',0x428a94:'mode7',0x41ccd6:'stop'} if not source else {0x10040000:'critical',sym['opencfw_pcm22_sequence2b']&~1:'mode2',sym['opencfw_pcm22_sequence7b']&~1:'mode7',0x10040010:'stop'}
 def hook(emu,pc,size,data):
  trace.append((hex(pc),hex(emu.reg_read(UC_ARM_REG_SP)),hex(emu.reg_read(UC_ARM_REG_LR))))
  if pc in (0x42abbc,0x10030000):emu.reg_write(UC_ARM_REG_R0,first_ret);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR));return
  if pc in lower:
   calls.append((lower[pc],emu.reg_read(UC_ARM_REG_R0)))
   if lower[pc]=='critical':emu.reg_write(UC_ARM_REG_R0,saved)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((sym['opencfw_boot_startup_spot_dispatch'] if source else 0x41ce52)|1,0x10000000,count=30000)
 target=rd(0x20026e64);assert target==((sym['opencfw_pcm22_timer_service']|1) if source else 0x42a04b)
 result=[u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200271a9,6)).hex(),rd(0x40020028),rd(0x40020060)]
 before=bytes(u.mem_read(0x20026e38,60));calls.clear();u.reg_write(UC_ARM_REG_R0,seed);u.reg_write(UC_ARM_REG_LR,0x10000001)
 try:u.emu_start(target,0x10000000,count=100)
 except Exception as exc:raise AssertionError((source,hex(u.reg_read(UC_ARM_REG_PC)),calls,trace[-20:])) from exc
 assert bytes(u.mem_read(0x20026e38,60))==before
 result.extend((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),tuple(name for name,arg in calls),rd(0x20000558)))
 return result
cases=[]
for rev,var in ((35,2),(36,0)):
 for mode,seed,first_ret,saved in itertools.product((0,2,7,255),(0,0xa5a5a5a5),(0,7),(0,1)):
  a,b=run(False,rev,var,mode,seed,first_ret,saved),run(True,rev,var,mode,seed,first_ret,saved)
  assert a==b,(rev,var,mode,hex(seed),first_ret,saved,a,b)
  cases.append((rev,var,mode,seed,first_ret,saved))
receipt=dict(status='PASS',cases=len(cases),stock_image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),provider_sha256=hashlib.sha256(provider.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='PCM2.2 branch; first callback and four lower providers are explicit hooks. PRIMASK MSR is replaced with two NOPs in both oracle images because Unicorn rejects the instruction; the source and original both restore the saved mask, but architectural PRIMASK mutation is not executed in this fixture. Compares installed pointer, dispatcher and timer callback branch/callee sequence, return and table integrity; lower effects and root startup remain separate. Scalar M4 execution; M55 archive separate.')
(H/'startup-timer-slot-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS startup timer slot',len(cases))
