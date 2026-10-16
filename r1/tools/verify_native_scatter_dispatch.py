#!/usr/bin/env python3
"""Observe source/native RAM initialization and stop before application entry."""
import hashlib,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scatter-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_scatter_dispatch.o';assert sha(obj)==r['units'][0]['object_sha256']
 bp=BASE/'native-scatter-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-scatter-runtime.o';assert sha(bo)==bundle['linked_sha256'] and bundle['undefined_symbols']==['r1_native_application_entry']
 for report in [r,bundle]:
  for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_scatter_dispatch_verification.ld';states={};digest=hashlib.sha256();handoffs=[];provider_counts={'native':{'decompress':0,'zero':0},'compiled':{'decompress':0,'zero':0}}
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';table=d/'table.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(bo),'-o',str(elf)],check=True)
  for section,target in [('.text',binary),('.r1.scatter.regions',table)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(target)],check=True)
  table_sha256=hashlib.sha256(table.read_bytes()).hexdigest()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_scatter_regions']==0xc43ec and syms['r1_native_application_entry']==0x20000201
  analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if match:decoded[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  native={0x286f4:'decompress',0x3bc68:'zero'};compiled={syms['r1_native_scatter_decompress']:'decompress',syms['r1_native_scatter_zero']:'zero'}
  def hook(u,address,size,_):
   st=states[id(u)]
   if address==(syms['r1_native_runtime_entry'] if st['source'] else 0x27208):st['runtime_entries']+=1
   if address in [0x75f64,0x20000200]:
    assert address==(0x20000200 if st['source'] else 0x75f64);st['boundary']={'pc':address,'sp':u.reg_read(UC_ARM_REG_SP),'lr':u.reg_read(UC_ARM_REG_LR),'registers':{name:u.reg_read(reg) for name,reg in registers.items() if name in [f'r{i}' for i in range(13)]}};u.emu_stop();return
   assert not st['source'] or not 0x27000<=address<0xc4d08,('candidate executed native code',hex(address))
   selected=(compiled if st['source'] else native).get(address)
   if selected:st['providers'].append([selected,*[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]])
   mnemonic,operands=decoded.get(address,('',''))
   if mnemonic.startswith('str'):
    regs,mem=operands.split('[',1);names=[x.strip() for x in regs.rstrip(', ').split(',')];terms=mem.split(']',1)[0].split(',');base=terms[0].strip()
    if base=='sp':return
    target=u.reg_read(registers[base])
    if len(terms)>1:
     term=terms[1].strip();target+=int(term[1:],0) if term.startswith('#') else u.reg_read(registers[term])
    target&=0xffffffff;width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
   elif mnemonic.startswith('stm'):
    base,regs=operands.split(',',1);base=base.strip().rstrip('!')
    if base=='sp':return
    assert mnemonic in ['stmia','stmia.w','stm'];target=u.reg_read(registers[base]);names=[x.strip() for x in regs.strip().strip('{}').split(',')];width=4
   else:return
   if 0x20000000<=target<0x2003e000:
    for i,name in enumerate(names):st['writes'].append([target+i*width,width,u.reg_read(registers[name])&((1<<(8*width))-1)])
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   if source:u.mem_write(0xc43ec,table.read_bytes())
  rng=random.Random(0x283a0);seeds=[bytes([value])*0x3e000 for value in [0,1,0x7f,0x80,0x96,0xff]]+[rng.randbytes(0x3e000) for _ in range(8)]
  for index,initial_ram in enumerate(seeds):
   results=[];boundaries=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,initial_ram);u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000301)
    for i in range(13):u.reg_write(globals()[f'UC_ARM_REG_R{i}'],0x12345600+i)
    st={'source':candidate,'writes':[],'providers':[],'boundary':None,'runtime_entries':0};states[id(u)]=st;u.emu_start((syms['r1_native_scatterload'] if candidate else 0x283a0)|1,0x20000300,count=2000000);assert st['boundary'] is not None and st['runtime_entries']==1
    initial=bytearray(initial_ram)
    for address,size,value in st['writes']:initial[address-0x20000000:address-0x20000000+size]=value.to_bytes(size,'little')
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,(index,'store reconciliation')
    results.append([st['providers'],st['writes'],hashlib.sha256(actual).hexdigest()]);boundaries.append(st['boundary'])
    for provider,*_ in st['providers']:provider_counts['compiled' if candidate else 'native'][provider]+=1
   assert results[0]==results[1],(index,results)
   assert results[0][0]==[['decompress',0xc4610,0x200064a8,0x195c],['zero',0xc4d08,0x20007e04,0x340b4]]
   handoffs.append(boundaries);digest.update(json.dumps([index,hashlib.sha256(initial_ram).hexdigest(),results[0],boundaries],sort_keys=True).encode())
 receipt=dict(comparisons=len(seeds),provider_counts=provider_counts,trace_sha256=digest.hexdigest(),handoffs=handoffs,full_ram_and_provider_arguments_and_nonstack_write_order_checked=True,executed_store_observer_with_full_ram_reconciliation=True,unicorn_memory_write_hooks_disabled=True,candidate_native_code_execution_forbidden=True,source_dispatch_providers_and_callback_configuration=True,source_runtime_handoff_body=True,runtime_entry_calls_per_case=1,application_body_terminal_boundary_fixture=True,application_body_executed=False,runtime_no_unresolved=False,unresolved_source_providers=['r1_native_application_entry'],handoff_sp_equal=all(a['sp']==b['sp'] for a,b in handoffs),handoff_raw_registers_equal=all(a['registers']==b['registers'] for a,b in handoffs),initialized_data_source_ownership=False,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),table_sha256=table_sha256,limitations=['Application entry is a named stop-before-execution boundary; its source provider remains unresolved.','Handoff PC/provider relocations and raw register/LR/private stack effects are not full startup ABI/image proof.','Authenticated compressed input is a fixture; initialized-data source ownership, reset SP setup, source application startup and whole-image identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='handoffs'}))
if __name__=='__main__':main()
