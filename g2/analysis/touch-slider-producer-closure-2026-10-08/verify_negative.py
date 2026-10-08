from pathlib import Path
import sys,subprocess,json
D=Path(__file__).resolve().parent;gcc=Path(sys.argv[1]);base=Path(sys.argv[2]);root=D.parents[1]/'components/touch/slider_producer_offline'
mutants={'threshold_inclusive':('slider.c','>threshold?1:0','>=threshold?1:0',([110,0,0,0],0,0,100,10,2,0)),'publish_during_debounce':('slider.c','else if(active)for','else if(0)for',([111,0,0,0],0,2,100,10,2,0)),'latest_centroid_tie':('centroid.c','if(sum>maxsum)','if(sum>=maxsum)',([111]*4,0,0,100,10,2,0)),'wrong_iir_weight':('centroid.c','prior*(256u-coefficient)','prior*(255u-coefficient)',([0,0,0,111],0,0,100,10,2,0x800102))};out=[]
for name,(file,a,b,inputs) in mutants.items():
 dest=base/name;dest.mkdir(parents=True,exist_ok=True);p=dest/file;p.write_text((root/file).read_text().replace(a,b));paths={f:root/f for f in ['slider.c','centroid.c','raw.c']};paths[file]=p;subprocess.run([sys.executable,str(D/'build.py'),str(gcc),str(dest),str(paths['slider.c']),str(paths['centroid.c']),str(paths['raw.c'])],check=True,stdout=subprocess.DEVNULL)
 sys.argv=[str(D/'verify.py'),str(dest/'slider.elf')];ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('patterns=')[0],ns);original=ns['run'](False,*inputs);mutant=ns['run'](True,*inputs);different=[k for k in original if original[k]!=mutant[k]];assert different,name;out.append({'mutant':name,'rejected':True,'inputs':inputs,'different_fields':different})
(D/'negative-results.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(out),'producer mutants rejected')
