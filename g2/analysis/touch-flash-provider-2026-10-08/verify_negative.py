from pathlib import Path
import subprocess,tempfile,json,argparse
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();flash=(D/'flash.c').read_text();providers=(D/'providers.c').read_text();results=[]
for name,option,text,verify in [('wrong-restore-error-priority','--flash-source',flash.replace('if(written)status=written','if(!status)status=written'),'verify_flash.py'),('propagate-error-unlike-stock','--providers-source',providers.replace('(void)touch_flash_write_row(a,data);','return touch_flash_write_row(a,data);'),'verify_adapters.py')]:
 with tempfile.TemporaryDirectory(prefix='opencfw-provider-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(text);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),option,str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/verify),str(w/'build/provider.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-500:]})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 flash/provider mutants rejected')
