#!/usr/bin/env python3
"""Compare scatter providers and authenticated initialized/BSS effects."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scatter-data';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_scatter_data.o';assert sha(obj)==r['units'][0]['object_sha256'] and not r['units'][0]['undefined']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_scatter_data_verification.ld';states={};digest=hashlib.sha256();counts=dict.fromkeys(['decompress','zero','official_decompress','official_zero'],0)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[];analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if match:decoded[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  def hook(u,address,size,_):
   st=states[id(u)];assert not st['source'] or not 0x27000<=address<0xc4d08
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
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x286f4);cases=[]
  for token in range(256):
   for extended_literal,extended_run,distance in itertools.product([1,2,7,8,255],[0,1,15,16,255],[0,1,2,7,255]):
    literals=(token&7) or extended_literal;run=(token>>4) or extended_run;data=bytes([token])+(bytes([extended_literal]) if not token&7 else b'')+(bytes([extended_run]) if not token>>4 else b'')+bytes(rng.randrange(256) for _ in range(literals-1))+(bytes([distance]) if token&8 else b'')
    output=literals-1+run+(2 if token&8 else 0)
    # A zero-output token is legal for size zero; positive-size loops need
    # another token. A final one-byte zero token supplies that progress.
    data+=b'\x11'
    for length in sorted(set([0,1,max(0,output-1),output])):cases.append(('decompress',data,length))
  for length in range(0,1028,4):cases.append(('zero',b'',length))
  cases.extend([('official_decompress',b'',0x195c),('official_zero',b'',0x340b4)])
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];official_output=None
  for index,(kind,data,length) in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x3e000);u.mem_write(0x20004000,data);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    is_zero=kind in ['zero','official_zero'];source=0xc4610 if kind=='official_decompress' else 0xc4d08 if kind=='official_zero' else 0x20004000;destination=0x200064a8 if kind=='official_decompress' else 0x20007e04 if kind=='official_zero' else 0x20002000
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[source,destination,length]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st={'source':candidate,'writes':[]};states[id(u)]=st;initial=bytearray(u.mem_read(0x20000000,0x3e000))
    entry=syms['r1_native_scatter_zero' if is_zero else 'r1_native_scatter_decompress'] if candidate else 0x3bc68 if is_zero else 0x286f4
    try:u.emu_start(entry|1,0x20000100,count=1000000)
    except Exception as error:raise RuntimeError((index,kind,data.hex(),length,candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(index,kind,length,candidate)
    for address,size,value in st['writes']:initial[address-0x20000000:address-0x20000000+size]=value.to_bytes(size,'little')
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,(index,'store reconciliation')
    results.append([u.reg_read(UC_ARM_REG_R0),st['writes'],hashlib.sha256(actual).hexdigest()])
    if kind=='official_decompress' and candidate:official_output=bytes(u.mem_read(destination,length))
   if results[0]!=results[1]:
    failure=dict(index=index,kind=kind,data=data.hex(),length=length,results=results,source_sha256=sha(ROOT/'r1/components/runtime/native_scatter_data.c'));(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[kind]+=1;digest.update(json.dumps([kind,data.hex(),length,results[0]],sort_keys=True).encode())
  assert official_output is not None and len(official_output)==6492;(OUT/'observed-initialized-data.bin').write_bytes(official_output)
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),return_stack_callee_integer_full_ram_and_nonstack_write_order_checked=True,executed_store_observer_with_full_ram_reconciliation=True,unicorn_memory_write_hooks_disabled=True,candidate_native_code_execution_forbidden=True,all_token_bytes=True,extended_literal_and_run_boundaries=True,overlapping_backreference_and_distance_zero=True,zero_output_size_still_processes_token=True,word_zero_lengths_multiple_of_four=True,official_compressed_bytes=1784,official_initialized_bytes=6492,official_zero_bytes=213172,observed_initialized_data_sha256=sha(OUT/'observed-initialized-data.bin'),compressed_initialization_data_is_authenticated_fixture=True,initialized_data_source_ownership=False,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Malformed zero extended literal counts, unaligned/non-multiple word clearing, wraparound/invalid memory and physical bus behavior remain open.','Authenticated compressed data and observed initialized RAM are verification inputs/evidence, not source-owned initialization or executable-image completion.','Scatter dispatcher/continuation, complete raw scratch/APSR/private frame, configuration ownership and original instruction/image identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
