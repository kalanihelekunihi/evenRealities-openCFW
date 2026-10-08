from pathlib import Path
import sys,subprocess,json
D=Path(__file__).resolve().parent;gcc=Path(sys.argv[1]);base=Path(sys.argv[2]);source=D.parents[1]/'components/touch/calibration_offline/calibration.c'
mutants={'calibrate_at_49':('if(delta>49)','if(delta>=49)',(1000,1049,1049,1,1,1,'success')),'new_baseline_in_same_report':('*(uint16_t *)(report+10)=saved','*(uint16_t *)(report+10)=RECORD->baseline',(1000,1050,1049,1,1,1,'success')),'proximity_at_500':('if(measured>b+500u)','if(measured>=b+500u)',(1000,1500,1049,0,1,0,'success'))};out=[]
for name,(a,b,inputs) in mutants.items():
 dest=base/name;dest.mkdir(parents=True,exist_ok=True);p=dest/'calibration.c';p.write_text(source.read_text().replace(a,b));subprocess.run([sys.executable,str(D/'build.py'),'--gcc',str(gcc),'--output',str(dest),'--calibration-source',str(p)],check=True,stdout=subprocess.DEVNULL)
 sys.argv=[str(D/'verify.py'),str(dest/'provider.elf')];ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[]\nfor b,delta')[0],ns)
 original=ns['run_report'](False,*inputs);mutant=ns['run_report'](True,*inputs);different=[k for k in original if original[k]!=mutant[k]];assert different,name;out.append({'mutant':name,'rejected':True,'inputs':inputs,'different_fields':different})
(D/'negative-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(out),'mutants rejected')
