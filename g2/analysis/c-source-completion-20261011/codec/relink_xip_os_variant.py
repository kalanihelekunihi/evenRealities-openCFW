#!/usr/bin/env python3
"""Relink the selected Codec A objects with measured smaller -Os replacements."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--probe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 image=json.loads(a.receipt.read_text())['images']['codec'];probe=json.loads((a.probe/'receipt.json').read_text());assert probe['receipt_sha256']==hashlib.sha256(a.receipt.read_bytes()).hexdigest()
 oldbase=a.receipt.parent/'codec';replacements={r['O2_object']:r for r in probe['rows'] if r.get('delta_bytes',0)<0};link=image['relocatable_link']['argv'];objects=[Path(x).name for x in link if x.endswith('.o') and x.startswith('/out/')];assert objects
 for n in objects:shutil.copy2(a.probe/n if n in replacements else oldbase/n,a.output/n)
 cmd=[f'type=bind,src={a.output.resolve()},dst=/out' if x.startswith('type=bind,src=') and x.endswith(',dst=/out') else '/out/candidate-os-variant.o' if x=='/out/candidate.o' else x for x in link]
 done=subprocess.run(cmd,capture_output=True,text=True)
 result={'baseline_receipt_sha256':probe['receipt_sha256'],'probe_receipt_sha256':hashlib.sha256((a.probe/'receipt.json').read_bytes()).hexdigest(),'replaced_sources':sorted(r['source'] for r in replacements.values()),'replacement_count':len(replacements),'link_exit':done.returncode,'link_stderr':done.stderr[-3000:]}
 if done.returncode==0:result['candidate_sha256']=hashlib.sha256((a.output/'candidate-os-variant.o').read_bytes()).hexdigest()
 (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print({k:result[k] for k in ('replacement_count','link_exit','candidate_sha256') if k in result})
 if done.returncode:raise SystemExit(done.returncode)
if __name__=='__main__':main()
