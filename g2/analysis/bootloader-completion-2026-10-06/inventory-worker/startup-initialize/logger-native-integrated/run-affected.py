from pathlib import Path
import subprocess,json
n=Path(__file__).resolve().parent;c=json.loads((n/'current-candidate.json').read_text());root=next(p for p in n.parents if (p/'AGENTS.md').exists());elf=root/c['directory']/'candidate.elf';rows=[]
for name in ['verify_remaining_native.py','verify_selector13_native.py','verify_selector9_native.py','verify_selector10_native.py','verify_selector23.py','verify_selector22.py','verify_deferred21.py','verify_deferred21_sequential.py','verify_hot_transitions.py','verify_selector5_integrated.py','verify_selector20_integrated.py','verify_updater_frontier.py','verify_temperature_default.py']:
 cmd=['/Users/kalani/.local/share/opencfw/venv/bin/python',str(n/'run_oracle.py'),str(n/name)]
 if name in ['verify_updater_frontier.py','verify_temperature_default.py']:cmd+=['--elf',str(elf),'--output',str(n/(name.removeprefix('verify_').removesuffix('.py')+'-comparison.json'))]
 r=subprocess.run(cmd,capture_output=True,text=True);rows.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));(n/'affected-run-results.json').write_text(json.dumps(rows,indent=2));print(name,r.returncode,r.stdout[-200:],r.stderr[-500:],flush=True)
