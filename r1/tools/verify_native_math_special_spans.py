#!/usr/bin/env python3
"""Authenticate relocation-free compiled instruction spans, not image placement."""
import hashlib,json
from pathlib import Path
from audit_source_frontier import section_bytes
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-math-special';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';obj=OUT/'native_math_special.o';report=json.loads((OUT/'report.json').read_text());assert sha(obj)==report['units'][0]['object_sha256'];spans=[]
    for name,a in [('r1_math_self_add32',0x3bac8),('r1_math_add32',0x3bace)]:
        section='.text.'+name;data=section_bytes(obj,section);assert len(data)==6 and data==app.read_bytes()[a-0x27000:a-0x27000+6]==bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])
        spans.append(dict(entry=f'0x{a:08x}',bytes=6,object='native-math-special/native_math_special.o',section=section,sha256=hashlib.sha256(data).hexdigest(),relocations=False,image_placement_proven=False))
    r=dict(compiled_instruction_byte_spans=spans,report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),instruction_identity=False,image_integration_proven=False,limitations=['These6-byte compiled sections match native bytes without relocations; final original placement and whole-image identity remain unproven.','Shared leaf entries are not complete parent-function source or full firmware coverage.'])
    (OUT/'instruction-span-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Two relocation-free6-byte instruction spans match; image placement remains gated')
if __name__=='__main__':main()
