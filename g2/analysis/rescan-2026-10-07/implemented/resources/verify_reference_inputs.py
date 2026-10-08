"""Authenticate recovered reference inputs before using their ABIs/resources."""
from pathlib import Path
import json,hashlib,argparse

def verify(root):
 manifest=root/'REFERENCE-SNAPSHOT-MANIFEST.json';data=json.loads(manifest.read_text());failures=[]
 for row in data['files']:
  p=root/row['path']
  if not p.is_file():failures.append({'path':row['path'],'error':'missing'});continue
  raw=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256'] or blob!=row['git_blob_sha1']:failures.append({'path':row['path'],'error':'identity mismatch'})
 return dict(status='FAIL' if failures else 'PASS',files=len(data['files']),source_commit=data['source_commit'],manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=failures,limits=['Reference identity only; no firmware compatibility, resource classification or source-closure claim.'])
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).with_name('reference-snapshots'));ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();r=verify(a.root);a.output.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['files']);raise SystemExit(r['status']!='PASS')
