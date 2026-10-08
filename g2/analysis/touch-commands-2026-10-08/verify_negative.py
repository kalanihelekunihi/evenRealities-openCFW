from pathlib import Path
import argparse,subprocess,tempfile,json
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--gcc',required=True);a=p.parse_args();source=(D/'app_event.c').read_text();results=[]
mutants=[('threshold-big-endian',source.replace('RX[1]|((uint16_t)RX[2]<<8)','RX[2]|((uint16_t)RX[1]<<8)')),('omit-threshold-deferred-flag',source.replace('*(uint8_t *)0x200009ceu=1;','/* negative */')),('clear-baseline-tail',source.replace('uint16_t v=*(uint16_t *)0x200009d4u;', 'for(unsigned i=0;i<16;i++)TX[i]=0;uint16_t v=*(uint16_t *)0x200009d4u;'))]
for name,modified in mutants:
 with tempfile.TemporaryDirectory(prefix='opencfw-touch-command-negative-') as tmp:
  w=Path(tmp);s=w/'mutant.c';s.write_text(modified);subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'build.py'),'--gcc',a.gcc,'--output',str(w/'build'),'--callback-source',str(s)],check=True,capture_output=True)
  r=subprocess.run(['/Users/kalani/.local/share/opencfw/venv/bin/python',str(D/'verify_commands.py'),str(w/'build/app-event.elf')],capture_output=True,text=True);assert r.returncode!=0 and 'AssertionError' in r.stderr;results.append({'control':name,'rejected':True,'diagnostic_tail':r.stderr[-400:]})
(D/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS3 command mutants rejected')
