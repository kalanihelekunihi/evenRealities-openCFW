#!/usr/bin/env python3
"""Verify native/source entry control flow using explicit external provider fixtures."""
import hashlib,itertools,json,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-application-entry';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PROVIDERS=[('nrf_log_init',0x79af4,2),('r1_adc_error',0x4e5bc,1),('nrf_log_default_backends_init',0x7968c,0),('cm_backtrace_init',0x588a4,3),('ble_dfu_buttonless_async_svci_init',0x52018,0),('nrf_drv_clock_init',0x788c8,0),('r1_boot_ctor_run',0x4e1e4,0),('r1_peripheral_module_init',0x50384,0),('r1_device_module_init',0x5c4c8,0),('r1_structured_log_mode_get',0x914ec,0),('r1_structured_log_format',0x91638,3),('nrf_log_frontend_std_0',0x799c0,2),('r1_reset_reason_nordic_adapter',0x77e98,0)]
REGIONS=[('scr',0x75ff8,4),('version',0x75ffc,12),('hardware',0x76008,12),('build',0x76014,44),('ring',0x76040,32),('log_bounds',0x76060,8),('sdk',0x76068,28),('callback_cell',0x76084,4)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_application_entry.o';assert sha(obj)==r['units'][0]['object_sha256'] and sorted(r['units'][0]['undefined'])==sorted(p[0] for p in PROVIDERS)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_application_entry_verification.ld';states={};digest=hashlib.sha256();count=0;call_counts={name:0 for name,_,_ in PROVIDERS};call_counts['initialized_callback']=0;first_handoffs=None
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};data=[]
  for name,address,length in REGIONS:
   q=d/f'{name}.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.app.entry.'+name,'-O','binary',str(elf),str(q)],check=True);raw=q.read_bytes();assert len(raw)==length and raw==app.read_bytes()[address-0x27000:address-0x27000+length];data.append((address,raw))
  native={a:(name,n) for name,a,n in PROVIDERS};compiled={syms[name]&~1:(name,n) for name,_,n in PROVIDERS};machines=[]
  analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if m:decoded[int(m[1],16)]=(m[2],m[3].split('@')[0].strip())
  regs={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};regs.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  def hook(u,address,size,_):
   st=states[id(u)];selected=(compiled if st['source'] else native).get(address)
   if address==(0x20000400 if st['source'] else 0x45e64):selected=('initialized_callback',0)
   if selected:
    name,n=selected;args=[u.reg_read(regs[f'r{i}']) for i in range(n)];st['calls'].append([name,args]);result=0x55aa55aa
    if name=='nrf_log_init':result=st['statuses'][0]
    elif name=='ble_dfu_buttonless_async_svci_init':result=st['statuses'][1]
    elif name=='nrf_drv_clock_init':result=st['statuses'][2]
    elif name=='r1_structured_log_mode_get':
     assert st['mode_index']<3;result=st['modes'][st['mode_index']];st['mode_index']+=1
    elif name=='initialized_callback':st['callback_seen']=True
    elif name=='r1_adc_error' and st['callback_seen']:
     assert args==[15];st['terminal_errors']+=1
     if st['terminal_errors']==3:st['end']={'pc':address,'sp':u.reg_read(UC_ARM_REG_SP),'lr':u.reg_read(UC_ARM_REG_LR)};u.emu_stop();return
    u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   assert not st['source'] or not 0x27000<=address<0xc4d08,('source executed native body',hex(address))
   mnemonic,operands=decoded.get(address,('',''))
   if not mnemonic.startswith('str'):return
   names,mem=operands.split('[',1);base=mem.split(']',1)[0].split(',')[0].strip()
   if base=='sp':return
   target=u.reg_read(regs[base]);terms=mem.split(']',1)[0].split(',')
   if len(terms)>1:target+=int(terms[1].strip()[1:],0)
   target&=0xffffffff
   if target==0xe000ed10:
    assert mnemonic in ['str','str.w'];st['writes'].append([target,4,u.reg_read(regs[names.strip().rstrip(',')])])
   else:assert target>=0x2003e000,('unexpected nonstack store',hex(address),hex(target))
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,0x1000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   if source:
    for address,raw in data:u.mem_write(address,raw)
  for statuses,modes,initial_scr in itertools.product(itertools.product([0,1,0xffffffff],repeat=3),itertools.product(range(8),repeat=3),[0,0xffffffff]):
   results=[];handoffs=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);u.mem_write(0x20006540,struct.pack('<I',0x20000401 if candidate else 0x45e65));u.mem_write(0xe000ed10,struct.pack('<I',initial_scr));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i in range(13):u.reg_write(regs[f'r{i}'],0x12345600+i)
    st={'source':candidate,'statuses':statuses,'modes':modes,'mode_index':0,'calls':[],'writes':[],'callback_seen':False,'terminal_errors':0,'end':None};states[id(u)]=st
    try:u.emu_start((syms['r1_native_application_entry'] if candidate else 0x75f64)|1,0x20000100,count=100000)
    except Exception as error:raise RuntimeError((statuses,modes,initial_scr,candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from error
    assert st['end'] and st['terminal_errors']==3 and st['callback_seen'];actual_scr=struct.unpack('<I',u.mem_read(0xe000ed10,4))[0];assert st['writes']==[[0xe000ed10,4,initial_scr|4]] and actual_scr==initial_scr|4
    ram=bytearray(u.mem_read(0x20000000,0x3e000));struct.pack_into('<I',ram,0x6540,0x45e65);expected=bytearray(b'\x96'*0x3e000);struct.pack_into('<I',expected,0x6540,0x45e65);assert ram==expected
    results.append([st['calls'],st['writes'],actual_scr]);handoffs.append(st['end'])
   if results[0]!=results[1]:
    failure=dict(statuses=statuses,modes=modes,initial_scr=initial_scr,results=results,source_sha256=sha(ROOT/'r1/components/runtime/native_application_entry.c'));(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError(failure)
   if first_handoffs is None:first_handoffs=handoffs
   for name,args in results[0][0]:call_counts[name]+=1
   count+=1;digest.update(json.dumps([statuses,modes,initial_scr,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,call_counts=call_counts,trace_sha256=digest.hexdigest(),first_terminal_boundaries=first_handoffs,provider_and_initialized_callback_fixtures=True,provider_executable_bodies_supplied=False,source_application_entry_body=True,candidate_native_body_execution_forbidden=True,all_three_status_success_error_combinations=True,mode_queue_triples_zero_to_seven=True,two_scr_initial_states=True,three_post_callback_fatal_iterations=True,typed_call_arguments_order_mmio_write_and_nonstack_ram_checked=True,callback_pointer_relocation_normalized=True,source_numeric_and_string_bytes=sum(n for _,_,n in REGIONS),runtime_no_unresolved=False,unresolved_source_providers=sorted(p[0] for p in PROVIDERS),initialized_callback_source_owned=False,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['All external providers and initialized callback are named typed fixtures; this does not prove their execution, native raw call ABI or source integration.','Entry is non-returning; private stack, LR/APSR/caller scratch, physical MMIO and error nonreturn behavior remain separate gates.','Source-owned initialization/callback, full startup/application dependencies, original compiler/shared data placement and byte-identical image integration remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
