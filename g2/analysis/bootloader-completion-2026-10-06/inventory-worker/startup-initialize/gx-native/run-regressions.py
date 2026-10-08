from pathlib import Path
import subprocess
root=Path.cwd();base=root/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native'
py='/Users/kalani/.local/share/opencfw/venv/bin/python';candidate='/tmp/opencfw-root-gx/candidate.elf'
for driver,output in [('verify_root_gx.py','root-comparison.json'),('verify_root_gx_initialized.py','root-initialized-ranks.json'),('verify_gx_children.py','children-comparison.json'),('verify_gx_event.py','event-comparison.json'),('verify_gx_transition_initialized.py','transition-initialized-ranks.json')]:
 subprocess.run([py,str(base/driver),'--elf',candidate,'--output',str(base/output)],check=True)
subprocess.run([py,str(base/'verify_scatter_table.py'),'--elf',candidate],check=True)
subprocess.run([py,'g2/components/bootloader/thread_creation/verify_code_alignment.py','--elf',candidate,'--output',str(base/'alignment.json')],check=True)
