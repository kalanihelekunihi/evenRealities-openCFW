#!/usr/bin/env python3
"""Replay an existing bounded fixture; persist only observed original instruction PCs."""
from pathlib import Path
import hashlib,json,collections
import unicorn,capstone
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'execution-proof';OUT.mkdir(exist_ok=True)
source=ROOT/'g2/analysis/audio-angle-2026-10-01/verify.py';text=source.read_text();digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest=='67617256018cc0c8936bec05cf606145ab394ad523beca8f4e8cb91437d95f22'
ns={'__file__':str(source),'__name__':'bounded_replay'};trace={};calls=[]
# Instrument only the existing firmware hook after its stub branch; never count asin.
text=text.replace('OUT=Path(__file__).resolve().parent','OUT=TRACE_OUT')
text=text.replace(" assert any(x<=a<z for x,z in ranges),hex(a)"," assert any(x<=a<z for x,z in ranges),hex(a)\n record_original(u,a,n)")
text=text.replace(" sp=0x203ff000;", " replay_calls.append(dict(entry=a,args=list(args),stack=list(stack)));sp=0x203ff000;")
def record(u,a,n):
 b=bytes(u.mem_read(a,n));blob=ns['B'];off=a-ns['BASE'];assert blob[off:off+n]==b
 key=(a,b.hex());r=trace.setdefault(key,dict(runtime_pc=a,payload_range=[off,off+n],instruction_bytes=b.hex(),sha256=hashlib.sha256(b).hexdigest(),replay_call_indices=[]))
 idx=len(calls)-1
 if idx not in r['replay_call_indices']:r['replay_call_indices'].append(idx)
ns.update(TRACE_OUT=OUT,record_original=record,replay_calls=calls)
exec(compile(text,str(source),'exec'),ns)
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
rows=sorted(trace.values(),key=lambda r:r['runtime_pc'])
for r in rows:
 bb=bytes.fromhex(r['instruction_bytes']);decoded=list(md.disasm(bb,r['runtime_pc']));assert len(decoded)==1 and decoded[0].size==len(bb);r['mnemonic']=decoded[0].mnemonic;r['operands']=decoded[0].op_str
assert all(a['payload_range'][1]<=b['payload_range'][0] for a,b in zip(rows,rows[1:])), 'instruction overlap'
(OUT/'executed-instructions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
report=dict(firmware_sha256=ns['SHA'],source_fixture=str(source.relative_to(ROOT)),source_fixture_sha256=digest,replay_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),case_count=len(ns['CASES']),body_hash_checks=len(ns['records']),unique_instructions=len(rows),unique_instruction_bytes=sum(len(bytes.fromhex(r['instruction_bytes'])) for r in rows),replay_calls=calls,unicorn_version=unicorn.__version__,capstone_version=capstone.__version__,limits='Synthetic PCM and controlled CPU state; original Thumb/VFP executes; asin is a host math stub and its PCs/bytes excluded. Pre-execution code hooks admitted only after all cases terminate and assertions pass; no faults or hardware trace. Full function bodies/literal pools are never promoted.')
report['executed_trace_sha256']=hashlib.sha256((OUT/'executed-instructions.jsonl').read_bytes()).hexdigest()
(OUT/'trace-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
