from pathlib import Path
import sys,subprocess,json,struct
D=Path(__file__).resolve().parent;gcc=Path(sys.argv[1]);base=Path(sys.argv[2]);source=D.parents[1]/'components/touch/gesture_machine_offline/gesture.c'
mutants={'motion_at_24':('if(magnitude(delta)>24)','if(magnitude(delta)>=24)',1,124,200,0),'rate_at_99':('counter-U32(s,40)>99','counter-U32(s,40)>=99',1,125,199,0),'tap_window_excludes_300':('counter-U32(s,36)<=300','counter-U32(s,36)<300',0,100,400,1),'hold_after_threshold':('elapsed>=*(uint16_t *)s','elapsed>*(uint16_t *)s',1,100,1100,0)};out=[]
for name,(a,b,previous,position,counter,pending) in mutants.items():
 dest=base/name;dest.mkdir(parents=True,exist_ok=True);p=dest/'gesture.c';p.write_text(source.read_text().replace(a,b));subprocess.run([sys.executable,str(D/'build.py'),str(gcc),str(dest),str(p)],check=True,stdout=subprocess.DEVNULL)
 sys.argv=[str(D/'verify.py'),str(dest/'gesture.elf')];ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('rng=random.Random')[0],ns);s=bytearray(80);struct.pack_into('<H',s,0,1000);s[12]=previous;s[13]=s[21]=s[44]=100;s[32]=1;s[33]=pending;s[72:77]=bytes([0,2,100,0,0]);
 for off in [16,24,36,40]:struct.pack_into('<I',s,off,100)
 original=ns['run'](False,s,1,position,counter,0);mutant=ns['run'](True,s,1,position,counter,0);assert original!=mutant,name;out.append({'mutant':name,'rejected':True,'original_event':bytes.fromhex(original['state'])[77:80].hex(),'mutant_event':bytes.fromhex(mutant['state'])[77:80].hex(),'original_state':original['state'],'mutant_state':mutant['state']})
(D/'negative-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(out),'machine mutants rejected')
