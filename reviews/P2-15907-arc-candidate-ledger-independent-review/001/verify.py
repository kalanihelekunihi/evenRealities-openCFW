#!/usr/bin/env python3
"""Read-only verifier for private P2-15906 candidate ledger."""
import hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[7]
OUT=pathlib.Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def loadj(path): return json.loads(path.read_text())
def main():
    contract=loadj(OUT/'contract.json'); ledger=loadj(OUT/'candidate-ledger.json')
    pins=loadj(OUT/'input-pins.json')['pins']
    failures=[]
    for pin in pins:
        p=ROOT/pin['path']
        if not p.is_file() or sha(p)!=pin['sha256']: failures.append('pin mismatch: '+pin['path'])
    image=ROOT/ledger['locked_image']['content_path']; payload=ROOT/ledger['locked_payload']['path']
    ib=image.read_bytes(); pb=payload.read_bytes()
    if sha(image)!=ledger['locked_image']['content_sha256']: failures.append('locked image hash mismatch')
    if sha(payload)!=ledger['locked_payload']['sha256']: failures.append('locked payload hash mismatch')
    if pb[1060:211948]!=ib: failures.append('payload/image mapping mismatch')
    rec=ledger['locked_image']; m=rec['loaded_image_map']; start,end=rec['source_span_in_payload']
    if (m['image_start'],m['image_end'],end-start)!=(0,len(ib),len(ib)): failures.append('mapping extent mismatch')
    rows=[json.loads(s) for s in (OUT/'instruction-bindings.jsonl').read_text().splitlines() if s]
    if len(rows)!=557 or ledger['candidate_instruction_rows']!=len(rows): failures.append('instruction row count')
    owners={}; modes={};
    for r in rows:
        a,b=r['image_span']; pa,pbspan=r['official_payload_span']; ra,rb=r['runtime_span']
        raw=bytes.fromhex(r['mapped_locked_image_bytes_hex'])
        if len(raw)!=b-a or ib[a:b]!=raw: failures.append('image bytes mismatch '+r['candidate_id'])
        if pb[pa:pbspan]!=raw or pa!=start+a or pbspan-pa!=b-a: failures.append('payload bytes mismatch '+r['candidate_id'])
        if ra!=m['loaded_start']+a or rb!=m['loaded_start']+b: failures.append('runtime map mismatch '+r['candidate_id'])
        if hashlib.sha256(raw).hexdigest()!=r['mapped_instruction_sha256']: failures.append('instruction hash mismatch '+r['candidate_id'])
        if r['recorded_byte_interpretation']=='each_halfword_byte_swapped':
            candidate=bytes.fromhex(r['recorded_instruction_bytes_hex']); transformed=b''.join(candidate[i:i+2][::-1] for i in range(0,len(candidate),2))
        elif r['recorded_byte_interpretation']=='as_recorded': transformed=bytes.fromhex(r['recorded_instruction_bytes_hex'])
        else: failures.append('unknown byte interpretation'); continue
        if transformed!=raw: failures.append('candidate transform mismatch '+r['candidate_id'])
        for i in range(a,b): owners[i]=owners.get(i,0)+1
        modes[r['recorded_byte_interpretation']]=modes.get(r['recorded_byte_interpretation'],0)+1
    if len(rows)!=sum(1 for _ in rows): failures.append('unreachable')
    union=len(owners); multi=sum(1 for n in owners.values() if n>1); total=sum(len(bytes.fromhex(r['mapped_locked_image_bytes_hex'])) for r in rows)
    if (union,multi,total)!=(1698,34,1732): failures.append(f'overlap counts {(union,multi,total)}')
    candidates=ledger['candidates']
    if len(candidates)!=22: failures.append('candidate count')
    for c in candidates:
        for key in ('instruction_file','pseudocode_file'):
            p=ROOT/c[key]
            expect=c['instruction_file_sha256'] if key=='instruction_file' else c['pseudocode_sha256']
            if not p.is_file() or sha(p)!=expect: failures.append('candidate hash mismatch '+c['candidate_id']+'/'+key)
    if ledger['accepted'] is not False or ledger['status']!='partial' or contract['accepted'] is not False: failures.append('status was promoted')
    if failures:
        print('FAIL'); print('\n'.join(failures)); return 1
    print(json.dumps({'result':'PASS','candidate_count':len(candidates),'instruction_rows':len(rows),'instruction_bytes_sum':total,'unique_image_bytes':union,'multiply_owned_bytes':multi,'byte_interpretation_rows':modes,'input_pins':len(pins),'accepted':False},sort_keys=True))
    return 0
if __name__=='__main__': sys.exit(main())
