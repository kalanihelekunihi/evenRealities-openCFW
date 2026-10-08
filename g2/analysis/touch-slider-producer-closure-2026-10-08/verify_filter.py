from pathlib import Path
import sys,json,struct,itertools
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('patterns=')[0],ns);out=[]
for count,prior,config in itertools.product([0,1,2,255],[0,1,2,255],[0,0x000102,0x800102,0xff0102]):
 result=[]
 for native in [False,True]:
  u=ns['guest']();w=bytearray(144);struct.pack_into('<I',w,60,0x20006200);struct.pack_into('<I',w,112,config);u.mem_write(0x20004000,bytes(w));u.mem_write(0x20006200,struct.pack('<IB3x',0x20006400,prior));u.mem_write(0x20006400,struct.pack('<8H',20,30,40,50,60,70,80,90));u.mem_write(0x20006500,struct.pack('<IB3x',0x20006300,count));u.mem_write(0x20006300,struct.pack('<8H',200,150,100,50,250,200,150,100));ns['call'](u,ns['symbols']['touch_position_filters'] if native else 0x4a2a,[0x20006500,0x20004000]);result.append({'position':u.mem_read(0x20006300,16).hex(),'history':u.mem_read(0x20006400,16).hex(),'header':u.mem_read(0x20006200,8).hex()})
 assert result[0]==result[1],(count,prior,config,result);out.append({'inputs':[count,prior,config],'result':result[0]})
(D/'filter-results.json').write_text(json.dumps({'status':'PASS_DIRECT_POSITION_FILTER_DEFINED_FULL_RECORDS','cases':len(out),'comparisons':out,'limits':['DirectinitializedpositionX/Y/paddingallowfullrecordcomparison; distinctfromsliderlocalundefinednonXbytes.','Atmosttwoallocatedpositions; count255specialsentinel doesnotdereference.']},indent=2)+'\n');print('PASS',len(out),'direct filter cases')
