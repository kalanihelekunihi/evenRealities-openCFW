from pathlib import Path
import subprocess,tempfile,json,argparse,hashlib
D=Path(__file__).resolve().parent;C=D.parents[1]/'components/touch/eeprom_init_offline';p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();source=(C/'init.c').read_text();results=[];before=hashlib.sha256((D/'results.json').read_bytes()).hexdigest()
start=source.index('uint32_t touch_init_ranges(');end=source.index('void touch_init_program_size',start)
mutants=[('wrong-configuration-error-status',source[:start]+source[start:end].replace('0x093e0002u','0x093e0000u')+source[end:]),('accept-unsupported-nonblocking',source.replace('if(!cfg[7])return 0x093e0000u;','')),('simple-mode-wear-not-coerced',source.replace('c[12]=c[13]?1:cfg[5];','c[12]=cfg[5];'))]
for name,text in mutants:
 with tempfile.TemporaryDirectory(prefix='opencfw-init-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),'--init-source',str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'build/provider.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr,(name,r.returncode,r.stderr);results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
assert hashlib.sha256((D/'results.json').read_bytes()).hexdigest()==before
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS3 initializer mutants rejected; positive receipt unchanged')
