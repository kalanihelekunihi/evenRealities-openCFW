#!/usr/bin/env python3
"""Exact early-return power branch comparison; fixture code is not a provider."""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';raw=OTA.read_bytes()[32:]
SRC=D/'power_entry_prefix_probe.c';DESC=R/'g2/components/foundation/power_domain/power_domain.c';IRQ=R/'g2/components/audio/source_candidate_20261010/irq_provider.c';TIMING=R/'g2/components/audio/clock_timing_offline/timing.c'
with tempfile.TemporaryDirectory(prefix='g2-power-prefix-') as td:
 t=Path(td);elf=t/'prefix.elf';ld=t/'prefix.ld';ld.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-mthumb','-O1','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-T,'+str(ld),str(SRC),str(DESC),str(IRQ),str(TIMING),'-o',str(elf)],check=True)
 target_objects={}
 for source in (SRC,DESC,IRQ,TIMING):
  obj=t/(source.stem+'-m55.o');dep=t/(source.stem+'-m55.d')
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O1','-ffreestanding','-fno-builtin','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)],check=True)
  target_objects[str(source.resolve())]=dict(object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),dependency_manifest=dep.read_text())
 with elf.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
 def run(name,source,domain,enabled,spot_failure=False,stop_before_critical=False,stop_after_critical=False,initial_mask=0,complete_ready=False,complete_disabled=False,cut_delay=False,final_status_fail=False,shared_nonlast=False,shared_last=False,otp_guard=False,audio_ready=False,audio_disabled=False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
  for a,b in sections:u.mem_write(a,b)
  u.mem_map(0x20000000,0x80000);u.mem_map(0x40020000,0x3000)
  u.mem_map(0xe000e000,0x2000);u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000))
  if spot_failure:
   u.mem_write(0x100f20,b'\x05\x20\x70\x47') # movs r0,#5; bx lr
   u.mem_write(0x20073274,struct.pack('<I',0x100f21))
  # All domain enable masks clear or set; allows a branch probe independent of which valid domain is selected.
  for a in (0x40021004,0x4002100c):u.mem_write(a,struct.pack('<I',0xffffffff if enabled else 0))
  if complete_disabled:
   u.mem_write(0x40021004,struct.pack('<I',1));u.mem_write(0x40021008,struct.pack('<I',0x30000001))
  if shared_nonlast:
   u.mem_write(0x40021004,struct.pack('<I',6));u.mem_write(0x40021008,struct.pack('<I',0x1e))
  if shared_last:
   u.mem_write(0x40021004,struct.pack('<I',2));u.mem_write(0x40021008,struct.pack('<I',0x1e))
  if otp_guard:
   u.mem_write(0x4002000c,struct.pack('<I',0x21));u.mem_write(0x40021008,struct.pack('<I',1<<21))
  if audio_ready:
   u.mem_write(0x4002100c,struct.pack('<I',0));u.mem_write(0x40021010,struct.pack('<I',0))
  if audio_disabled:
   u.mem_write(0x4002100c,struct.pack('<I',4));u.mem_write(0x40021010,struct.pack('<I',4))
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100f01);u.reg_write(UC_ARM_REG_R0,domain);u.reg_write(UC_ARM_REG_PRIMASK,initial_mask)
  writes=[];callbacks=[];lastpcs=[];entered=[];status_reads=[]
  def wh(_u,_acc,a,size,value,_):
   if a<0x2007d000 or a>=0x40000000:writes.append([a,size,value])
   if complete_ready and a==0x40021004:
    _u.mem_write(0x40021008,struct.pack('<I',0x30000001))
   if audio_ready and a==0x4002100c:
    _u.mem_write(0x40021010,struct.pack('<I',4))
   if audio_disabled and a==0x4002100c:
    _u.mem_write(0x40021010,struct.pack('<I',0))
   if (complete_disabled or shared_last) and a==0x40021004:
    _u.mem_write(0x40021008,struct.pack('<I',0))
  u.hook_add(UC_HOOK_MEM_WRITE,wh)
  def rh(cpu,_access,a,size,value,_):
   if a==0x40021008:
    status_reads.append([a,size])
    if final_status_fail and len(status_reads)==2:
     cpu.mem_write(a,struct.pack('<I',0))
  u.hook_add(UC_HOOK_MEM_READ,rh)
  def ch(cpu,pc,size,_):
   lastpcs.append(pc)
   if pc==(symbols['stock_save_irq']&~1 if source else 0x473940):entered.append('critical')
   if pc==(symbols['audio_wait5']&~1 if source else 0x480826):entered.append('wait5')
   if cut_delay and pc==(symbols['audio_delay_us']&~1 if source else 0x4807a0):
    entered.append(['delay_us',cpu.reg_read(UC_ARM_REG_R0)])
    cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR));return
   if stop_before_critical and not source and pc==0x47f680:
    cpu.emu_stop();return
   if stop_after_critical and not source and pc==0x47f69c:
    cpu.emu_stop();return
   if pc==0x100f20:
    ptr=cpu.reg_read(UC_ARM_REG_R2)
    callbacks.append([cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),struct.unpack('<I',cpu.mem_read(ptr,4))[0]])
  u.hook_add(UC_HOOK_CODE,ch)
  entry=(symbols['power_'+name+'_prefix_probe'] if source else (0x47f5b8 if name=='enable' else 0x47f7ae))|1
  try:u.emu_start(entry,0x100f00,count=6000)
  except Exception as exc:raise RuntimeError((name,source,domain,enabled,spot_failure,[hex(x) for x in lastpcs[-20:]],callbacks)) from exc
  result=dict(writes=writes,callbacks=callbacks,entered=entered,status_reads=status_reads,regs=[bytes(u.mem_read(a,4)).hex() for a in (0x40021004,0x40021008,0x4002100c)])
  result['primask']=u.reg_read(UC_ARM_REG_PRIMASK)
  if not (stop_before_critical or stop_after_critical):result.update(ret=u.reg_read(UC_ARM_REG_R0),pc=u.reg_read(UC_ARM_REG_PC))
  else:result['prefix_boundary_reached']=(u.reg_read(UC_ARM_REG_PC)==(0x47f69c if stop_after_critical else 0x47f680) if not source else u.reg_read(UC_ARM_REG_R0)==0xfeedbeef)
  return result
 rows=[]
 for name in ('enable','disable'):
  for domain in (0,1,7,11,15,28,29,30,31,32,33,34,35,255):
   for enabled in (False,True):
    if domain<34 and enabled!=(name=='enable'):continue
    a=run(name,False,domain,enabled);b=run(name,True,domain,enabled)
    assert a==b,(name,domain,enabled,a,b)
    rows.append(dict(entry=name,domain=domain,enable_register_set=enabled,result=a))
 # Stock product's early CRYPTO/OTP-off failure after descriptor and enable check.
 for domain in (0x17,0x117):
  a=run('enable',False,domain,False);b=run('enable',True,domain,False)
  assert a==b,('crypto_otp_off',domain,a,b)
  rows.append(dict(entry='enable_crypto_otp_off',domain=domain,enable_register_set=False,result=a))
 for domain in (0,0x100):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('enable',False,domain,False,spot_failure,initial_mask=mask,complete_ready=True)
    b=run('enable',True,domain,False,spot_failure,initial_mask=mask,complete_ready=True)
    assert a==b,('ready_success',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='enable_ready_success',domain=domain,enable_register_set=False,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (30,0x11e):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('enable',False,domain,False,spot_failure,initial_mask=mask,audio_ready=True)
    b=run('enable',True,domain,False,spot_failure,initial_mask=mask,audio_ready=True)
    assert a==b,('audio_ready_enable',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='audio_ready_enable',domain=domain,initial_mask=mask,spot_failure=spot_failure,result=a))
 for mask in (0,1):
  for spot_failure in (False,True):
   a=run('enable',False,0,False,spot_failure,initial_mask=mask,complete_ready=True,final_status_fail=True)
   b=run('enable',True,0,False,spot_failure,initial_mask=mask,complete_ready=True,final_status_fail=True)
   assert a==b,('enable_final_status_fail',mask,spot_failure,a,b)
   rows.append(dict(entry='enable_final_status_fail',domain=0,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (0,0x100):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('disable',False,domain,True,spot_failure,initial_mask=mask,complete_disabled=True)
    b=run('disable',True,domain,True,spot_failure,initial_mask=mask,complete_disabled=True)
    assert a==b,('disable_ready_success',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='disable_ready_success',domain=domain,enable_register_set=True,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (30,0x11e):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('disable',False,domain,True,spot_failure,initial_mask=mask,audio_disabled=True)
    b=run('disable',True,domain,True,spot_failure,initial_mask=mask,audio_disabled=True)
    assert a==b,('audio_ready_disable',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='audio_ready_disable',domain=domain,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (3,0x103):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('disable',False,domain,True,spot_failure,initial_mask=mask,shared_nonlast=True)
    b=run('disable',True,domain,True,spot_failure,initial_mask=mask,shared_nonlast=True)
    assert a==b,('disable_shared_nonlast',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='disable_shared_nonlast',domain=domain,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (3,0x103):
  for mask in (0,1):
   for spot_failure in (False,True):
    a=run('disable',False,domain,True,spot_failure,initial_mask=mask,shared_last=True)
    b=run('disable',True,domain,True,spot_failure,initial_mask=mask,shared_last=True)
    assert a==b,('disable_shared_last',domain,mask,spot_failure,a,b)
    rows.append(dict(entry='disable_shared_last',domain=domain,initial_mask=mask,spot_failure=spot_failure,result=a))
 for domain in (0x1d,0x11d):
  for mask in (0,1):
   a=run('disable',False,domain,True,initial_mask=mask,otp_guard=True)
   b=run('disable',True,domain,True,initial_mask=mask,otp_guard=True)
   assert a==b,('disable_otp_rev_guard',domain,mask,a,b)
   rows.append(dict(entry='disable_otp_rev_guard',domain=domain,initial_mask=mask,result=a))
 for mask in (0,1):
  for spot_failure in (False,True):
   a=run('enable',False,0,False,spot_failure,initial_mask=mask,cut_delay=True)
   b=run('enable',True,0,False,spot_failure,initial_mask=mask,cut_delay=True)
   assert a==b,('enable_timeout',mask,spot_failure,a,b)
   rows.append(dict(entry='enable_timeout_with_delay_cut',domain=0,initial_mask=mask,spot_failure=spot_failure,result=a))
 out=dict(status='PASS_BOUNDED_POWER_ENTRY_FAMILIES_NOT_PROVIDER',cases=len(rows),groups={name:sum(x['entry']==name for x in rows) for name in sorted({x['entry'] for x in rows})},public_early_return_cases=sum(x['entry'] not in ('enable_ready_success','disable_ready_success','audio_ready_enable','audio_ready_disable','disable_shared_nonlast','disable_shared_last','enable_final_status_fail','enable_timeout_with_delay_cut') for x in rows),ordinary_enable_ready_cases=sum(x['entry']=='enable_ready_success' for x in rows),audio_enable_ready_cases=sum(x['entry']=='audio_ready_enable' for x in rows),audio_disable_ready_cases=sum(x['entry']=='audio_ready_disable' for x in rows),ordinary_disable_ready_cases=sum(x['entry']=='disable_ready_success' for x in rows),ordinary_disable_nonlast_cases=sum(x['entry']=='disable_shared_nonlast' for x in rows),ordinary_disable_last_cases=sum(x['entry']=='disable_shared_last' for x in rows),otp_revision_guard_cases=sum(x['entry']=='disable_otp_rev_guard' for x in rows),enable_final_status_failure_cases=sum(x['entry']=='enable_final_status_fail' for x in rows),enable_timeout_delay_cut_cases=sum(x['entry']=='enable_timeout_with_delay_cut' for x in rows),official_payload_sha256=hashlib.sha256(raw).hexdigest(),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),descriptor_sha256=hashlib.sha256(DESC.read_bytes()).hexdigest(),irq_source_sha256=hashlib.sha256(IRQ.read_bytes()).hexdigest(),timing_source_sha256=hashlib.sha256(TIMING.read_bytes()).hexdigest(),m55_target_objects=target_objects,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),rows=rows,limits=['40 complete public-entry early returns: invalid mapping, already-on/off, stock-corrected CRYPTO OTP-off, and pre-B1 OTP-in-use guard.','8 ordinary domain-0 ready-enable and 8 ready-disable full public-entry cases use a synthetic status register that changes on the MMIO power write.','4 enable timeout cases return 4 after five original/source wait5 delay calls; delay_us is an explicit call-argument cut in this joint suite, with separate prior timing provider proof.','4 full ordinary enable final-status failure cases, 8 non-last shared-domain disables, and 8 last-member shared-domain ready-off disables use synthetic status and enable-register state.','8 audio domain-30 ready enables and 8 audio domain-30 ready disables use synthetic audio MMIO and SPOT stimulus 4; other audio domains remain open.','Fixture-only source sentinel excludes other active domains, GPU/clock, OTP/CRYPTO, timeout delay body and physical power behavior; no archive admission.'])
 (D/'power-entry-prefix-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),'power entry prefix cases')
