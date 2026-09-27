#!/usr/bin/env python3
"""Fail-closed checks for the G2 pseudocode-first campaign records."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]

def sha(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def load(p): return json.loads(pathlib.Path(p).read_text())
def fail(msg): raise ValueError(msg)
def verify_identity(campaign: pathlib.Path) -> None:
    target=load(ROOT/'g2/workflow/target.json')
    rec=load(campaign/'identity.json')
    if rec.get('target_id') != target['target_id']: fail('target_id mismatch')
    if rec.get('target_lock_sha256') != sha(ROOT/'g2/workflow/target.json'): fail('target lock hash mismatch')
    b=rec['bundle']; bp=ROOT/b['path']
    if not bp.is_file() or bp.stat().st_size != target['bundle']['size'] or sha(bp) != target['bundle']['sha256']: fail('bundle identity mismatch')
    if b['sha256'] != target['bundle']['sha256']: fail('bundle receipt hash mismatch')
    seen=set()
    for c in target['components']:
        if c['id'] in seen: fail('duplicate component id')
        seen.add(c['id'])
        r=rec['components'].get(c['id'])
        p=ROOT/c['local_payload_path']
        if r is None or r.get('sha256') != c['sha256'] or not p.is_file() or p.stat().st_size != c['size'] or sha(p) != c['sha256']:
            fail(f"component identity mismatch: {c['id']}")
    if len(seen)!=6: fail('expected six components')
    parser=rec.get('container_validation',{})
    if parser.get('status')!='passed' or not parser.get('receipt_sha256'): fail('container validation receipt absent')
    cp=campaign/'inventory'/'outer-container.json'
    if not cp.is_file() or sha(cp)!=parser['receipt_sha256']: fail('container receipt hash mismatch')

def verify_task(path: pathlib.Path) -> None:
    t=load(path)
    required=['schema_version','campaign_id','task_id','phase','objective','worker_profile','target_sha256','target_lock_sha256','required_gate_receipts','component','input_files','required_evidence_excerpts','read_roots','write_allowlist','allowed_commands','required_artifacts','acceptance_checks','stop_conditions','attempt_output_root','result_path']
    missing=[k for k in required if k not in t or t[k] is None]
    if missing: fail('unfilled task fields: '+', '.join(missing))
    if t['worker_profile']!={'model':'gpt-6-luna','reasoning_effort':'low'}: fail('worker profile mismatch')
    if t['phase']=='P1_INVENTORY' and t.get('required_gate_receipts') not in ([],): fail('P1 cannot require future gate')
    if not t['write_allowlist'] or not t['attempt_output_root']: fail('missing private write scope')
    out=pathlib.PurePosixPath(t['attempt_output_root'])
    if not str(out).startswith(f"g2/build/pseudocode-first/{t['campaign_id']}/attempts/"): fail('attempt path outside campaign')
    for ent in t['input_files']:
        p=ROOT/ent['path']
        if not p.is_file() or sha(p)!=ent['sha256']: fail('stale input: '+ent['path'])

def partition(intervals, total, label):
    if not isinstance(total,int) or total < 0: fail(f'{label}: invalid total')
    cursor=0
    for row in intervals:
        start=row.get('start', (row.get('payload_offsets') or [None,None])[0])
        end=row.get('end', (row.get('payload_offsets') or [None,None])[1])
        if start != cursor or not isinstance(end,int) or end <= cursor:
            fail(f'{label}: gap, overlap, or empty interval at {cursor}')
        kind=row.get('kind',row.get('classification'))
        if kind=='code_or_data_unknown': kind='unknown'
        if kind not in {'code','data','container','padding','unknown'}:
            fail(f'{label}: unsupported classification')
        if not row.get('evidence',row.get('evidence_or_note')): fail(f'{label}: missing evidence')
        cursor=end
    if cursor != total: fail(f'{label}: closes at {cursor}, expected {total}')

def verify_inventory(campaign: pathlib.Path) -> None:
    verify_identity(campaign)
    target=load(ROOT/'g2/workflow/target.json')
    outer=load(campaign/'inventory'/'outer-container.json')
    if outer.get('campaign_id') != campaign.name or outer.get('artifact_sha256') != target['bundle']['sha256']:
        fail('outer inventory identity mismatch')
    if outer.get('unaccounted_bytes') != 0 or not outer.get('entry_spans'):
        fail('outer inventory not conserved')
    package_intervals=[{'start':0,'end':64,'kind':'container','evidence':'EVENOTA fixed header'},
                       {'start':64,'end':160,'kind':'container','evidence':'six-entry table of contents'},
                       {'start':160,'end':176,'kind':'container','evidence':'fixed trailer'}]
    for e in outer['entry_spans']:
        package_intervals.append({'start':e['package_offset'][0],'end':e['package_offset'][1],
                                  'kind':'container','evidence':'validated entry header and authenticated payload '+e['payload_id']})
    partition(package_intervals,target['bundle']['size'],'outer package')
    secondary=load(campaign/'inventory'/'secondary-payloads.json')
    tasks={p.name for p in (campaign/'attempts').iterdir() if p.is_dir()}
    for component in target['components']:
        cid=component['id']; size=component['size']
        if cid=='apollo_main':
            p=campaign/'attempts/P1-apollo_main-inventory-001/coverage.json'
            c=load(p); intervals=c.get('intervals',[])
            partition(intervals,size,cid)
            continue
        if cid=='codec':
            p=campaign/'attempts/P1-codec-inventory-002/coverage.json'
            c=load(p); intervals=c.get('intervals',[])
            partition(intervals,size,cid)
            continue
        if cid in secondary['components']:
            c=secondary['components'][cid]['coverage']; partition(c['intervals'],size,cid)
            continue
        fail(f'missing payload coverage: {cid}')
    plan=load(campaign/'inventory'/'analysis-plan.json')
    if plan.get('campaign_id') != campaign.name or plan.get('target_sha256') != target['bundle']['sha256']:
        fail('analysis plan identity mismatch')
    if {x.get('component') for x in plan.get('images',[])} != {x['id'] for x in target['components']}:
        fail('analysis plan does not include all six components')
    for image in plan['images']:
        if image.get('decoder_support') not in {'verified','planned_with_local_decoder'}:
            fail('missing architecture-specific decoder plan: '+str(image.get('component')))
        for src in image.get('evidence',[]):
            p=ROOT/src['path']
            if not p.is_file() or sha(p)!=src['sha256']: fail('analysis plan evidence hash mismatch: '+src['path'])

    reuse=load(campaign/'inventory'/'reuse-audit.json')
    if reuse.get('campaign_id') != campaign.name or reuse.get('target_sha256') != target['bundle']['sha256']:
        fail('historical evidence audit identity mismatch')
    if {x.get('component') for x in reuse.get('components',[])} != {x['id'] for x in target['components']}:
        fail('historical evidence audit must explicitly cover all six components')
    for component in reuse['components']:
        for src in component.get('evidence',[]):
            expected=src.get('sha256','')
            if expected.startswith(('DOC-','MISSING')): continue
            p=ROOT/src['path']
            if not p.is_file() or sha(p)!=expected: fail('reuse-audit input hash mismatch: '+src['path'])
    audits=load(campaign/'inventory'/'component-audits.json')
    if audits.get('campaign_id') != campaign.name or audits.get('case',{}).get('identity',{}).get('sha256') != next(x['sha256'] for x in target['components'] if x['id']=='case'):
        fail('component audit target identity mismatch')

    # Reject promotion of the contradicted Apollo transfer literal. It is retained as a blocker.
    block=load(campaign/'inventory'/'blockers.json')
    if not block.get('blockers') or block.get('status')!='blocked_pending_resolution':
        fail('P1 blocker registry missing or incorrectly cleared')
    expected={'path':'g2/tools/analyze_g2_codec_fwpk_segments.py','sha256':'1dd334eef9d8062ef6192c4c545ca7cde6304622e9df94035d10448ef8780159'}
    if expected not in block['evidence_inputs']: fail('codec blocker source pin missing')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['identity','task','inventory']); ap.add_argument('path'); a=ap.parse_args()
    try:
        if a.command=='identity': verify_identity(pathlib.Path(a.path))
        elif a.command=='task': verify_task(pathlib.Path(a.path))
        else: verify_inventory(pathlib.Path(a.path))
    except Exception as e:
        print(f'FAIL: {e}',file=sys.stderr); return 1
    print('PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
