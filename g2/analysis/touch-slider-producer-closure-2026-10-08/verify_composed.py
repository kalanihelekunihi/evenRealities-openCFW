from pathlib import Path
import sys,json,struct,hashlib
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;machine=D.parent/'touch-gesture-machine-closure-2026-10-08';slider=Path(sys.argv[3]);sys.argv=[str(machine/'verify_composed.py'),sys.argv[1],sys.argv[2]];ns={'__file__':str(machine/'verify_composed.py')};exec((machine/'verify_composed.py').read_text().split('out=[]')[0],ns);g=ns['ns'];oldguest=g['guest']
with slider.open('rb') as f:
 e=ELFFile(f);section=e.get_section_by_name('.slider_source');body=(section['sh_addr'],section.data());producer=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='touch_slider_widget')
def guest(native):
 u=oldguest(native)
 if native:u.mem_write(*body)
 return u
g['guest']=guest
patterns={
 'motion':[(100,[1900,1900,1900,2500]),(200,[1900,1900,2500,1900]),(300,[1900,2500,1900,1900]),(400,[2500,1900,1900,1900]),(401,[1900]*4)],
 'stationary_hold':[(100,[1900,1900,1900,2500]),(1099,[1900,1900,1900,2500]),(1100,[1900,1900,1900,2500]),(1200,[1900]*4)],
 'threshold_hysteresis':[(100,[2435]*4),(101,[2436]*4),(200,[2326]*4),(201,[2325]*4),(502,[1900]*4)],
 'negative_baseline_reset':[(100+i,[0]*4) for i in range(32)],
 'clamp':[(100,[65535,65535,65535,65535]),(200,[1900]*4)]}
def session(native,trace):
 u=g['setup'](native,1000,1050,1049,1,2,1);w=0x20004090;c=0x2000503c;u.mem_write(w,struct.pack('<II',c,0x20006500));u.mem_write(w+40,struct.pack('<I',0x20006600));u.mem_write(w+48,struct.pack('<I',1));u.mem_write(w+52,struct.pack('<H',200));u.mem_write(w+56,struct.pack('<H',4));u.mem_write(w+58,b'\x04');u.mem_write(w+60,struct.pack('<I',0x20006700));u.mem_write(w+112,struct.pack('<IH',0x800102,0x6000));u.mem_write(w+122,bytes([1,2]));context=bytearray(60);struct.pack_into('<HH',context,4,3000,3000);struct.pack_into('<HH',context,8,480,100);struct.pack_into('<H',context,12,30);struct.pack_into('<HHH',context,26,300,200,55);context[32]=1;context[34]=1;context[35]=6;struct.pack_into('<I',context,36,0x20006300);u.mem_write(c,bytes(context));u.mem_write(0x20006600,b'\x01');u.mem_write(0x20006700,struct.pack('<IB3x',0x20006800,0));u.mem_write(0x20006800,bytes(8));u.mem_write(0x20006300,bytes(8))
 for i in range(4):u.mem_write(0x20006500+i*10,struct.pack('<HHHBBBB',1900,1900,0,0,0,0,0))
 events=[];latch=None;frames=[]
 def write(u,access,addr,n,value,user):
  nonlocal latch
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');params=list(struct.unpack('<II',u.mem_read(arg,8))) if cmd in [4,5,0x18,0x16,0x17] else [arg]
   if cmd in [4,5]:
    data=bytes(u.mem_read(arg+8,128));events.append([cmd,params,data.hex()]);
    if cmd==4:latch=data
    else:assert data==latch;u.mem_write((params[0]>>16)*128,data)
   else:events.append([cmd,params])
   u.mem_write(0x40100008,struct.pack('<I',0xa0000000))
 u.hook_add(g['UC_HOOK_MEM_WRITE'],write)
 for counter,raws in trace:
  for i,raw in enumerate(raws):u.mem_write(0x20006500+i*10,struct.pack('<H',raw))
  status=g['call'](u,producer if native else 0x4ba8,[1,0x200004ec]);u.mem_write(0x200008e8,struct.pack('<I',counter));g['call'](u,g['symbols']['touch_calibration_report'] if native else 0x3b24,[])
  frames.append({'counter':counter,'input_raws':raws,'status':status,'sensors':u.mem_read(0x20006500,40).hex(),'widget':u.mem_read(c,60).hex(),'position_x':u.mem_read(0x20006300,2).hex(),'history_x':u.mem_read(0x20006800,2).hex(),'debounce':u.mem_read(0x20006600,1).hex(),'gesture':u.mem_read(0x20000940,80).hex(),'record':u.mem_read(0x200009d0,8).hex(),'tx':u.mem_read(0x200009b0,16).hex(),'flags':u.mem_read(0x200009c8,8).hex(),'storage':u.mem_read(0xe400,2048).hex(),'srom':list(events)})
 return frames
out=[]
for name,trace in patterns.items():
 a=session(False,trace);b=session(True,trace);assert a==b,(name,[(i,{k:(x[k],y[k]) for k in x if x[k]!=y[k]}) for i,(x,y) in enumerate(zip(a,b)) if x!=y]);out.append({'name':name,'frames':a})
(D/'composed-results.json').write_text(json.dumps({'status':'PASS_CPU_RAW_TO_POSITION_GESTURE_CALIBRATION_REPORT','sequences':len(out),'steps':sum(len(x['frames']) for x in out),'comparisons':out,'slider_fixture_elf_sha256':hashlib.sha256(slider.read_bytes()).hexdigest(),'limits':['Syntheticacquiredrawcounts and calibratedmaxRaw3000; firmwarestartupmaxRaw0 is runtime-populated,not assumed3000.','Actualfactoryfinger480,hysteresis55,noise300,negativeNoise200,reset30,baselinecoef1,debounce1,positionIIR128 used.','Nativeproducer/gesture/speed/report/storage; originalresetcopysetup plus syntheticSROM,widget2sampleinputs; no ADC/IRQ/physicaltiming.','OnlypositionX/historyX defined; nonXlocalstackfields excluded fromproducer comparison.']},indent=2)+'\n');print('PASS',len(out),'composedrawsequences;',sum(len(x['frames']) for x in out),'steps')
