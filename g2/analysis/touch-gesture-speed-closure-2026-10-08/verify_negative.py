from pathlib import Path
import sys,subprocess,json,struct
D=Path(__file__).resolve().parent;gcc=Path(sys.argv[1]);base=Path(sys.argv[2]);source=D.parents[1]/'components/touch/gesture_speed_offline/speed.c'
mutants={'retain_filter_on_reverse':('if(prior && direction && prior!=direction)s[74]=0;','',100,0,1000,100,1),'wrong_smoothing':('speed*4u+s[74]*6u','speed*3u+s[74]*7u',0,255,1,100,0),'store_zero_elapsed_fallback':('if(current==old)return s[74]?s[74]:1;','if(current==old){if(!s[74])s[74]=1;return s[74];}',100,100,0,0,0)};out=[]
for name,(a,b,oldposition,position,elapsed,filtered,direction) in mutants.items():
 dest=base/name;dest.mkdir(parents=True,exist_ok=True);p=dest/'speed.c';p.write_text(source.read_text().replace(a,b));subprocess.run([sys.executable,str(D/'build.py'),str(gcc),str(dest),str(p)],check=True,stdout=subprocess.DEVNULL)
 sys.argv=[str(D/'verify.py'),str(dest/'speed.elf')];ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('rng=random.Random')[0],ns);s=bytearray(80);s[72:76]=bytes([1,2,filtered,direction&255]);s[48]=oldposition;struct.pack_into('<I',s,52,100);original=ns['run'](False,s,position,100+elapsed,0);mutant=ns['run'](True,s,position,100+elapsed,0);assert original!=mutant,name;out.append({'mutant':name,'rejected':True,'original':original,'mutant_result':mutant})
(D/'negative-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(out),'speed mutants rejected')
