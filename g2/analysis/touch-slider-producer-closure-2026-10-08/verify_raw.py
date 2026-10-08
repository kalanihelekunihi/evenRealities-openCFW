from pathlib import Path
import sys,json,struct,itertools
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('patterns=')[0],ns);coverage=set()
def run(native,raws,negative,automatic,method,ready,coefficient,widget_type=2,id=1):
 u=ns['guest']();ns['prepare'](u,[0]*4,0,2,100,10,2,0x800102);u.mem_write(0x20002000,struct.pack('<5I',0x20003000,0,0,0x20003f70,0x20004fc4));common=bytearray(64);struct.pack_into('<H',common,14,1);common[40]=automatic;u.mem_write(0x20003000,bytes(common));u.mem_write(0x20004000+116,struct.pack('<H',0x6000));u.mem_write(0x20004000+58,b'\x04');u.mem_write(0x20004000+122,bytes([method,widget_type]));u.mem_write(0x20005000+35,bytes([ready]));u.mem_write(0x20005000+4,struct.pack('<HH',3000,2500));u.mem_write(0x20005000+12,struct.pack('<H',2));u.mem_write(0x20005000+26,struct.pack('<HH',20,30));u.mem_write(0x20005000+34,bytes([coefficient]))
 for i,raw in enumerate(raws):u.mem_write(0x20006000+i*10,struct.pack('<HHHBBBB',raw,1900,0,4,negative,8,9))
 if not native:
  def code(u,a,n,user):
   if 0x4ba8<=a<0x4c04 or 0x4fee<=a<0x5054 or 0x5920<=a<0x5a0a or 0x5bc0<=a<0x5c02:coverage.update(range(a,a+n))
  u.hook_add(ns['UC_HOOK_CODE'],code)
 result=ns['call'](u,ns['symbols']['touch_slider_widget'] if native else 0x4ba8,[id,0x20002000]);return {'return':result,**ns['snap'](u)}
patterns=[[0,0,0,0],[1600,1900,1910,2050],[1890,1900,1930,2010],[1900,2009,2010,2011],[65535,3001,3000,2500]];out=[]
for raws,negative,automatic,method,ready,coefficient in itertools.product(patterns,[0,1,2,255],[0,1],[0,1],[0,6],[0,128,255]):
 args=(raws,negative,automatic,method,ready,coefficient);a=run(False,*args);b=run(True,*args);assert a==b,(args,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});out.append({'inputs':args,'result':a})
for typ,id in [(7,1),(2,3),(2,0xffffffff)]:
 args=([2050]*4,0,0,1,6,128,typ,id);a=run(False,*args);b=run(True,*args);assert a==b;out.append({'inputs':args,'result':a})
(D/'raw-results.json').write_text(json.dumps({'status':'PASS_SELECTED_FULL_CPU_SLIDER_RAW_TO_POSITION','cases':len(out),'coverage':sorted(coverage),'comparisons':out,'elf_sha256':ns['hashlib'].sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Acquiredrawcounts are synthetic inputs; HW-IIR/commonmode/ADC external.','Actual slider CPUrawfilterbitsdisabled(flags6000),onefrequency,coherentpointers; proximitywidgettype6 outside scope.','DefinedX/count/status/baseline/fraction/debounce compared; localnonXstackfields excluded.']},indent=2)+'\n');print('PASS',len(out),'raw-to-position cases')
