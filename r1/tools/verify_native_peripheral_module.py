#!/usr/bin/env python3
"""Native ten-call dispatcher order, callback PRIMASK state and last raw R0."""
import hashlib,itertools,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-peripheral-module';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CALLS=[('r1_led_ldo_device_bind',0x502c4),('r1_native_rtc_cached_device',0x50dc0),('r1_vbat_adc_handle_cache',0x9143c),('r1_yhm_device_handles_initialize',0x50578),('r1_ppg_device_bind',0x50944),('r1_motion_interrupt_input_lookup',0x50128),('r1_touch_device_bind',0x51310),('r1_i2c2_handle_cache',0x50f08),('r1_i2c5_nfc_resource_registration',0x50464),('r1_native_watchdog_hw_handle_init',0x500d4)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_peripheral_module.o';assert sha(obj)==r['units'][0]['object_sha256'] and sorted(r['units'][0]['undefined'])==sorted(n for n,_ in CALLS)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_peripheral_module_verification.ld';states={};digest=hashlib.sha256();count=0;callbacks=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};native={a:i for i,(_,a) in enumerate(CALLS)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(CALLS)};machines=[]
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is None:assert not st['source'] or not 0x27000<=address<0xc4d08;return
   st['trace'].append([index,u.reg_read(UC_ARM_REG_PRIMASK)])
   if st['actions'][index] is not None:u.reg_write(UC_ARM_REG_PRIMASK,st['actions'][index])
   u.reg_write(UC_ARM_REG_R0,st['statuses'][index]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x50384);statuses=[[0]*10,list(range(10)),[0xffffffff]*10]+[[int(i==bad) for i in range(10)] for bad in range(10)]+[[rng.getrandbits(32) for _ in range(10)] for _ in range(32)];actions=[[None]*10,[i&1 for i in range(10)],[1-(i&1) for i in range(10)]]
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for values,mask,action in itertools.product(statuses,range(2),actions):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x3e000);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0xabcdef01)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    states[id(u)]={'source':candidate,'trace':[],'statuses':values,'actions':action};u.emu_start((syms['r1_peripheral_module_init'] if candidate else 0x50384)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and bytes(u.mem_read(0x20000000,0x3e000))==b'\x96'*0x3e000
    trace=states[id(u)]['trace'];assert [x[0] for x in trace]==list(range(10));results.append([trace,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK)])
   assert results[0]==results[1] and results[0][1]==values[-1],(values,mask,action,results)
   count+=1;callbacks+=10;digest.update(json.dumps([values,mask,action,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),typed_callback_order_primask_return_r0_stack_callee_integer_and_nonstack_ram_checked=True,callback_bodies_are_named_fixtures=True,provider_bodies_integrated=False,source_dispatcher_body=True,candidate_native_body_execution_forbidden=True,initial_primask_zero_and_one=True,per_callback_interrupt_state_changes=True,seeded_random_callback_results=True,runtime_no_unresolved=False,unresolved_source_providers=sorted(n for n,_ in CALLS),unicorn_memory_write_hooks_disabled=True,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['All ten external provider bodies are typed no-argument fixtures; incoming/raw argument-register liveness and actual provider execution remain open.','Sampled last raw R0, PRIMASK and callee preservation do not prove all caller scratch/APSR/private frame or physical interrupt behavior.','Provider source integration, startup/initialization ownership, original compiler/shared-data placement and byte-identical whole-image integration remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
