from pathlib import Path
import subprocess,json,tempfile
D=Path(__file__).resolve().parent; text=(D/'case_wake.c').read_text(); results=[]
for name,modified in [('drop-pin6',text.replace('0x3fu','0x1fu')),('wrong-polarity-shift',text.replace('arg >> 8','arg >> 7'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-case-mutant-') as work:
  w=Path(work); (w/'mutant.c').write_text(modified)
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Oz','-ffreestanding','-fno-builtin','-c',str(w/'mutant.c'),'-o',str(w/'mutant.o')],check=True)
  subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_wake_enable',str(w/'mutant.o'),'-o',str(w/'mutant.elf')],check=True)
  p=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_case_wake.py'),str(w/'mutant.elf')],capture_output=True,text=True)
  assert p.returncode!=0 and 'AssertionError' in p.stderr
  results.append(dict(mutant=name,rejected=True,diagnostic=p.stderr.splitlines()[-1]))
(D/'case-negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS',len(results),'semantic mutants rejected')
