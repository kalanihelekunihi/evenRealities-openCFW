from pathlib import Path
import json,subprocess
n=Path(__file__).resolve().parent
rows=[]
for row in json.loads((n/"broad-first-failures.json").read_text()):
 r=subprocess.run(row["command"],capture_output=True,text=True);rows.append(dict(command=row["command"],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(r.returncode,r.stdout[-200:],r.stderr[-500:],flush=True)
(n/"broad-pin-repairs.json").write_text(json.dumps(rows,indent=2))
