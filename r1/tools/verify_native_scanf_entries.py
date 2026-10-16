#!/usr/bin/env python3
"""Whole source scanf calls versus native variadic frontend and conversion graph."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scanf-core';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={0x27898:('sscanf','r1_native_sscanf'),0x2801c:('descriptor','r1_native_scanf_descriptor_init'),0x283c4:('core','r1_native_scanf_core'),0x28010:('format','r1_native_scanf_format_getc'),0x28038:('get','r1_native_scanf_input_getc'),0x28056:('unget','r1_native_scanf_input_ungetc'),0x275f4:('space','r1_native_isspace'),0x27ff4:('digit','r1_native_scanf_digit'),0x278d0:('integer','r1_native_scanf_integer'),0x27a1c:('string','r1_native_scanf_string')}
def main():
 vp=OUT/'entry-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_scanf_core.o';assert sha(obj)==r['units'][0]['object_sha256']
 bp=BASE/'native-sscanf-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-sscanf-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
 for report in [r,bundle]:
  for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_sscanf_verification.ld';states={};digest=hashlib.sha256();counts=dict.fromkeys(['core','descriptor'],0);entries={side:dict.fromkeys([k for k,_ in TARGETS.values()],0) for side in ['native','compiled']};callback_count=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(bo),'-o',str(elf)],check=True)
  for section,target in [('.text',binary),('.r1.ctype.window',d/'ctype.bin'),('.r1.scanf.width_limit',d/'limit.bin')]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(target)],check=True)
  assert (d/'ctype.bin').read_bytes()==app.read_bytes()[0xbda90-0x27000:0xbdb91-0x27000] and (d/'limit.bin').read_bytes()==app.read_bytes()[0x286f0-0x27000:0x286f4-0x27000]
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};compiled={syms[s]:(k,s) for k,s in TARGETS.values()};machines=[]
  analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if match:decoded[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  def observe_store(u,address,st):
   mnemonic,operands=decoded.get(address,('',''))
   if not mnemonic.startswith('str'):return
   regs,mem=operands.split('[',1);names=[x.strip() for x in regs.rstrip(', ').split(',')];terms=mem.split(']',1)[0].split(',');base=terms[0].strip()
   if base=='sp':return
   destination=u.reg_read(registers[base])
   if len(terms)>1:
    term=terms[1].strip();offset=int(term[1:],0) if term.startswith('#') else u.reg_read(registers[term])
    if len(terms)>2:offset<<=int(terms[2].strip().split('#')[1],0)
    destination+=offset
   destination&=0xffffffff
   if not 0x20000000<=destination<0x2003e000:return
   width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
   for i,name in enumerate(names):st['writes'].append([destination+i*width,width,u.reg_read(registers[name])&((1<<(width*8))-1)])
  def hook(u,address,size,_):
   st=states[id(u)];assert not st['source'] or not 0x27000<=address<0xc4d08,('candidate executed native code',hex(address))
   observe_store(u,address,st);selected=compiled.get(address) if st['source'] else TARGETS.get(address)
   if not selected:return
   kind,_=selected;st['entries'][kind]+=1;r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
   if kind=='format':st['callbacks'].append([kind,r1])
   elif kind in ['get','unget']:st['callbacks'].append([kind])
   elif kind=='space':st['callbacks'].append([kind,r0])
   elif kind=='digit':st['callbacks'].append([kind,r0,r1])
   elif kind=='integer':
    descriptor=u.reg_read(UC_ARM_REG_R3);st['callbacks'].append([kind,u.reg_read(UC_ARM_REG_R2),bytes(u.mem_read(descriptor+4,8)).hex()])
   elif kind=='string':
    descriptor=u.reg_read(UC_ARM_REG_R2);selection=u.reg_read(UC_ARM_REG_R3);mode=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];st['callbacks'].append([kind,bytes(u.mem_read(descriptor+4,8)).hex(),bytes(u.mem_read(selection,32)).hex() if selection else None,mode])
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   if source:u.mem_write(0xbda90,(d/'ctype.bin').read_bytes());u.mem_write(0x286f0,(d/'limit.bin').read_bytes())
  inputs=[b'',b' ',b'\t\n42!',b'0',b'00',b'0x',b'0x1a!',b'0XFF',b'-0x10!',b'+',b'-',b'12345',b'-2147483649',b'4294967296',b'99999999999999999999999999',b'0779',b'8',b'xyz',b'  -12x',b'abc def',b'aaabbbccc',b'a-z',b']x',b'%',b'abc,42',bytes([128,255,65])]
  formats=[b'',b' ',b'abc',b'%%',b'%',b'%q',b'%[',b'%[]',b'%[^',b'%[a-z]',b'%[^a-z]',b'%[]]',b'%[^]]']
  formats += [b'%'+suppress+width+length+conversion for suppress,width,length,conversion in itertools.product([b'',b'*'],[b'',b'0',b'1',b'3',b'2147483647',b'2147483648',b'99999999999'],[b'',b'hh',b'h',b'l',b'll',b'j',b'z',b't',b'L'],[b'd',b'u',b'i',b'o',b'x',b'X',b'p',b'n',b'c',b's',b'f'])]
  direct_formats=[b'',b'%d%n',b'%s%n',b'%3c%lln',b'%[a-z]%n',b'%*i%x',b'%f',b'%lld',b'%%',b'%hhd %hd %u',b'%2147483648d']
  cases=[(entry,value,fmt) for entry,value,fmt in itertools.product(['core','descriptor'],inputs,direct_formats)]
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,(category,value,fmt) in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20001000,b'\x96'*8192);u.mem_write(0x20001000,value+b'\0');u.mem_write(0x20001400,fmt+b'\0');u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    output_pointers=[0x20002000+i*64 for i in range(16)];u.mem_write(0x2003f000,struct.pack('<14I',*output_pointers[2:]));descriptor=0x20001800;input_state=0x20001900;argument_table=0x20001a00
    callback_addresses=[0x28011,0x28039,0x28057,0x275f5]
    if candidate:callback_addresses=[syms[name]|1 for name in ['r1_native_scanf_format_getc','r1_native_scanf_input_getc','r1_native_scanf_input_ungetc','r1_native_isspace']]
    u.mem_write(argument_table,struct.pack('<16I',*output_pointers));u.mem_write(input_state,struct.pack('<4I',0x20001000,0xffffffff,0x20001000,0));u.mem_write(descriptor,struct.pack('<9I',argument_table,0x96969696,0x96969696,0x20001400,0,callback_addresses[0],callback_addresses[1],callback_addresses[2],callback_addresses[3]));states[id(u)]={'source':candidate,'writes':[],'callbacks':[],'entries':dict.fromkeys(entries['native'],0)};initial=bytearray(u.mem_read(0x20001000,8192))
    for reg,arg in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],([input_state,0x20001400,descriptor,0] if category=='descriptor' else [input_state,descriptor,0,0])):u.reg_write(reg,arg)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    entry=(syms['r1_native_scanf_descriptor_init' if category=='descriptor' else 'r1_native_scanf_core'] if candidate else 0x2801c if category=='descriptor' else 0x283c4)
    try:u.emu_start(entry|1,0x20000100,count=200000)
    except Exception as error:raise RuntimeError((index,category,value.hex(),fmt.hex(),candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(index,category,value,fmt,candidate)
    st=states[id(u)]
    for address,size,data in st['writes']:
     assert 0x20001000<=address and address+size<=0x20003000;offset=address-0x20001000;initial[offset:offset+size]=data.to_bytes(size,'little')
    actual=bytes(u.mem_read(0x20001000,8192));assert initial==actual,(index,'store reconciliation')
    relocations={syms[name]|1:address|1 for address,(_,name) in TARGETS.items()};canonical=bytearray(actual)
    for slot in [5,6,7,8]:
     offset=descriptor+slot*4-0x20001000;word=struct.unpack_from('<I',canonical,offset)[0];struct.pack_into('<I',canonical,offset,relocations.get(word,word))
    canonical_writes=[[a,n,relocations.get(v,v) if n==4 and a in [descriptor+20,descriptor+24,descriptor+28,descriptor+32] else v] for a,n,v in st['writes']]
    results.append([u.reg_read(UC_ARM_REG_R0),canonical_writes,st['callbacks'],canonical.hex()])
    for kind,n in st['entries'].items():entries['compiled' if candidate else 'native'][kind]+=n
   if results[0]!=results[1]:
    failure=dict(index=index,category=category,input=value.hex(),format=fmt.hex(),results=results,source_sha256=sha(ROOT/'r1/components/runtime/native_scanf_core.c'),driver_sha256=sha(Path(__file__)));(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[category]+=1;callback_count+=len(results[0][2]);digest.update(json.dumps([category,value.hex(),fmt.hex(),results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_comparisons=callback_count,entries=entries,internal_entry_counts_are_not_equivalence_claim=True,trace_sha256=digest.hexdigest(),return_stack_callee_integer_full_arena_and_nonstack_write_order_checked=True,normalized_callback_transcripts_checked=True,source_frontend_core_conversions_ctype_and_input=False,source_core_descriptor_conversions_ctype_and_input=True,callback_function_pointer_relocations_normalized=True,native_core_fixture=False,runtime_no_unresolved=True,candidate_native_code_execution_forbidden=True,variadic_register_and_stack_outputs=False,suppression_width_length_count_and_scanset_cases=True,native_float_and_long_long_nop_failures_preserved=True,executed_store_observer_with_full_arena_reconciliation=True,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Callback function pointer relocations are normalized after raw store reconciliation; original instruction/absolute provider addresses are not proven equal.','Source descriptor mode is zero; alternate native private-frame scanset modes, arbitrary callback mutations, malformed pointers and full domain remain open.','Complete caller scratch/APSR/private frame, source startup, physical hardware, shared data placement and original instruction/whole-image identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
