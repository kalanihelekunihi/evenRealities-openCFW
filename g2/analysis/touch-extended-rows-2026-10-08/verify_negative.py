from pathlib import Path
import subprocess,tempfile,json,argparse
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();source=(D/'extended.c').read_text();results=[]
for name,text in [('skip-four-checksum-bytes',source.replace('row[1u+i]','row[4u+i]')),('pad-final-row-length',source.replace('i==rows-1u?size:capacity','capacity'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-extended-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),'--extended-source',str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify.py'),str(w/'build/provider.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 extended mutants rejected')
