import subprocess,json
from pathlib import Path
jobs=[]
results=[]
for j in jobs:
 r=subprocess.run(j,capture_output=True,text=True);results.append(dict(command=j,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(j[2],r.returncode,flush=True)
Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-delay-native-integrated/delay-nor-results.json').write_text(json.dumps(results,indent=2)+"\n")
assert all(r["returncode"]==0 for r in results)
