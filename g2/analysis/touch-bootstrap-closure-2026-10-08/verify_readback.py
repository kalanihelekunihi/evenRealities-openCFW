from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[];coverage=set()')[0],ns)
results=[]
for case in json.loads((D/'results.json').read_text())['comparisons']:
 if case['inputs'][0]=='invalid-initializer':continue
 outputs=[]
 for native in [False,True]:
  u=ns['guest'](native);u.mem_write(0xe400,bytes.fromhex(case['result']['storage']));ns['call'](u,ns['symbols']['touch_application_eeprom_init'] if native else 0x34d8,[])
  status=ns['call'](u,ns['symbols']['touch_application_read'] if native else 0x3520,[0,0x20006000,8]);outputs.append({'status':status,'record':u.mem_read(0x20006000,8).hex()})
 assert outputs[0]==outputs[1],case['inputs'];results.append({'inputs':case['inputs'],'readback':outputs[0]})
(D/'readback-results.json').write_text(json.dumps({'status':'PASS_FRESH_INITIALIZE_AND_READ_AFTER_BOOTSTRAP','cases':len(results),'comparisons':results},indent=2)+'\n');print('PASS',len(results),'fresh readback cases')
