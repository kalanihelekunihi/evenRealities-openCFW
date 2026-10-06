#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
REPO=Path('/Users/kalani/Repo/evenRealities-openCFW')
CAMPAIGN=REPO/'g2/build/pseudocode-first/20260930T190500Z'
OUT=CAMPAIGN/'analysis/csky-manifest-binding-investigation-15974/001'
A=CAMPAIGN/'analysis/csky-recovery-4056/002';OLD=CAMPAIGN/'analysis/csky-recovery-4056/001'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,msg):
    if not ok: raise SystemExit('FAIL: '+msg)
old=json.loads((A/'receipt.json').read_text()); new=json.loads((OUT/'superseding-receipt.json').read_text())
m=A/'artifact-manifest.json'
check(old['accepted'] is False and new['accepted'] is False,'accepted stays false')
check(sha(A/'receipt.json')==new['supersedes_receipt_sha256'],'old receipt pin')
check(old['artifact_manifest_sha256']==sha(m)==new['artifact_manifest_sha256'],'expected hash and superseding binding')
check(new['artifact_manifest']==str(m.relative_to(REPO)),'corrected path')
check(sha(REPO/old['artifact_manifest'])!=old['artifact_manifest_sha256'],'historical 001 path mismatch preserved')
manifest=json.loads(m.read_text());check(manifest['task_id']==old['task_id'] and manifest['task_sha256']==old['task_sha256'],'task binding')
for e in manifest['files']:
    f=A/e['path'];check(f.is_file() and f.stat().st_size==e['bytes'] and sha(f)==e['sha256'],'manifest file '+e['path'])
for name,digest in [('instructions.json','27fd7af74f8ab8e841b9f688d8268ee90525e648c6f7cf990b8812044d4e6b26'),('pseudocode.md','d47bdcaf8fa17b567deabd0b2abfbc4de173ee3bea52b1304707a9a2caaa69bb')]:check(sha(A/name)==digest,'critical input '+name)
check(any(e['path']=='instructions.json' and e['sha256']==sha(A/'instructions.json') for e in manifest['files']),'instruction manifest binding')
check(any(e['path']=='pseudocode.md' and e['sha256']==sha(A/'pseudocode.md') for e in manifest['files']),'pseudocode manifest binding')
q=subprocess.run([sys.executable,str(A/'verify-correction.py')],cwd=REPO,text=True,capture_output=True)
check(q.returncode==0,'existing correction verifier: '+q.stdout+q.stderr)
print('PASS_SCOPED: exact attempt-002 manifest recovered; all listed files, task, instruction, and pseudocode pins verify; superseding receipt accepted:false; old evidence untouched.')
