from pathlib import Path
import json,subprocess
p=Path(__file__).resolve().parent;q=p/'focused-run-results.json';rows=json.loads(q.read_text())
for i,x in enumerate(rows):
 if x['returncode']:
  assert any('verify_selector17.py' in v for v in x['command'])
  r=subprocess.run(x['command'],capture_output=True,text=True);rows[i]=dict(command=x['command'],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);print(r.stdout,r.stderr);q.write_text(json.dumps(rows,indent=2)+'\n');assert r.returncode==0
