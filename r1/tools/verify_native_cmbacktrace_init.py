#!/usr/bin/env python3
"""Pinned upstream initialization versus native private-state and copy contracts."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-cmbacktrace-init';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'cmbacktrace-init-runtime.o';assert sha(obj)==r['linked_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/cmbacktrace/native-init-placement.ld';states={};digest=hashlib.sha256();count=0;copy_calls=0;log_calls=0;raw_return_equal=True
 bounds=[(0x20037eb8,0x2003beb8,0x27000,0xc4610),(0x20037eb8,0x20037eb8,0x27000,0xc4610),(0x20037eb8,0x2003beb8,0x27000,0x27000),(0x2003beb8,0x20037eb8,0x27000,0xc4610),(0x20037eb8,0x2003beb8,0xc4610,0x27000)]
 rng=random.Random(0x588a4);samples=[b'',b'a',b'A'*19,b'B'*20,b'C'*21,b'D'*64,bytes([128,255,1,2,3]),bytes(rng.randrange(1,256) for _ in range(40))];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
  for bound_index,values in enumerate(bounds):
   elf=d/'test.elf';binary=d/'text.bin';defs=dict(zip(['r1_cmb_stack_start','r1_cmb_stack_end','r1_cmb_code_start','r1_cmb_code_end'],values));defs['r1_retained_log_printf_sink']=0x20000201;subprocess.run(['arm-none-eabi-ld','-T',str(layout),*['--defsym='+k+'='+hex(v) for k,v in defs.items()],str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
   syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert {name:syms[name] for name in ['fw_name','hw_ver','sw_ver','init_ok','main_stack_start_addr','main_stack_size','code_start_addr','code_size']}==dict(fw_name=0x2002e8e4,hw_ver=0x2002e8f9,sw_ver=0x2002e90e,init_ok=0x20007a1c,main_stack_start_addr=0x20007a24,main_stack_size=0x20007a28,code_start_addr=0x20007a2c,code_size=0x20007a30)
   decoded={}
   for image in [analysis,elf]:
    for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
     m=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
     if m:decoded[int(m[1],16)]=(m[2],m[3].split('@')[0].strip())
   registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
   def hook(u,address,size,_):
    st=states[id(u)]
    if address==(0x20000200 if st['source'] else 0x7f030):
     pointer=u.reg_read(UC_ARM_REG_R0);text=bytearray()
     for i in range(512):
      ch=u.mem_read(pointer+i,1)[0]
      if not ch:break
      text.append(ch)
     st['logs'].append(text.hex());u.reg_write(UC_ARM_REG_R0,0x55aa55aa);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
    assert not st['source'] or not 0x27000<=address<0xc4d08
    if address==(syms['r1_native_strncpy'] if st['source'] else 0x277d8):st['copies'].append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)])
    mnemonic,operands=decoded.get(address,('',''))
    if not mnemonic.startswith('str'):return
    names,mem=operands.split('[',1);names=[x.strip() for x in names.rstrip(', ').split(',')];terms=mem.split(']',1)[0].split(',');base=terms[0].strip()
    if base=='sp':return
    target=u.reg_read(registers[base]);
    if len(terms)>1:target+=int(terms[1].strip()[1:],0) if terms[1].strip().startswith('#') else u.reg_read(registers[terms[1].strip()])
    target&=0xffffffff
    if not 0x20000000<=target<0x2003e000:return
    width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
    for i,name in enumerate(names):st['writes'].append([target+i*width,width,u.reg_read(registers[name])&((1<<(8*width))-1)])
   machines=[]
   for source in range(2):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
    if not source:
     for address,value in zip([0x588fc,0x58904,0x58908,0x5890c],values):u.mem_write(address,struct.pack('<I',value))
   for samples3,fill,initial_flag in itertools.product(itertools.product(samples,repeat=3),[0,0x96],[0,1]):
    results=[];returns=[]
    for candidate,u in enumerate(machines):
     u.mem_write(0x20000000,bytes([fill])*0x3e000);u.mem_write(0x20007a1c,bytes([initial_flag]));pointers=[0x20001000,0x20001400,0x20001800]
     for pointer,data in zip(pointers,samples3):u.mem_write(pointer,data+b'\0')
     initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],pointers):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     st={'source':candidate,'copies':[],'writes':[],'logs':[]};states[id(u)]=st
     try:u.emu_start((syms['cm_backtrace_init'] if candidate else 0x588a4)|1,0x20000100,count=100000)
     except Exception as error:raise RuntimeError((bound_index,[x.hex() for x in samples3],candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from error
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     for address,size,value in st['writes']:initial[address-0x20000000:address-0x20000000+size]=value.to_bytes(size,'little')
     actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,('store reconciliation',bound_index)
     returns.append(u.reg_read(UC_ARM_REG_R0));results.append([st['copies'],st['writes'],st['logs'],hashlib.sha256(actual).hexdigest()])
    raw_return_equal &= returns[0]==returns[1]
    if results[0]!=results[1]:
     failure=dict(bound_index=bound_index,bounds=values,samples=[x.hex() for x in samples3],fill=fill,initial_flag=initial_flag,results=results,upstream_sha256=r['upstream_source_sha256']);(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
    count+=1;copy_calls+=len(results[0][0]);log_calls+=len(results[0][2]);digest.update(json.dumps([values,[x.hex() for x in samples3],fill,initial_flag,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,source_copy_calls_per_side=copy_calls,error_log_calls_per_side=log_calls,trace_sha256=digest.hexdigest(),full_nonstack_ram_write_order_copy_args_callee_integer_and_stack_checked=True,executed_store_observer_with_full_ram_reconciliation=True,source_upstream_init_and_source_copy_provider=True,upstream_unmodified=True,retained_error_logger_fixture=True,error_log_pointer_content_normalized=True,linker_bound_values_are_explicit_fixtures=True,canonical_bound_case_present=True,zero_stack_and_zero_code_distinguished=True,wrapped_range_cases=True,prior_init_flag_sticky_on_error=True,array_twenty_first_bytes_preserved=True,raw_r0_equal=raw_return_equal,raw_void_return_not_equivalence_claim=True,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),runtime_object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Noncanonical range values are explicit linker/literal test fixtures; they do not alter the authenticated on-disk image or prove another image layout.','Only initialization is source-admitted; other upstream fault/unwind functions compiled in the raw translation unit remain separate R1 adaptation/native gates.','Retained logger, full raw void-return/caller scratch/APSR/private frame, source image linker configuration and whole-image byte identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
