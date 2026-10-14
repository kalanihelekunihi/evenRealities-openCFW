from pathlib import Path
import json,collections,struct
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent;P=B/'case-wave060-ram-reaching-definitions/check.py';source=P.read_text().split('# Negative controls')[0]
# Instrument frozen evaluator without changing its transfer functions or results.
source=source.replace('active=set();cache={};proof=[]','active=set();cache={};proof=[];diagnostics=[]\n def unknown(reason,pc,r):\n  diagnostics.append(dict(reason=reason,PC=hex(pc),register=r,opcode=hex(ins[pc][0]) if pc in ins else None));return {UNKNOWN}')
source=source.replace('if key in active:return {UNKNOWN}',"if key in active:return unknown('BACKWARD_LOOP_CYCLE',pc,r)")
source=source.replace('if not pred.get(pc):out.add(UNKNOWN)',"if not pred.get(pc):out|=unknown('ENTRY_REGISTER_UNDEFINED',pc,r)")
source=source.replace('if len(out)>32:out={UNKNOWN}',"if len(out)>32:out=unknown('VALUE_SET_LIMIT',pc,r)")
source=source.replace("if w&0xff87==0x4780:return {UNKNOWN} if r in [0,1,2,3,12,14] else values(pc,r)","if w&0xff87==0x4780:return unknown('CALLER_SAVED_BLX_CLOBBER',pc,r) if r in [0,1,2,3,12,14] else values(pc,r)")
source=source.replace("if w&0xf800==0xf000 and tail&0xd000==0xd000:return {UNKNOWN} if r in [0,1,2,3,12,14] else values(pc,r)","if w&0xf800==0xf000 and tail&0xd000==0xd000:return unknown('CALLER_SAVED_BL_CLOBBER',pc,r) if r in [0,1,2,3,12,14] else values(pc,r)")
source=source.replace("if w==0xf3ef and r==(tail>>8)&15:return {UNKNOWN}","if w==0xf3ef and r==(tail>>8)&15:return unknown('PROCESSOR_REGISTER_VALUE',pc,r)")
source=source.replace("else:out.add(int.from_bytes", "else:out.add(int.from_bytes")
source=source.replace("if a is None or not 0x8000000<=a<=0x8000000+len(raw)-size:out.add(UNKNOWN)","if a is None or not 0x8000000<=a<=0x8000000+len(raw)-size:out|=unknown('NON_ROM_MEMORY_LOAD_OR_UNKNOWN_ADDRESS',pc,r)")
source=source.replace("if w&0xf800==0x9800:return {UNKNOWN} if r==(w>>8)&7 else values(pc,r)","if w&0xf800==0x9800:return unknown('SP_RELATIVE_LOAD_UNMODELED',pc,r) if r==(w>>8)&7 else values(pc,r)")
source=source.replace("if w&0xfe00==0xbc00:return {UNKNOWN} if r<8 and w&(1<<r) else values(pc,r)","if w&0xfe00==0xbc00:return unknown('POP_RESTORE_UNMODELED',pc,r) if r<8 and w&(1<<r) else values(pc,r)")
source=source.replace("if w&0xf000==0x5000:return {UNKNOWN} if (w>>9)&7>=3 and r==rd else values(pc,r)","if w&0xf000==0x5000:return unknown('REGISTER_OFFSET_LOAD_UNMODELED',pc,r) if (w>>9)&7>=3 and r==rd else values(pc,r)")
# Remaining conservative unknown leaves, without broadening evaluator support.
source=source.replace('return {UNKNOWN}',"return unknown('UNSUPPORTED_TRANSFER',pc,r)")
source=source.replace("return op(pc,rd,('reg',src),funcs[code]) if code in funcs else {UNKNOWN}","return op(pc,rd,('reg',src),funcs[code]) if code in funcs else unknown('UNSUPPORTED_ALU',pc,r)")
# Undo instrumentation's own recursive replacement.
source=source.replace("if pc in ins else None));return unknown('UNSUPPORTED_TRANSFER',pc,r)","if pc in ins else None));return {UNKNOWN}")
source=source.replace('return result,sorted(set(proof))','return result,sorted(set(proof)),diagnostics')
ns={'__file__':str(P)};exec(source,ns)
old=json.loads((B/'case-wave060-ram-reaching-definitions/verification.json').read_text());original={(row['target'],x['PC'],x['expected_base']):x for row in old['joins'] for x in row['examples']};rows=[]
for rec in ns['review']['RAM_operand_review']:
 for hit in rec['examples']:
  prior=original[(rec['target'],hit['PC'],hit['required_base_value'])]
  if prior['all_syntactic_predecessors_constant']:continue
  pc=int(hit['PC'],16);fn=ns['cat'][int(hit['function_entry'],16)];reg=int(hit['decoded_operand']['base_register'][1:]);values,proof,events=ns['analyze'](fn,pc,reg);assert values=={None if v is None else int(v,16) for v in prior['inferred_values']}
  unique={(x['reason'],x['PC'],x['register']):x for x in events};rows.append(dict(target=rec['target'],operand_PC=hit['PC'],function_entry=hit['function_entry'],base_register=reg,inferred_values=prior['inferred_values'],reason_categories=sorted(set(x['reason'] for x in events)),definition_failures=list(unique.values())))
counts=collections.Counter(reason for row in rows for reason in row['reason_categories']);leaves=collections.Counter((e['reason'],e['opcode']) for row in rows for e in row['definition_failures']);assert len(rows)==106
r=dict(status='PASS_106_UNRESOLVED_SAMPLES_EXACT_BASELINE_PRESERVATION',unresolved_target_site_samples=106,unique_operand_PCs=len(set(x['operand_PC'] for x in rows)),reason_sample_counts=dict(counts),failure_opcode_counts=[dict(reason=a,opcode=b,count=c) for (a,b),c in leaves.most_common()],samples=rows,limits=['Reason counts overlap because one backward slice may have multiple conservative leaves','Instrumented wave060 transfer semantics/results unchanged;106samples include70uniqueoperandPCs','Reasons identify analysis limitations, not firmware defects or actual dynamic behavior'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['reason_sample_counts']);print(r['failure_opcode_counts'][:12])
