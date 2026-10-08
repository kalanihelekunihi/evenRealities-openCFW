from pathlib import Path
import sys,json,itertools,hashlib
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;cal=D.parent/'touch-calibration-closure-2026-10-08';speed=Path(sys.argv[2]);sys.argv=[str(cal/'verify.py'),sys.argv[1]];ns={'__file__':str(cal/'verify.py')};exec((cal/'verify.py').read_text().split('cases=[]\nfor b,delta')[0],ns);oldguest=ns['guest'];sections=[]
with speed.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s.name in ['.native_speed','.native_support']]
def guest(native):
 u=oldguest(native)
 if native:
  for a,b in sections:u.mem_write(a,b)
 return u
ns['guest']=guest;out=[]
for b,delta,active,prior,flag,mode in itertools.product([0,1000,65000],[-50,-49,0,49,50,500,501],[0,1],[1,2],[0,1],['success','program-error']):
 measured=max(0,min(65535,b+delta));args=(b,measured,max(0,min(65535,b+49)),active,prior,flag,mode);a=ns['run_report'](False,*args);z=ns['run_report'](True,*args);assert a==z,(args,{k:(a[k],z[k]) for k in a if a[k]!=z[k]});out.append({'inputs':args,'result':a})
(D/'composed-results.json').write_text(json.dumps({'status':'PASS_COMPOSED_REPORT_WITH_NATIVE_SPEED','cases':len(out),'calibration_elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'speed_fixture_elf_sha256':hashlib.sha256(speed.read_bytes()).hexdigest(),'comparisons':out,'limits':['Original gesture4070 retained; selected native speed section occupies old helper address and support110000; original helper is replaced only in offline guest.','No entry hooks returning stub values; synthetic SROM and sensor structures remain.','Selective sections loaded, not ELFsegmentpadding or production firmware.']},indent=2)+'\n');print('PASS',len(out),'composed reports with native speed')
