from pathlib import Path
import sys,json,struct,itertools,hashlib,random
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns)
rows=[];rng=random.Random(0x5378)
cases=[(flags, inactive, seed) for flags in itertools.product([0,1,2,255],repeat=3) for inactive in [0,1,2,4,5,255] for seed in [0,1]]
for name,pc in [('touch_generate_modes',0x52bc),('touch_generate_pin_functions',0x50e4),('touch_generate_base',0x5378)]:
 for flags,inactive,seed in cases:
  internal=bytearray(rng.randbytes(128));common=rng.randbytes(64);internal[90:93]=bytes(flags);internal[116]=inactive;internal[117]=5 if seed else 0
  if seed==0:
   for off in [48,50,60,62,64,66,68]:struct.pack_into('<H',internal,off,0)
   internal[81]=0
  frame=rng.randbytes(256);vals=[]
  for native in [False,True]:
   u=ns['guest']();u.mem_write(0x20002000,struct.pack('<10I',0x20003000,0,0x20003500,0,0,0,0,0,0,0x20004000));u.mem_write(0x20003000,common);u.mem_write(0x20003500,bytes(internal));u.mem_write(0x20004000,frame)
   ns['call'](u,ns['symbols'][name] if native else pc,[0x20002000]);vals.append((u.mem_read(0x20003500,128).hex(),u.mem_read(0x20004000,256).hex()))
  assert vals[0]==vals[1],(name,flags,inactive,seed,vals)
  rows.append({'function':name,'dither_flags':flags,'inactive_csd':inactive,'zero_fields':seed==0})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Original complete functions vs independent C; no call stubs.','Synthetic coherent ARM32 descriptors; pointer aliases excluded.','Comparisons cover full destination frame and internal context; not stack scratch or write chronology.','Configuration registers only; no analog/timing validation.']},indent=2)+'\n');print('PASS',len(rows))
