from pathlib import Path
import subprocess,json
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());T=Path('/tmp/opencfw-logger-mutants');T.mkdir(exist_ok=True);flags=['--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=softfp','-O1','-ffreestanding','-fno-builtin','-I',str(R/'g2/components/bootloader/filesystem/freestanding_include')];rows=[];paths=[Path('/tmp/opencfw-log-adapters.elf'),Path('/tmp/opencfw-dfu-task-logger.elf')];saved={p:p.read_bytes() for p in paths}
try:
 for name,source,old,new,target,verifier in [('blob-mask','log_adapters.c','0x00ffffffu','0xffffffffu',paths[0],'verify_adapters.py'),('short-read-detail','task_with_log_detail.c','0x214u,got','0x214u,0',paths[1],'verify_task_logger.py')]:
  text=(R/'g2/components/bootloader/log_call_adapters'/source).read_text();assert old in text;p=T/source;p.write_text(text.replace(old,new));
  if source=='task_with_log_detail.c':p.write_text(p.read_text().replace('#include "../dfu_task/task.h"','#include "'+str(R/'g2/components/bootloader/dfu_task/task.h')+'"').replace('#include "../update_core/update_core.h"','#include "'+str(R/'g2/components/bootloader/update_core/update_core.h')+'"'))
  o=T/(name+'.o');subprocess.run(['clang',*flags,'-c',str(p),'-o',str(o)],check=True)
  inputs=[str(o)] if target==paths[0] else ['/tmp/opencfw-log-adapters.o',str(o),'/tmp/opencfw-logger-memory.o'];ld=N/('module.ld' if target==paths[0] else 'task_module.ld');subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),*inputs,'-o',str(target)],check=True,capture_output=True)
  cmd=['/Users/kalani/.local/share/opencfw/venv/bin/python',str(N/verifier)];
  if target==paths[1]:cmd+=['--elf',str(target),'--output',str(N/'mutant-should-not-pass.json')]
  r=subprocess.run(cmd,capture_output=True,text=True);(N/(name+'-rejected.txt')).write_text(r.stdout+r.stderr);assert r.returncode!=0;rows.append(dict(control=name,rejected=True,returncode=r.returncode))
finally:
 for p,b in saved.items():p.write_bytes(b)
(N/'negative-controls.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
