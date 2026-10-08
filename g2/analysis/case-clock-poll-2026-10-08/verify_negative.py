from pathlib import Path
import subprocess,tempfile,json
D=Path(__file__).resolve().parent;source=(D/'voltage_scaling.c').read_text();results=[]
for name,modified in [('omit-final-retry',source.replace('1000000u)+1u','1000000u)')),('wrong-regulator-busy-bit',source.replace('pwr[5]&0x400u','pwr[5]&0x200u'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-case-voltage-negative-') as tmp:
  w=Path(tmp);(w/'mutant.c').write_text(modified);subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Oz','-ffreestanding','-fno-builtin','-c',str(w/'mutant.c'),'-o',str(w/'mutant.o')],check=True);subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000','-e','case_voltage_scaling',str(w/'mutant.o'),'-o',str(w/'test.elf')],check=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'test.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-400:]})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 voltage scaling mutants rejected')
