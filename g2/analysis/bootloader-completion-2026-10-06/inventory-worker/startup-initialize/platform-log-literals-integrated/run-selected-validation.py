from pathlib import Path
import json,subprocess
N=Path(__file__).resolve().parent
rows=[]
for suite in ['integration','affected']:
 r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(N/('run-'+suite+'.py'))],capture_output=True,text=True);x=json.loads((N/(suite+'-run-results.json')).read_text());bad=[r for r in x if r['returncode']];rows.append({'suite':suite,'jobs':len(x),'failed':len(bad),'runner_exit':r.returncode});print(rows[-1],flush=True)
 for r in bad:print(r['command'],r['stderr'][-1500:],flush=True)
(N/'selected-validation.json').write_text(json.dumps(rows,indent=2)+'\n');assert not any(r['failed'] or r['runner_exit'] for r in rows)
