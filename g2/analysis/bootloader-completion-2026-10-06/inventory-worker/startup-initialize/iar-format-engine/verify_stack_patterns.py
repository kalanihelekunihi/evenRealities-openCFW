from pathlib import Path
import subprocess,json,shutil
N=Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/iar-format-engine');C=Path('g2/components/bootloader/initializer_callbacks/iar_format_native');rows=[]
for word in [0,0x30303030,0xffffffff,0xa5a5a5a5]:
 t=Path('/tmp/opencfw-iar-format-stack')/hex(word);r=subprocess.run(['python3',str(N/'verify_qemu.py'),'--source-dir',str(C),'--output',str(t),'--stack-word',hex(word)],capture_output=True,text=True,timeout=90);print(hex(word),r.returncode,r.stdout[:120],r.stderr[-700:],flush=True);rows.append(json.loads((t/'comparison.json').read_text()));assert r.returncode==0
(N/'current-evidence/stack-pattern-comparisons.json').write_text(json.dumps(rows,indent=2)+'\n')
