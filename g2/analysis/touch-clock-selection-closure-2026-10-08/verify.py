from pathlib import Path
import sys,json,struct,hashlib,random,itertools
from unicorn.arm_const import UC_ARM_REG_R3
D=Path(__file__).resolve().parent;s=D.parent/'touch-all-slot-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('for typ,csd,csx')[0],ns);g=ns['ns'];rng=random.Random(0x6384);rows=[]
def invoke(u,pc,args):
 if len(args)>3:u.reg_write(UC_ARM_REG_R3,args[3])
 if len(args)>4:u.mem_write(0x20008000,struct.pack('<I',args[4]))
 return g['call'](u,pc,args)
for name,pc,argslist in [
 ('touch_poly_period',0x6220,[[x] for x in [0,1,2,3,255,256,32767,32768,65535,65536,0xffffffff]]),
 ('touch_dither_value',0x6262,[list(x) for x in itertools.product([0,1,2,3,4,127,128,255],[0,1,3,30,31,32,255,256])]),
 ('touch_dither_limit',0x6270,[[rng.choice([0,1,7,8,16,4096,65535,0xffffffff]),rng.choice([0,4,8]),rng.choice([0,1,20,100,255,0xffffffff]),rng.choice([0,1,3,31,32,255])] for _ in range(200)]),
 ('touch_ssc_run',0x61f0,[list(x) for x in itertools.product([0,1,2,255],[0,2,16],[0,2,15],[1,3,255],[0,1,3,255,65535])])]:
 for args in argslist:
  vals=[]
  for native in [False,True]:u=g['guest']();vals.append(invoke(u,g['symbols'][name] if native else pc,args))
  assert vals[0]==vals[1],(name,args,vals);rows.append({'function':name,'args':args,'return':vals[0]})
for n in range(720):
 specs=[]
 for j in range(3):specs.append((rng.choice([1,2,10,255]),rng.choice([0,1,2,4,5,8,10,255]),rng.choice([0,1,3,128,129,131,255]),rng.choice([0,1,7,8,9,16,4096,4097,65535]),rng.choice([0,1,255,65535]),rng.choice([0,20,100,255]),rng.choice([0,1,2,255])))
 scale=rng.choice([0,1,3,31,32,255]);poly=rng.choice([0,1,3,255,256,0xffff]);fine=rng.choice([0,1,255]);vals=[]
 for native in [False,True]:
  u=ns['fixture']();u.mem_write(0x20003500+60,struct.pack('<H',poly));u.mem_write(0x20003500+77,bytes([fine,scale]))
  for j,(method,src,bits,div,conv,percent,sel) in enumerate(specs):
   u.mem_write(0x20004000+j*144+122,bytes([method]));u.mem_write(0x20004000+j*144+135,bytes([percent,sel]));u.mem_write(0x20005000+j*60+14,struct.pack('<H',div));u.mem_write(0x20005000+j*60+33,bytes([src]));u.mem_write(0x20005000+j*60+44,struct.pack('<H',conv));u.mem_write(0x20005000+j*60+56,bytes([bits]))
  r=invoke(u,g['symbols']['touch_initialize_source_clock'] if native else 0x6384,[0x20002000]);vals.append((r,u.mem_read(0x20005000,180).hex(),u.mem_read(0x20003500,128).hex()))
 assert vals[0]==vals[1],(n,specs,scale,poly,fine,vals);rows.append({'function':'touch_initialize_source_clock','specs':specs,'scale':scale,'polynomial':poly,'fine_init':fine,'return':vals[0][0]})
for interval,factor in itertools.product([0,1,16383,16384,65535,65536,0x3fffffff,0xffffffff],[0,1,16384,32768,65535,0xffffffff]):
 vals=[]
 for native in [False,True]:
  u=ns['fixture']();u.mem_write(0x20003500+44,struct.pack('<I',factor));vals.append(invoke(u,g['symbols']['touch_timer_cycles'] if native else 0x5d70,[interval,0x20002000]))
 assert vals[0]==vals[1],(interval,factor,vals);rows.append({'function':'touch_timer_cycles','interval':interval,'factor':factor,'return':vals[0]})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Complete original helper/clock-selection instructions vs independent C and compiler division; no call stubs.','Direct SSC helper scope:nonzero polynomial period; pointer-coherent synthetic configurations.','Randomized bounded mixed widgets, no analog acquisition or physical frequency/time proof.']},indent=2)+'\n');print('PASS',len(rows))
