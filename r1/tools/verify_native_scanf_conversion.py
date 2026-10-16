#!/usr/bin/env python3
"""Compare source scanf conversions with native callback and memory contracts."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scanf-conversion';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'integer':('r1_native_scanf_integer',0x278d0,332),'string':('r1_native_scanf_string',0x27a1c,224),'getc':('r1_native_scanf_input_getc',0x28038,30),'ungetc':('r1_native_scanf_input_ungetc',0x28056,34)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_scanf_conversion.o';assert sha(obj)==r['units'][0]['object_sha256']
 bp=BASE/'native-scanf-conversion-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-scanf-conversion-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
 for report in [r,bundle]:
  for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_scanf_conversion_verification.ld';states={};counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();callback_count=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);fixture=ROOT/'r1/tools/fixtures/scanf_whitespace_fixture.c';fo=d/'fixture.o';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-c',str(fixture),'-o',str(fo)],check=True);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(bo),str(fo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
  original={0x28038:('getc','r1_native_scanf_input_getc'),0x28056:('ungetc','r1_native_scanf_input_ungetc'),0x27ff4:('digit','r1_native_scanf_digit')};compiled={syms[s]:(k,s) for k,s in original.values()}
  # Memory-write hooks in Unicorn 2.1.4 corrupt IT state for conditional stores.
  # Decode the executed store instructions instead; reconcile their effects
  # with independent full-arena readback for each call.
  analysis=ROOT/'r1/research/source-build/i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
  decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if match:decoded[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)}
  registers.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  def observe_store(u,address,st):
   mnemonic,operands=decoded.get(address,('',''))
   if not mnemonic.startswith('str'):return
   regs,mem=operands.split('[',1);names=[x.strip() for x in regs.rstrip(', ').split(',')];address_terms=mem.split(']',1)[0].split(',');base=address_terms[0].strip()
   if base=='sp':return
   destination=u.reg_read(registers[base])
   if len(address_terms)>1:
    term=address_terms[1].strip();destination+=(int(term[1:],0) if term.startswith('#') else u.reg_read(registers[term]))
   destination&=0xffffffff
   if not 0x20000000<=destination<0x2003e000:return
   width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
   for i,name in enumerate(names):
    value=u.reg_read(registers[name])&((1<<(width*8))-1);st['writes'].append([destination+i*width,width,value])
  def hook(u,address,size,_):
   st=states[id(u)]
   observe_store(u,address,st)
   if address==syms['r1_scanf_whitespace_fixture']:
    ch=u.reg_read(UC_ARM_REG_R0);result=int(ch in [9,10,11,12,13,32]);st['callbacks'].append(['space',ch,result]);return
   if address in original and st['source']:u.reg_write(UC_ARM_REG_PC,syms[original[address][1]]|1);return
   selected=compiled.get(address) if st['source'] else original.get(address)
   if selected:
    kind,_=selected;st['callbacks'].append([kind,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if kind=='digit' else None])
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  cases=[]
  for kind,ch,remaining,eof,offset in itertools.product(['getc','ungetc'],range(256),[0,1,2,0xffffffff],[0,1],[0,1,7]):cases.append((kind,bytes([ch]),remaining,0,eof,offset,0))
  inputs=[b'',b' ',b'\t\n42!',b'0',b'00',b'0x',b'0x1a!',b'0XFF',b'-0x10!',b'+',b'-',b'12345',b'-2147483649',b'4294967296',b'99999999999999999999999999',b'0779',b'8',b'xyz',b'  -12x',bytes([128,255,65])]
  flags=[0,1,8,0x40,0x41,0x48,0x800,0x840,0x600,0xe49]
  for data,width,radix,flag in itertools.product(inputs,[0,1,2,3,8,32,0xffffffff],[0,2,8,10,16,36,0xffffffff],flags):cases.append(('integer',data,width,radix,flag,0,0))
  for data,width,flag,set_mode,char_mode in itertools.product(inputs+[b'ab cd',b'abcdef',b'aaabbbccc'],[0,1,2,8,32,0xffffffff],[0,1],range(4),[0,1,2]):cases.append(('string',data,width,set_mode,flag,0,char_mode))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,data,width,radix,flags,offset,char_mode in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20001000,b'\x96'*8192);u.mem_write(0x20002000,data+b'\0');current=0x20002000+offset
    remaining=width if kind in ['getc','ungetc'] else 0xffffffff
    u.mem_write(0x20001000,struct.pack('<IIII',current,remaining,0x20002000,flags if kind in ['getc','ungetc'] else 0));u.mem_write(0x20001200,struct.pack('<I',0x20001300))
    u.mem_write(0x20001100,struct.pack('<9I',0x20001200,flags,width,0,0,0,0x28039,0x28057,syms['r1_scanf_whitespace_fixture']|1))
    mask=[0xffffffff]*8 if radix==1 else [0]*8
    if radix in [2,3]:
     for ch in (range(48,58) if radix==2 else range(97,123)):mask[ch//32]|=1<<(ch%32)
    u.mem_write(0x20001400,struct.pack('<8I',*mask));states[id(u)]={'source':candidate,'writes':[],'callbacks':[]};initial_arena=bytearray(u.mem_read(0x20001000,8192))
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.mem_write(0x2003f000,struct.pack('<I',char_mode))
    if kind=='integer':args=[0xfffffffe,0x20001000,radix,0x20001100]
    elif kind=='string':args=[0xfffffffe,0x20001000,0x20001100,0x20001400 if radix else 0]
    else:args=[0x20001000,0x12345678,0x87654321,0xabcdef01]
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    # Enter compiled helper directly to avoid double-counting redirected entry.
    entry=syms[TARGETS[kind][0]] if candidate else TARGETS[kind][1]
    try:u.emu_start(entry|1,0x20000100,count=100000)
    except Exception as error:raise RuntimeError((kind,data.hex(),width,radix,flags,offset,char_mode,candidate,hex(u.reg_read(UC_ARM_REG_PC)),states[id(u)])) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(kind,data,width,radix,flags,candidate)
    st=states[id(u)]
    for address,size,value in st['writes']:
     assert 0x20001000<=address and address+size<=0x20003000
     offset_in_arena=address-0x20001000;initial_arena[offset_in_arena:offset_in_arena+size]=value.to_bytes(size,'little')
    assert initial_arena==bytes(u.mem_read(0x20001000,8192)),(kind,'executed-store reconciliation')
    results.append([u.reg_read(UC_ARM_REG_R0),st['writes'],st['callbacks'],bytes(u.mem_read(0x20001000,8192)).hex()])
   if results[0]!=results[1]:
    failure=dict(kind=kind,data=data.hex(),width=width,radix=radix,flags=flags,offset=offset,character_mode=char_mode,results=results,source_sha256=sha(ROOT/'r1/components/runtime/native_scanf_conversion.c'),driver_sha256=sha(Path(__file__)));(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[kind]+=1;callback_count+=len(results[0][2]);digest.update(json.dumps([kind,data.hex(),width,radix,flags,offset,char_mode,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_comparisons=callback_count,trace_sha256=digest.hexdigest(),return_stack_callee_integer_full_arena_and_nonstack_write_order_checked=True,callback_transcripts_checked=True,executed_store_observer_with_full_arena_reconciliation=True,analysis_elf_sha256=sha(analysis),unicorn_memory_write_hooks_disabled=True,whitespace_callback_fixture=True,whitespace_fixture_source=str(fixture.relative_to(ROOT)),whitespace_fixture_sha256=sha(fixture),source_input_callbacks_and_digit=True,signed_unsigned_byte_short_word_and_suppression=True,integer_radix_and_prefix_boundaries=True,string_character_and_scanset_modes=True,all_input_byte_values=True,runtime_no_unresolved=True,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Whitespace callback is a named ASCII fixture; full native ctype raw-index contract and arbitrary callback mutations remain separate.','Bounded seeded descriptors do not prove complete caller scratch/APSR/private frames, aliasing/invalid-memory/full-domain or physical hardware behavior.','Full scanf frontend/core, startup, instruction placement and byte-identical firmware integration remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
