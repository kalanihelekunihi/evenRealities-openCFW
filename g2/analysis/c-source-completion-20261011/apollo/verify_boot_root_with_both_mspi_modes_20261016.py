"""Execute stock bytes and independent source leaves; callback bodies controlled."""
from pathlib import Path
import sys,json,hashlib,struct,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
from elftools.elf.elffile import ELFFile
def current_elf_info(path):
 with path.open('rb') as handle:
  image=ELFFile(handle)
  assert image.elfclass==32 and image.little_endian and image['e_machine']=='EM_ARM'
  segments=[dict(address=s['p_vaddr'],data=s.data()) for s in image.iter_segments()
            if s['p_type']=='PT_LOAD']
  symbols={s.name:s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()
           if s.name and s['st_shndx']!='SHN_UNDEF'}
 return segments,symbols
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
segments,symbols=current_elf_info(args.elf)
spot_elf=ROOT/"g2/analysis/c-source-completion-20261011/apollo/spot-m4-oracle/startup_runtime.elf"
spot_segments,spot_symbols=current_elf_info(spot_elf)
memory_elf=ROOT/"g2/build/c-firmware/20261016/boot-memory-m33-overlay/memory.elf"
memory_segments,memory_symbols=current_elf_info(memory_elf)
mspi_elf=ROOT/"g2/build/c-firmware/20261016/boot-mspi-m33-overlay/mspi.elf"
mspi_segments,mspi_symbols=current_elf_info(mspi_elf)
entries={'write':('opencfw_boot_startup_sleep_fields_write',0x41c9ca,0x41ca08),'read':('opencfw_boot_startup_sleep_fields_read',0x41ca0c,0x41ca2c)}
for name,lo,hi in [('20',0x41cdca,0x41cde0),('24',0x41cde0,0x41cdfa),('28',0x41cdfa,0x41ce10),('30',0x41ce10,0x41ce26),('34',0x41ce26,0x41ce3c),('38',0x41ce3c,0x41ce52)]:entries[name]=('opencfw_boot_startup_hook'+name,lo,hi)
entries['init']=('opencfw_boot_startup_power_initialize',0x41c4b4,0x41c7de)
CHILDREN=[4334894, 4309370, 4309720, 4308868, 4307224, 4309792, 4330824, 4312658, 4307920, 4308534, 4307180]
stock_clock_cuts={0x41d1c0:'delay',0x41d246:'poll',0x41d3e4:'gpio',0x41d90e:'power_read',0x41d92c:'power_update',0x41ca5c:'prepare',0x41bf84:'mode_enter',0x41c17a:'mode_leave',0x41e348:'cache',0x41caa2:'finish'}
source_clock_names={'opencfw_hal_delay_us':'delay','opencfw_hal_status_poll':'poll','opencfw_legacy_gpio_mode':'gpio','opencfw_power_register_read':'power_read','opencfw_bl_power_register_update':'power_update','opencfw_low_power_prepare':'prepare','opencfw_bl_mspi_mode_enter':'mode_enter','opencfw_bl_mspi_mode_leave':'mode_leave','opencfw_cache_invalidate':'cache','opencfw_low_power_finish':'finish'}
source_clock_cuts={symbols[k]&~1:v for k,v in source_clock_names.items()}
source_child_names={0x42252e:'opencfw_boot_shutdown_debug_release',0x41c17a:'opencfw_bl_mspi_mode_leave',0x41c2d8:'opencfw_boot_control_query',0x41bf84:'opencfw_bl_mspi_mode_enter',0x41b918:'opencfw_boot_startup_trim_version',0x41c320:'opencfw_boot_startup_info_cache',0x421548:'opencfw_boot_device_mode_wait',0x41ce52:'opencfw_boot_startup_spot_dispatch',0x41bbd0:'opencfw_boot_startup_mcu_memory',0x41be36:'opencfw_boot_startup_shared_memory',0x41b8ec:'opencfw_boot_control_critical_save'}
ORACLE_M55_CUTS=False
NATIVE_QUERY=True
NATIVE_CRITICAL=True
NATIVE_DEBUG_RELEASE=True
NATIVE_INFO_CACHE=True
NATIVE_TRIM_VERSION=True
NATIVE_SPOT_DISPATCH=True
NATIVE_SHARED_MEMORY=True
NATIVE_MCU_MEMORY=True
NATIVE_DEVICE_MODE_WAIT=True
NATIVE_MODE_ENTER=True
NATIVE_MODE_LEAVE=True
LOCAL_SPOT_STOCK={"bl009_slot8_noop":0x42d849,"bl009_slot34_enable":0x42d693,"bl009_slot38_disable":0x42d6a7,"bl009_slot18_timing":0x42d5f9,"bl009_slot1c_config":0x42d61f,"bl009_special_slot18_timing":0x42f3db,"bl009_special_slot1c_config":0x42f401,"pcm21_slot14_config":0x42bd8d,"pcm21_slot18_timing":0x42bda1,"pcm21_slot1c_timing":0x42bdbd}
SPOT_POINTER_NORMALIZE={(spot_symbols[name]|1):address for name,address in LOCAL_SPOT_STOCK.items()}
trace={}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0x410000,0x35000),(0x08000000,0x100000),(0x0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0xe000e000,0x1000),(0xe001e000,0x1000),(0x40000000,0x300000),(0x47ff0000,0x10000)]:u.mem_map(lo,sz)
 if source:
  u.mem_write(0x410000,blob)
  for seg in segments:u.mem_write(seg['address'],seg['data'])
  for seg in spot_segments:u.mem_write(seg['address'],seg['data'])
  for seg in memory_segments:u.mem_write(seg['address'],seg['data'])
  for seg in mspi_segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 w(0xe000ed14,f.get('scr',0));w(0xe001e300,f.get('value',0));u.mem_write(0x20001000,b'\xa5'*4)
 if name not in ['read','write','init']:w(0x20026e38+int(name,16),0x080e0101 if f['present'] else 0)
 
 if name=='init':
  for p in [0x4000885c,0x40020250,0x4002021c,0x400201bc,0x40004044,0x40004120,0x40020448,0x4002036c,0x40020088,0x40020044,0x4002004c,0x40020374,0x40020080,0x400201b0,0x40020344,0x4002034c,0x40020358,0x40020354,0x4002037c,0x40020380,0x400211c8]:w(p,f.get('seed',0))
  w(0x40021028,f.get('shared_status',0));w(0x40021024,f.get('shared_power_seed',0));w(0x4002102c,f.get('shared_config_seed',0));w(0x40021040,f.get('shared_ctrl_seed',0));w(0x400201bc,f.get('gate29',0));w(0x40021008,f.get('info_status',0));w(0x40021108,f.get('gate',0)<<4);w(0x4002000c,f['revision']);w(0x20000098,f['variant']);w(0x200267f8,0x1f01600d if f.get('cached',True) else 0)
  for p in range(0x2002704c,0x2002708c,4):w(p,0xa5a5a5a5)
  for p in [0x200271a3,0x200271a8,0x2000009c,0x200271a5]:u.mem_write(p,bytes([f.get('saved',0) if p==0x200271a8 else (f.get('skipdebug',0) if p==0x200271a3 else (f.get('modebyte',0) if p==0x200271a5 else 0))]))
  for slot in [0x20026e58,0x20026e5c,0x20026e68]:w(slot,0x080e0101 if f.get('present',False) else 0)
 w(0x40008858,(0x5af0<<16)|f['clock_flags']);w(0x4000885c,f['clock_guard'])
 events=[];writes=[];done=False;in_clock=False
 def hook(cpu,p,size,_):
  nonlocal done,in_clock
  # The selected archive is M55. Unicorn's M33 model rejects CSET/CSEL;
  # execute their exact flag/register effects in this comparison fixture.
  if ORACLE_M55_CUTS and source and p==0x0800a626:
   zero=(u.reg_read(a.UC_ARM_REG_CPSR)>>30)&1
   u.reg_write(a.UC_ARM_REG_R0,zero)
   u.reg_write(a.UC_ARM_REG_PC,0x0800a62b);return
  if ORACLE_M55_CUTS and source and p==0x0800a62c:
   zero=(u.reg_read(a.UC_ARM_REG_CPSR)>>30)&1
   if zero:u.reg_write(a.UC_ARM_REG_R0,0)
   u.reg_write(a.UC_ARM_REG_PC,0x0800a631);return
  if ORACLE_M55_CUTS and source and p==0x0800a650:
   zero=(u.reg_read(a.UC_ARM_REG_CPSR)>>30)&1
   u.reg_write(a.UC_ARM_REG_R1,zero)
   u.reg_write(a.UC_ARM_REG_PC,0x0800a655);return
  if source and name=='init' and p==(symbols['opencfw_bl_mspi_mode_leave']&~1):
   u.reg_write(a.UC_ARM_REG_PC,mspi_symbols['opencfw_bl_mspi_mode_leave']);return
  if source and name=='init' and p==(symbols['opencfw_bl_mspi_mode_enter']&~1):
   u.reg_write(a.UC_ARM_REG_PC,mspi_symbols['opencfw_bl_mspi_mode_enter']);return
  if source and name=='init' and p==(symbols['opencfw_boot_startup_mcu_memory']&~1):
   u.reg_write(a.UC_ARM_REG_PC,memory_symbols['opencfw_boot_startup_mcu_memory']);return
  if source and name=='init' and p==(symbols['opencfw_boot_startup_shared_memory']&~1):
   u.reg_write(a.UC_ARM_REG_PC,memory_symbols['opencfw_boot_startup_shared_memory']);return
  if source and name=='init' and p==(symbols['opencfw_boot_startup_spot_dispatch']&~1):
   u.reg_write(a.UC_ARM_REG_PC,spot_symbols['opencfw_boot_startup_spot_dispatch']);return
  if source and NATIVE_MODE_ENTER:
   caller=u.reg_read(a.UC_ARM_REG_LR)&~1
   callback=struct.unpack('<I',u.mem_read(0x20026e3c,4))[0]&~1
   if callback and p==callback and 0x437090<=caller<0x437388:
    regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(3)]
    events.append(['shared-power',regs[0],regs[1],0 if regs[2]==0 else 'config'])
    u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p in (0x40,0x080f0050):
   events.append(['rom40-delay',u.reg_read(a.UC_ARM_REG_R0)])
   u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==0x08000000:done=True;u.emu_stop();return
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(u.mem_read(p,size)).hex()
  if p==((symbols['am_hal_pwrctrl_low_power_init_clockmux_fragment']&~1) if source else 0x41acb2):in_clock=True
  cuts=source_clock_cuts if source else stock_clock_cuts
  if in_clock and p in cuts and not ((NATIVE_MODE_ENTER and cuts[p]=='mode_enter') or (NATIVE_MODE_LEAVE and cuts[p]=='mode_leave')):
   kind=cuts[p];regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   fifth=struct.unpack('<I',u.mem_read(u.reg_read(a.UC_ARM_REG_SP),4))[0]
   if kind=='delay':event=[kind,regs[0]]
   elif kind=='poll':event=[kind,*regs,fifth]
   elif kind=='gpio':event=[kind,regs[0],u.mem_read(regs[1],1)[0] if regs[1] else None]
   elif kind in ['power_read','mode_enter','mode_leave']:event=[kind,regs[0]]
   elif kind in ['power_update','cache']:event=[kind,regs[0],regs[1]]
   else:event=[kind]
   events.append(event)
   if kind=='power_read' and regs[1]:w(regs[1],0xdeadbeef)
   if kind=='gpio' and regs[1]:u.mem_write(regs[1],b'\x5a')
   u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  source_device_dispatch=symbols['opencfw_boot_info_read_dispatch']&~1
  if NATIVE_DEVICE_MODE_WAIT and p in ((source_device_dispatch,0x4213e6) if source else (0x4213e6,)):
   regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   r0,r1,r2,r3=regs;irq=u.reg_read(a.UC_ARM_REG_PRIMASK)
   event=['0x421548',irq,r0,r1,r2,('stack-buffer' if 0x2003e000<=r3<0x20040000 else r3)]
   result=f.get('failure',0) if r1==f.get('fail_selector',0) else 0
   if not result:
    for word in range(r2):w(r3+word*4,0x87654321+word)
   events.append(event);u.reg_write(a.UC_ARM_REG_R0,result);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  shared_poll=((symbols['opencfw_hal_status_poll']&~1) if source else 0x41d246)
  if NATIVE_SHARED_MEMORY and p==shared_poll:
   regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   fifth=struct.unpack('<I',u.mem_read(u.reg_read(a.UC_ARM_REG_SP),4))[0]
   events.append(['shared-poll',*regs,fifth])
   if f.get('shared_poll_mirror'):
    w(0x40021028,(struct.unpack('<I',u.mem_read(0x40021028,4))[0]&~7)|(struct.unpack('<I',u.mem_read(0x40021024,4))[0]&7))
   u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  shared_power=((symbols['opencfw_boot_power_callback']&~1) if source else 0x41cd1a)
  if NATIVE_SHARED_MEMORY and p in ((shared_power,mspi_symbols['opencfw_boot_power_callback']&~1) if source else (shared_power,)):
   callback=struct.unpack('<I',u.mem_read(0x20026e3c,4))[0]
   if not callback:
    u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
   regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(3)]
   events.append(['shared-power',regs[0],regs[1],0 if regs[2]==0 else 'config'])
   u.reg_write(a.UC_ARM_REG_R0,0);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  debug_delay=((symbols['opencfw_boot_control_delay_status_change']&~1)
               if source else 0x41d21c)
  if NATIVE_DEBUG_RELEASE and p==debug_delay:
   regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
   events.append(['debug-delay',*regs])
   u.reg_write(a.UC_ARM_REG_R0,0)
   u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if name=='init':
   for index,original in enumerate(CHILDREN):
    if (NATIVE_QUERY and original==0x41c2d8) or (NATIVE_CRITICAL and original==0x41b8ec) or (NATIVE_DEBUG_RELEASE and original==0x42252e) or (NATIVE_INFO_CACHE and original==0x41c320) or (NATIVE_TRIM_VERSION and original==0x41b918) or (NATIVE_SPOT_DISPATCH and original==0x41ce52) or (NATIVE_SHARED_MEMORY and original==0x41be36) or (NATIVE_MCU_MEMORY and original==0x41bbd0) or (NATIVE_DEVICE_MODE_WAIT and original==0x421548) or (NATIVE_MODE_ENTER and original==0x41bf84) or (NATIVE_MODE_LEAVE and original==0x41c17a):continue
    entry=(symbols[source_child_names[original]]&~1) if source else original
    if p==entry or (source and original==0x421548 and p==original):
     r0=u.reg_read(a.UC_ARM_REG_R0);r1=u.reg_read(a.UC_ARM_REG_R1);r2=u.reg_read(a.UC_ARM_REG_R2);r3=u.reg_read(a.UC_ARM_REG_R3);irq=u.reg_read(a.UC_ARM_REG_PRIMASK)
     event=[hex(original),irq]
     if original in [0x41c17a,0x41bf84]:event+=[r0]
     if original==0x41be36:event+=[r0]
     if original==0x41bbd0:event+=[r0,bytes(u.mem_read(r0,1)).hex()]
     if original==0x421548:event+=[r0,r1,r2,('stack-buffer' if 0x2003e000<=r3<0x20040000 else r3)]
     result=0
     if original==0x41c2d8:event+=[r0];u.mem_write(r1,bytes([f.get('active',0)]))
     if original==0x41b918:w(r0,0x12345678)
     if original==0x421548:
      result=f.get('failure',0) if r1==f.get('fail_selector',0) else 0
      if not result:
       for word in range(r2):w(r3+word*4,0x87654321+word)
     if original==0x41b8ec:result=irq;u.reg_write(a.UC_ARM_REG_PRIMASK,1)
     events.append(event);u.reg_write(a.UC_ARM_REG_R0,result);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==0x080e0100:
   events.append(['callback',u.reg_read(a.UC_ARM_REG_PRIMASK)]) if name=='init' else events.append([u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)] if name=='24' else ['noarg'])
   u.reg_write(a.UC_ARM_REG_R0,f.get('status',7));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
 def write(cpu,access,p,size,value,_):writes.append([p,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x402fffff);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe001efff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,0x20001000 if name=='read' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('second',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 u.reg_write(a.UC_ARM_REG_R5,f['ambient_r5']);u.reg_write(a.UC_ARM_REG_R7,f['ambient_r7'])
 u.reg_write(a.UC_ARM_REG_R1,0x10203040);u.reg_write(a.UC_ARM_REG_R2,0x55667788);u.reg_write(a.UC_ARM_REG_R3,0x89abcdef)
 for reg in [4,6,8,9,10,11]:u.reg_write(getattr(a,f'UC_ARM_REG_R{reg}'),0xa0000000+reg)
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1]
 try:u.emu_start(pc|1,0,count=200000)
 except UcError as error:raise RuntimeError((source,name,hex(u.reg_read(a.UC_ARM_REG_PC)),hex(u.reg_read(a.UC_ARM_REG_LR)),events[-10:],error)) from error
 assert done
 if name=='init':return dict(registers=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)],callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],stack=u.reg_read(a.UC_ARM_REG_SP),ret=u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),calibration=bytes(u.mem_read(0x2002704c,64)).hex(),saved=bytes(u.mem_read(0x200271a8,1)).hex(),revisionflag=bytes(u.mem_read(0x2000009c,1)).hex(),spot_flags=bytes(u.mem_read(0x200271a9,6)).hex(),spot_slot_offsets=[i for i in range(0,60,4) if int.from_bytes(u.mem_read(0x20026e38+i,4),'little')],spot_slots=[SPOT_POINTER_NORMALIZE.get(int.from_bytes(u.mem_read(0x20026e38+i,4),'little'),int.from_bytes(u.mem_read(0x20026e38+i,4),'little')) if source else int.from_bytes(u.mem_read(0x20026e38+i,4),'little') for i in range(0,60,4)])
 return dict(ret=None if name=='read' else u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,output=bytes(u.mem_read(0x20001000,4)).hex(),irq=u.reg_read(a.UC_ARM_REG_PRIMASK))
fixtures=[]
for revision,saved,flags,r5,r7,guard in itertools.product([32,33,34,35,36],[0,1],[0,2,0x45,0x7f,0x20,0x0c,0x10],[0x20027064,0xa5b6c7d8],[0,0x11223344],[0,2]):
 fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=saved,present=True,irq=0,clock_flags=flags,ambient_r5=r5,ambient_r7=r7,clock_guard=guard))
legacy_fixtures=[]
for revision,variant,gate,seed,saved,present,irq in itertools.product([32,33,34,35,36],[0,1,2,3,4],[0,3],[0,0xffffffff],[0,1],[False,True],[0,1]):legacy_fixtures.append(dict(revision=revision,variant=variant,gate=gate,seed=seed,saved=saved,present=present,irq=irq))
for selector,status,active,skipdebug in itertools.product([0x210,0x245],[0,7],[0,1],[0,1]):legacy_fixtures.append(dict(revision=34,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,cached=False,fail_selector=selector,failure=status,gate29=8,active=active,skipdebug=skipdebug,modebyte=255))
for status,fail_selector,skipdebug in itertools.product([0,0x08000000],[0,0x204,0x245],[0,1]):
 legacy_fixtures.append(dict(revision=34,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,cached=False,fail_selector=fail_selector,failure=6 if fail_selector else 0,gate29=8,info_status=status,active=1,skipdebug=skipdebug,modebyte=255))
for failure,skipdebug,info_status in itertools.product([0,6],[0,1],[0,0x08000000]):
 legacy_fixtures.append(dict(revision=34,variant=0xffffffff,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,cached=False,fail_selector=0x244,failure=failure,gate29=8,info_status=info_status,active=1,skipdebug=skipdebug,modebyte=255))
for revision,shared_config_seed,shared_ctrl_seed in itertools.product([33,34,35,36],[0,0xffffffff],[0,0xffffffff]):
 legacy_fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,shared_status=7,shared_power_seed=7,shared_config_seed=shared_config_seed,shared_ctrl_seed=shared_ctrl_seed))
for revision,shared_config_seed in itertools.product([33,34,35,36],[0,0xffffffff]):
 legacy_fixtures.append(dict(revision=revision,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,shared_poll_mirror=True,shared_config_seed=shared_config_seed))
for f in legacy_fixtures:
 f.update(clock_flags=0x7f,ambient_r5=0xa5b6c7d8,ambient_r7=0x11223344,clock_guard=0);fixtures.append(f)
rows=[]
for f in fixtures:
 stock=run(False,'init',f);source=run(True,'init',f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(fixture=f,stock=stock,source=source),indent=2));raise AssertionError((f,stock,source))
 rows.append(dict(fixture=f,result=stock))
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r=dict(status='PASS_NATIVE_BOOT_ROOT_WITH_BOTH_MSPI_MODES_COMPOSED',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in entries.items()},comparisons=rows,limits=['Selected-archive root entry and C core execute, including selected query, critical-save, debug-release, information-cache, trim-version, SPOT, shared-memory, MCU-memory, device-mode gate and both MSPI mode bodies. All eleven root child entries run; debug delay-status, downstream device read, ROM timing and other lower contracts remain controlled.','Clockmux and runtime query modules were compiled for M33; SPOT installer source was independently compiled for M4; updated memory and MSPI sources were compiled for M33 in separately linked overlays. Named external callbacks and non-SPOT native leaves use authenticated stock bytes in both runs. Local static callback pointer identities are normalized to stock targets. This is a source comparison, not production selected M55 ELF execution; the M55 archive separately compiles and links.','R0-R3, R4-R11, SP, PRIMASK, ordered MMIO writes, local RAM, six SPOT flags and all 15 installed pointer slots are compared. SPOT-installed named callback bodies execute authenticated stock bytes on both sides; MSPI/shared/MCU power callbacks, status polls, the device-mode dispatcher, ROM delay and other lower providers remain controlled. ROM, product layout, hardware timing and whole-image equality remain outside this oracle.'])
r['isolated_spot_elf_sha256']=hashlib.sha256(spot_elf.read_bytes()).hexdigest()
r['spot_source_sha256']=hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/startup_runtime.c').read_bytes()).hexdigest()
r['mspi_source_sha256']=hashlib.sha256((ROOT/'g2/components/bootloader/platform_control/power_domains.c').read_bytes()).hexdigest()
r['mspi_overlay_elf_sha256']=hashlib.sha256(mspi_elf.read_bytes()).hexdigest()
r['memory_overlay_elf_sha256']=hashlib.sha256(memory_elf.read_bytes()).hexdigest()
r['device_mode_source_sha256']=hashlib.sha256((ROOT/'g2/components/bootloader/application_storage/device_mode_wait.c').read_bytes()).hexdigest()
r['shared_source_sha256']=hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/startup_memory_config.c').read_bytes()).hexdigest()
r['composed_child_coverage']={
 'debug_release_native_bytes_70':len(used&set(range(0x42252e,0x422574))),
 'info_cache_native_bytes_352':len(used&set(range(0x41c320,0x41c480))),
 'controlled_device_dispatch_calls':sum(sum(e[0]=='0x421548' for e in row['result']['events']) for row in rows),
 'mode_leave_native_bytes':len(used&set(range(0x41c17a,0x41c2d8))),
 'mode_enter_native_bytes':len(used&set(range(0x41bf84,0x41c0be))),
 'device_mode_native_bytes':len(used&set(range(0x421548,0x42156e))),
 'mcu_memory_native_bytes':len(used&set(range(0x41bbd0,0x41bd92))),
 'shared_memory_native_bytes':len(used&set(range(0x41be36,0x41bf3a))),
 'spot_dispatch_native_bytes':len(used&set(range(0x41ce52,0x41d0ee))),
 'trim_version_native_bytes_60':len(used&set(range(0x41b918,0x41b954))),
 'fixtures_with_info_reads':sum(any(e[0]=='0x421548' and len(e)>5 and e[5]=='stack-buffer' for e in row['result']['events']) for row in rows),
 'controlled_info_read_calls':sum(sum(e[0]=='0x421548' and len(e)>5 and e[5]=='stack-buffer' for e in row['result']['events']) for row in rows),
 'fixtures_with_trim_provider_read':sum(any(e[0]=='0x421548' and len(e)>3 and e[3]==0x244 for e in row['result']['events']) for row in rows),
 'fixtures_with_shared_poll_mirror':sum(bool(row['fixture'].get('shared_poll_mirror')) for row in rows),
 'fixtures_with_shared_match':sum(row['fixture'].get('shared_status')==7 for row in rows),
 'fixtures_with_shared_power':sum(any(e[0]=='shared-power' for e in row['result']['events']) for row in rows),
 'fixtures_with_spot_installed':sum(bool(row['result']['spot_slot_offsets']) for row in rows),
 'fixtures_with_debug_delay':sum(any(e[0]=='debug-delay' for e in row['result']['events']) for row in rows),
}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])
