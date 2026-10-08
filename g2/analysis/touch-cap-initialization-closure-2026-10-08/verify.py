from pathlib import Path
import sys,json,struct,itertools,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'touch-mode-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for old,desired,busy')[0],ns);g=ns['g'];rows=[]
for old,lock,hw,maximums,flags in itertools.product([0,1,2,3,4,5,6,7,8,255],[0,1,2,255],[0,0x40000000],[[0]*6,[0,1,1,0,65535,65535],[65535]*6],[0,1,255]):
 vals=[]
 for native in [False,True]:
  u=ns['fixture']();u.mem_write(0x20003100,struct.pack('<I',hw));u.mem_write(0x20003700,bytes([lock]));u.mem_write(0x20003500,b'\xa5'*128);u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20004000,struct.pack('<I',0x20005000))
  for j in range(3):u.mem_write(0x20005000+j*60+4,struct.pack('<HH',*maximums[j*2:j*2+2]));u.mem_write(0x20005000+j*60+35,bytes([flags]))
  r=g['call'](u,g['symbols']['touch_cap_init'] if native else 0x4c7c,[0x20002000]);vals.append((r,u.mem_read(0x20003500,128).hex(),u.mem_read(0x20005000,180).hex(),u.mem_read(0x20003700,1).hex()))
 assert vals[0]==vals[1],(old,lock,hw,maximums,flags,vals);rows.append({'initial_mode':old,'initial_lock':lock,'hw':hw,'maximums':maximums,'initial_flags':flags,'return':vals[0][0],'final_lock':vals[0][3],'internal':vals[0][1]})
for native in [False,True]:u=ns['fixture']();assert g['call'](u,g['symbols']['touch_cap_init'] if native else 0x4c7c,[0])==1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows)+2,'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Full original initialization/capture/mode instructions versus independent source and pinned public PDL capture; no function stubs.','Synthetic configurations and lock states; no IRQ concurrency or hardware acquisition.']},indent=2)+'\n');print('PASS',len(rows)+2)
