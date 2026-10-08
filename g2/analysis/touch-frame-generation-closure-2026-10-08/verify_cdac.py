from pathlib import Path
import sys,json,struct,itertools,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);n=0
for method,flag,divider,sensor,pattern,common in itertools.product([0,1,2,10],[0,1,2],[0,1,4096,65535],[0,2,3,7],[0,1,255],[0,0x1000,0x4000]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_write(0x20002000+4,struct.pack('<4I',0x20003200,0x20003500,0x20004000,0x20005000));u.mem_write(0x20003200+8,struct.pack('<I',common));u.mem_write(0x20003500+90,bytes([flag]*3));u.mem_write(0x20004000,struct.pack('<II',0x20005000,0x20006500));u.mem_write(0x20004000+58,b'\x03');u.mem_write(0x20004000+122,bytes([method]));u.mem_write(0x20005000+46,bytes([pattern,255-pattern,pattern,255-pattern,0,pattern]));u.mem_write(0x20005000+54,struct.pack('<H',divider));u.mem_write(0x20006500,b''.join(bytes(9)+bytes([(pattern+j)&255]) for j in range(8)));u.mem_write(0x20006000,struct.pack('<HH',0,sensor));u.mem_write(0x20007000,struct.pack('<6I',0,0,0,0x55555555,0xa5a5a5a5,0));r=ns['call'](u,ns['symbols']['touch_generate_cdac'] if native else 0x51bc,[0x20006000,0x20007000,0x20002000]);vals.append((r,u.mem_read(0x20007000,24).hex()))
 assert vals[0]==vals[1],(method,flag,divider,sensor,pattern,common,vals);n+=1
(D/'cdac-results.json').write_text(json.dumps({'status':'PASS','cases':n,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'scope':'Full original51bc versus independent CDAC source; no function-call stubs; synthetic configuration/sensors only'},indent=2)+'\n');print('PASS',n)
