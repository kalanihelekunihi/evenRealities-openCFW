"""Run only synthetic QEMU M55 guest tests, capture architectural exception logs."""
from pathlib import Path
import json,subprocess,hashlib,re,datetime
HERE=Path(__file__).resolve().parent;rows=json.loads((HERE/'scenario-inputs.json').read_text());out=[]
for row in rows:
 elf=Path(row['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==row['elf_sha256']
 log=elf.with_name(row['tag']+'-int.log')
 args=['/opt/homebrew/bin/qemu-system-arm','-M','mps3-an547','-nographic','-monitor','none','-serial','none','-semihosting-config','enable=on,target=native','-kernel',str(elf),'-d','int','-D',str(log)]
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=15);result={'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except subprocess.TimeoutExpired as e:
  result={'exit_code':None,'timeout_seconds':15,'stdout':str(e.stdout),'stderr':str(e.stderr)}
 facts={k:int(v,16) for k,v in re.findall(r'(\w+)=(0x[0-9a-fA-F]+)',result['stderr'])}
 passed=result['exit_code']==0 and 'PASS actual-entry-return' in result['stderr']
 item={**row,'status':'PASS' if passed else 'FAIL','result':result,'facts':facts,'qemu_log':str(log),'qemu_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest() if log.exists() else None}
 out.append(item);print(row['tag'],item['status'],result['stderr'],flush=True)
 (HERE/'comparison.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if len(out)==len(rows) and all(x['status']=='PASS' for x in out) else 'PARTIAL_OR_FAILED','scenarios':out,'limits':['QEMU mps3-an547 core/NVIC/FP model with reconstructed source only; not Apollo510 peripherals, locked-original ELF execution, timing or hardware validation.','Synthetic coherent ready lists/tasks/stacks; actual SVC/IRQ/PendSV entry/return and allocator/scheduler/reclamation source execute. No timer or IRQ concurrency stress.']},indent=2)+'\n')
 if not passed:raise SystemExit(1)
