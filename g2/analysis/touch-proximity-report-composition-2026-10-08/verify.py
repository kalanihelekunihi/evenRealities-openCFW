from pathlib import Path
import sys,json,struct,hashlib
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent
slider=D.parent/'touch-slider-producer-closure-2026-10-08'
prox=Path(sys.argv[4]);args=sys.argv[:];sys.argv=[str(slider/'verify_composed.py'),args[1],args[2],args[3]]
ns={'__file__':str(slider/'verify_composed.py')};exec((slider/'verify_composed.py').read_text().rsplit('\nout=[]',1)[0],ns)
g=ns['g'];producer=ns['producer'];oldguest=g['guest']
with prox.open('rb') as f:
 e=ELFFile(f);sec=e.get_section_by_name('.proximity_source');body=(sec['sh_addr'],sec.data());syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def guest(native):
 u=oldguest(native)
 if native:u.mem_write(*body)
 return u
g['guest']=guest

def session(native,trace,command=None,baseline=1000,overflow=0):
 u=g['setup'](native,baseline,1050,1049,1,1,1);w=0x20004090;c=0x2000503c;u.mem_write(w,struct.pack('<II',c,0x20006500));u.mem_write(w+40,struct.pack('<I',0x20006600));u.mem_write(w+48,struct.pack('<I',1));u.mem_write(w+52,struct.pack('<H',200));u.mem_write(w+56,struct.pack('<H',4));u.mem_write(w+58,b'\x04');u.mem_write(w+60,struct.pack('<I',0x20006700));u.mem_write(w+112,struct.pack('<IH',0x800102,0x6000));u.mem_write(w+122,bytes([1,2]));context=bytearray(60);struct.pack_into('<HH',context,4,3000,3000);struct.pack_into('<HH',context,8,480,100);struct.pack_into('<H',context,12,30);struct.pack_into('<HHH',context,26,300,200,55);context[32]=1;context[34]=1;context[35]=6;struct.pack_into('<I',context,36,0x20006300);u.mem_write(c,bytes(context));u.mem_write(0x20006600,b'\x01');u.mem_write(0x20006700,struct.pack('<IB3x',0x20006800,0));u.mem_write(0x20006800,bytes(8));u.mem_write(0x20006300,bytes(8))
 for i in range(4):u.mem_write(0x20006500+i*10,struct.pack('<HHHBBBB',1900,1900,0,0,0,0,0))
 w2=0x20004120;c2=0x20005078
 u.mem_write(w2,struct.pack('<II',c2,0x20006000));u.mem_write(w2+28,struct.pack('<III',0x20007000,0x20007100,64));u.mem_write(w2+40,struct.pack('<I',0x20007200));u.mem_write(w2+56,struct.pack('<H',1));u.mem_write(w2+58,b'\x01');u.mem_write(w2+116,struct.pack('<H',0x3696));u.mem_write(w2+122,bytes([1,6]));cxt=bytearray(60);struct.pack_into('<HH',cxt,4,3000,3000);struct.pack_into('<HH',cxt,8,1000,160);struct.pack_into('<H',cxt,12,30);struct.pack_into('<HHH',cxt,26,40,40,10);cxt[32]=3;cxt[34]=1;cxt[35]=6;u.mem_write(c2,bytes(cxt));u.mem_write(0x20006000,struct.pack('<HHHBBBB',1900,1900,0,overflow,0,0,0));u.mem_write(0x20007000,struct.pack('<6H',1900,1900,1900,1900,1900,1900));u.mem_write(0x20007100,b'\x00');u.mem_write(0x20007200,b'\x03\x03')
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
 if command is not None:
  u.mem_write(0x200009a0,bytes([7,command&255,command>>8])+bytes(13));u.mem_write(0x200008ec+64,struct.pack('<I',3));g['call'](u,g['symbols']['app_event'] if native else 0x3700,[0x20]);frames.append({'label':'command7-before-deferred','record':u.mem_read(0x200009d0,8).hex(),'gesture':u.mem_read(0x20000940,80).hex(),'tx':u.mem_read(0x200009b0,16).hex()});g['call'](u,g['symbols']['touch_deferred'] if native else 0x3a80,[])
 for counter,raws,proxraw in trace:
  u.mem_write(0x20006000,struct.pack('<H',proxraw));pstatus=g['call'](u,syms['touch_proximity_raw'] if native else 0x5938,[2,0x200004ec]);g['call'](u,syms['touch_proximity_process'] if native else 0x5a0a,[w2])
  for i,raw in enumerate(raws):u.mem_write(0x20006500+i*10,struct.pack('<H',raw))
  status=g['call'](u,producer if native else 0x4ba8,[1,0x200004ec]);u.mem_write(0x200008e8,struct.pack('<I',counter));g['call'](u,g['symbols']['touch_calibration_report'] if native else 0x3b24,[])
  frames.append({'proximity_raw':proxraw,'proximity_status':pstatus,'proximity_context':u.mem_read(c2,60).hex(),'proximity_sensor':u.mem_read(0x20006000,10).hex(),'proximity_history':u.mem_read(0x20007000,12).hex(),'proximity_fraction':u.mem_read(0x20007100,1).hex(),'proximity_debounce':u.mem_read(0x20007200,2).hex(),'counter':counter,'input_raws':raws,'status':status,'sensors':u.mem_read(0x20006500,40).hex(),'widget':u.mem_read(c,60).hex(),'position_x':u.mem_read(0x20006300,2).hex(),'history_x':u.mem_read(0x20006800,2).hex(),'debounce':u.mem_read(0x20006600,1).hex(),'gesture':u.mem_read(0x20000940,80).hex(),'record':u.mem_read(0x200009d0,8).hex(),'tx':u.mem_read(0x200009b0,16).hex(),'flags':u.mem_read(0x200009c8,8).hex(),'storage':u.mem_read(0xe400,2048).hex(),'srom':list(events)})
 return frames
traces={
 'debounce_activate_release':[(100+i,[1900]*4,2400 if i<18 else 1900) for i in range(40)],
 'inactive_stale_x':[(100,[1900,1900,1900,2500],1900),(150,[1900]*4,1900),(451,[1900]*4,1900),(452,[1900]*4,1900)],
 'hold_during_proximity':[(100+i*100,[1900,1900,1900,2500] if i<15 else [1900]*4,2400 if i<18 else 1900) for i in range(35)],
 'negative_reset_calibration':[(100+i,[1900]*4,0) for i in range(45)],
 'wrapped_callbacks':[(0xfffffff0,[1900,1900,1900,2500],1900),(984,[1900,1900,1900,2500],2400),(1020,[1900]*4,2400)]}
out=[]
def compare(name,trace,**kwargs):
 a=session(False,trace,**kwargs);b=session(True,trace,**kwargs);assert a==b,(name,[(i,{k:(x[k],y[k]) for k in x if x[k]!=y[k]}) for i,(x,y) in enumerate(zip(a,b)) if x!=y]);out.append({'name':name,'parameters':kwargs,'frames':a})
for name,trace in traces.items():compare(name,trace)
for command in [0,1,1000,65535]:compare('command7_reset',traces['hold_during_proximity'][:18],command=command)
for baseline in [0,1900,2000]:compare('calibration_ordering',traces['debounce_activate_release'],baseline=baseline)
compare('overflow_preserved',traces['inactive_stale_x'],baseline=0,overflow=4)
(D/'results.json').write_text(json.dumps({'status':'PASS','sequences':len(out),'steps':sum(len(x['frames']) for x in out),'comparisons':out,'elf_sha256':hashlib.sha256(prox.read_bytes()).hexdigest(),'limits':['Synthetic acquired counts, maxRaw3000 and explicitly sequenced calls.','SROM synthetic; physicalADC/timing/IRQ concurrency not verified.','Stock uninitialized slider nonX stack bytes excluded, defined X/count compared.']},indent=2)+'\n');print('PASS',len(out),'sequences',sum(len(x['frames']) for x in out),'steps')
