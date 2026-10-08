from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[];coverage=set()')[0],ns)
selected=[['zero',1000,'erase-base-error',0],['zero',1000,'program-error',0],['valid',0,'success',0],['erased',1000,'load-error',0]];out=[]
for c in json.loads((D/'results.json').read_text())['comparisons']:
 if c['inputs'] not in selected:continue
 args=c['inputs'];raw=bytes.fromhex(c['result']['storage']);a,_=ns['boot'](False,args[0],args[1],'success',0,initial_storage=raw);b,_=ns['boot'](True,args[0],args[1],'success',0,initial_storage=raw);assert a==b
 out.append({'first_boot_inputs':args,'second_boot_fault_mode':'success','result':a})
(D/'reboot-results.json').write_text(json.dumps({'status':'PASS_SECOND_BOOT_ORIGINAL_NATIVE_NO_FUNCTION_CUTS','cases':len(out),'comparisons':out},indent=2)+'\n');print('PASS',len(out),'second boot cases')
