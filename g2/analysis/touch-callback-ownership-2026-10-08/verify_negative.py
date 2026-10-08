from pathlib import Path
import subprocess,tempfile,json,argparse
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);a=p.parse_args();text=(D/'app_event.c').read_text();results=[]
for name,modified in [('ignore-error-event',text.replace('!(events&0x40u)','1')),('omit-RX-rearm',text.replace('Cy_SCB_I2C_SlaveConfigWriteBuf(SCB1,RX,16,CTX);','/*deliberate negative: RX not rearmed*/'))]:
 with tempfile.TemporaryDirectory(prefix='opencfw-app-negative-') as work:
  w=Path(work);src=w/'mutant.c';src.write_text(modified)
  subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',str(a.gcc),'--output',str(w/'build'),'--callback-source',str(src)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_app_event.py'),str(w/'build/app-event.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append(dict(control=name,rejected=True,diagnostic_tail=r.stderr[-700:]))
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS2 registered-callback mutants rejected')
