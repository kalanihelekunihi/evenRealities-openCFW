from pathlib import Path
import sys,struct,json,itertools
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split("counts={'filters'")[0],ns)
n=0
for raw,negative,automatic,coefficient in itertools.product([0,1600,1900,2000,2300,65535],[0,29,30,255],[0,1],[1,128,255]):
 outputs=[]
 for native in [False,True]:
  u=ns['fixture']();u.mem_write(0x20002000,struct.pack('<5I',0x20003000,0,0,0x20004000,0x20005000));common=bytearray(64);common[40]=automatic;u.mem_write(0x20003000,bytes(common));u.mem_write(0x20004000+28,struct.pack('<II',0x20007000,0x20007100));u.mem_write(0x20005000+12,struct.pack('<H',30));u.mem_write(0x20005000+26,struct.pack('<HH',100,200));u.mem_write(0x20005000+34,bytes([coefficient]));u.mem_write(0x20006000,struct.pack('<HHHBBBB',raw,1900,0,4,negative,8,9));u.mem_write(0x20007000,struct.pack('<6H',1700,1900,1800,1600,1700,1800));u.mem_write(0x20007100,b'\x45')
  ret=ns['ns']['call'](u,ns['ns']['symbols']['touch_proximity_raw'] if native else 0x5938,[0,0x20002000]);ns['ns']['call'](u,ns['ns']['symbols']['touch_proximity_process'] if native else 0x5a0a,[0x20004000]);outputs.append((ret,bytes(u.mem_read(0x20005000,60)),bytes(u.mem_read(0x20006000,10)),bytes(u.mem_read(0x20007000,12)),bytes(u.mem_read(0x20007100,1)),bytes(u.mem_read(0x20006100,2))))
 assert outputs[0]==outputs[1],(raw,negative,automatic,coefficient,outputs);n+=1
(D/'raw-results.json').write_text(json.dumps({'status':'PASS','cases':n,'scope':'Original5938 baseline/difference/filter chain followed by original5a0a versus independent C; synthetic inputs; no report/ADC/max-calibration claim'},indent=2)+'\n');print('PASS',n)
