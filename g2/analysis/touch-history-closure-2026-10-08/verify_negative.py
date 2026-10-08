from pathlib import Path
import subprocess,tempfile,json,argparse,hashlib
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();history=(D/'history.c').read_text();providers=(D/'providers.c').read_text();results=[];before=hashlib.sha256((D/'helper-results.json').read_bytes()).hexdigest()
mutants=[('signed-sequence-selection','--history-source',history.replace('s>best','(int32_t)(s-best)>0')),('omit-history-crc','--history-source',history.replace('status=crc_check(source,size);','status=0;')),('ignore-redundant-integrity','--history-source',history.replace('row+region(c)','row')),('wrong-copy-success-status','--providers-source',providers.replace('data[i]=src[i];return 0;','data[i]=src[i];return 1;'))]
for name,option,text in mutants:
 with tempfile.TemporaryDirectory(prefix='opencfw-history-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),option,str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_helpers.py'),str(w/'build/provider.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
assert hashlib.sha256((D/'helper-results.json').read_bytes()).hexdigest()==before
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS4 history/provider mutants rejected; positive receipt unchanged')
