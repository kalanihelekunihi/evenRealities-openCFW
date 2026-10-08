from pathlib import Path
import tempfile,subprocess,json
D=Path(__file__).resolve().parent;source=(D/'write_dispatch.c').read_text();results=[]
for name,text in [('invert-mode',source.replace('return c[13] ?', 'return !c[13] ?')),('reject-raw-overflow',source.replace('if(address+size>', 'if((uint64_t)address+size>'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-eeprom-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--source',str(s),'--output',str(w/'build')],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'build/write_dispatch.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 EEPROM dispatcher mutants rejected')
