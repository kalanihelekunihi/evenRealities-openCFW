from pathlib import Path
import subprocess,json
N=Path(__file__).resolve().parent;results=[]
for suite in ['broad','focused','extra','closure']:
 r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(N/('run-'+suite+'.py'))],capture_output=True,text=True);rows=json.loads((N/(suite+'-run-results.json')).read_text());results.append(dict(suite=suite,jobs=len(rows),failed=sum(x['returncode']!=0 for x in rows),runner_exit=r.returncode));print(results[-1],flush=True)
 for x in rows:
  if x['returncode']:print(x['command'][2],x['stderr'][-1800:],flush=True)
(N/'other-regressions.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(x['failed']==0 and x['runner_exit']==0 for x in results)
