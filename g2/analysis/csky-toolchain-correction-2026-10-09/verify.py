from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=R/'g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/csky-target-contracts';pins=json.loads((D/'provenance.json').read_text());verified=[]
for p in pins:
 if 'path' in p and 'sha256' in p:assert sha(R/p['path'])==p['sha256'];verified.append(p)
op=(D/'binutils-gdb/opcodes/csky-opc.h').read_text();gas=(D/'binutils-gdb/gas/config/tc-csky.c').read_text();gcc=(D/'gcc/gcc/config/csky/csky.h').read_text()
assert '0xe8200000' in op and '0xf8008440' in op;assert '#define CSKY_ISA_804   (CSKY_ISA_803 | CSKY_ISA_803R3)' in gas;assert '#define STACK_BOUNDARY\t32' in gcc
packet=R/'g2/analysis/csky-descriptor-initializer-2026-10-09';record=json.loads((packet/'results.json').read_text());image=R/record['direct_inputs'][0]['path'];assert sha(image)==record['direct_inputs'][0]['sha256'];b=image.read_bytes();base=record['conditional_runtime_base'];rows=[]
for addr,expected,name in [(0x1020590a,0xfae0844d,'mula.32.l'),(0x1020592a,0xe832ffef,'bnezad')]:
 raw=b[addr-base:addr-base+4];word=(int.from_bytes(raw[:2],'little')<<16)|int.from_bytes(raw[2:],'little');assert word==expected
 if name=='mula.32.l':
  operands={'destination':word&31,'source1':(word>>16)&31,'source2':(word>>21)&31};assert operands=={'destination':13,'source1':0,'source2':23};assert word==0xf8008440|13|(23<<21)
 else:
  displacement=word&0xffff;displacement=displacement-0x10000 if displacement&0x8000 else displacement;operands={'register':(word>>16)&31,'signed_halfword_displacement':displacement,'target':hex(addr+2*displacement)};assert operands=={'register':18,'signed_halfword_displacement':-17,'target':'0x10205908'};assert word==0xe8200000|(18<<16)|(displacement&0xffff)
 rows.append({'address':hex(addr),'bytes':raw.hex(),'instruction_word':hex(word),'name':name,'operands_from_official_fields':operands})
result={'source_provenance_sha256':sha(D/'provenance.json'),'verified_pins':verified,'original_instruction_fields':rows,'vendor_compiler_stack_boundary_bits':32,'old_published_ABI_eight_byte_statement_superseded_as_unconditional_compiler_requirement':True,'CK804_assembler_feature_eligibility':True,'physical_target_identified':False,'instruction_execution_semantics_tested':False,'campaign_admitted':False,'limits':'Static encoding and vendor source/feature/ABI contract only; no physical CPU/revision, producing compiler or architecture execution proven. Old sealed packets unmodified.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('C-SKY source-field checks PASS',len(rows),'vendor stack boundary',32)
