from pathlib import Path
import sys,json,struct,itertools,hashlib
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);rows=[]
def fixture():
 u=ns['guest']();c=bytearray(64);struct.pack_into('<H',c,12,3);c[44]=1;u.mem_write(0x20003000,bytes(c));u.mem_write(0x20002000,struct.pack('<13I',0x20003000,0x20003200,0x20003500,0x20004000,0x20005000,0x20006000,0x20006100,0,0,0,0x20007400,0x20007500,0x20007000));u.mem_write(0x20002000+52,struct.pack('<I',0x20007100));i=bytearray(128);i[90:93]=bytes([1,0,0]);i[93:97]=bytes([6,4,10,1]);i[99]=0;i[100]=7;i[104]=5;i[107]=6;i[109]=3;u.mem_write(0x20003500,bytes(i));u.mem_write(0x20006000,b''.join(struct.pack('<IBB2x',0x40040000,j,p) for j,p in enumerate([1,7,15])));u.mem_write(0x20006100,struct.pack('<IBB2x',0x40040100,7,31))
 for j in range(3):
  w=bytearray(144);struct.pack_into('<III',w,0,0x20005000+j*60,0x20006500+j*40,0x20006200+j*32);w[58]=4;w[122:124]=bytes([1,2 if j<2 else 6]);w[132]=1;w[140]=64;u.mem_write(0x20004000+j*144,bytes(w));ctx=bytearray(60);struct.pack_into('<H',ctx,8,600);struct.pack_into('<H',ctx,12,30);struct.pack_into('<H',ctx,14,24);struct.pack_into('<HH',ctx,26,40,40);ctx[32]=3;ctx[33]=2;struct.pack_into('<H',ctx,44,16);ctx[46:52]=bytes([15,16,2,3,0,2]);struct.pack_into('<H',ctx,54,2);u.mem_write(0x20005000+j*60,bytes(ctx));u.mem_write(0x20006500+j*40,b''.join(bytes(9)+bytes([10+n]) for n in range(4)))
  for n in range(4):u.mem_write(0x20006200+j*32+n*8,struct.pack('<IBB2x',0x20006000+(n%3)*8,0,1))
 u.mem_write(0x20007000,struct.pack('<10H',0,0,1,0,1,1,1,2,2,0));u.mem_write(0x20007100,struct.pack('<8H',0,0,1,1,1,2,2,0));u.mem_write(0x20007400,b'\xa5'*140);u.mem_write(0x20007500,b'\x5a'*176);return u
for typ,csd,csx,shield,invalid,cal in itertools.product([0,1],[0,2,4],[0,2,5],[0,1],[False,True],[0,0x1000]):
 vals=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20003500+116,bytes([csd,csx]));u.mem_write(0x20003000+44,bytes([shield]));u.mem_write(0x20003200+8,struct.pack('<I',cal))
  if invalid:u.mem_write(0x20004000+144+122,b'\x02')
  ns['call'](u,ns['symbols']['touch_generate_all_slots'] if native else 0x56a4,[typ,0x20002000]);vals.append((u.mem_read(0x20007400,140).hex(),u.mem_read(0x20007500,176).hex(),u.mem_read(0x20003500,128).hex()))
 assert vals[0]==vals[1],(typ,csd,csx,shield,invalid,cal,vals);rows.append({'type':typ,'inactive_csd':csd,'inactive_csx':csx,'shield_count':shield,'invalid_sensor_method':invalid,'calibration_flag':cal,'active_frames':vals[0][0],'lp_frames':vals[0][1]})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Actual original all-slot/per-sensor/CDAC/mask/divider instructions versus independent source, no call stubs.','Synthetic descriptors/configurations;5 active/4 LP slots fixed by actual compiled function.','Generation status discarded; physical scan/analog acquisition not validated.']},indent=2)+'\n');print('PASS',len(rows))
