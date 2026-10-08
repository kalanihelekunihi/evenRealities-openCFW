from pathlib import Path
import subprocess,tempfile,json,argparse,hashlib
D=Path(__file__).resolve().parent;C=D.parents[1]/'components/touch/eeprom_offline';p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();source=(C/'read.c').read_text();results=[];before=hashlib.sha256((D/'results.json').read_bytes()).hexdigest()
mutants=[('skip-header-overlay',source.replace('for(uint32_t i=0;i<rows;i++){','for(uint32_t i=0;i<0;i++){')),('accept-bad-historic-crc',source.replace('uint32_t status=check(row,c);','uint32_t status=0;'))]
for name,text in mutants:
 with tempfile.TemporaryDirectory(prefix='opencfw-read-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),'--read-source',str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'build/provider.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr,(name,r.returncode,r.stderr);results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
assert hashlib.sha256((D/'results.json').read_bytes()).hexdigest()==before
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 read mutants rejected; positive receipt unchanged')
