from pathlib import Path
import tempfile,subprocess,json
D=Path(__file__).resolve().parent;t=(D/'stop_mode.c').read_text();results=[]
for name,modified in [('wrong-deep-sleep-bit',t.replace('SCR=SCR | 4u','SCR=SCR & ~4u')),('wrong-stop-selection',t.replace('? 1u : 0u','? 2u : 0u'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-stop-negative-') as work:
  w=Path(work);(w/'mutant.c').write_text(modified)
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Oz','-ffreestanding','-fno-builtin','-c',str(w/'mutant.c'),'-o',str(w/'mutant.o')],check=True)
  subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_stop_mode',str(w/'mutant.o'),'-o',str(w/'test.elf')],check=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'test.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append(dict(control=name,rejected=True,diagnostic_tail=r.stderr[-500:]))
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 STOP mutants rejected')
