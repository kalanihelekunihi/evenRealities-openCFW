from pathlib import Path
import sys,json,struct
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify_composed.py')};exec((D/'verify_composed.py').read_text().split('out=[]')[0],ns)
setup=ns['ns']['setup'];call=ns['ns']['call'];symbols=ns['ns']['symbols'];UC_HOOK_MEM_WRITE=ns['ns']['UC_HOOK_MEM_WRITE']
def session(native,trace,command=None,pending_idle=False):
 u=setup(native,1000,1050,1049,1,2 if pending_idle else 1,1);events=[];latch=None;frames=[]
 def write(u,access,addr,n,value,user):
  nonlocal latch
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');params=list(struct.unpack('<II',u.mem_read(arg,8))) if cmd in [4,5,0x18,0x16,0x17] else [arg]
   if cmd in [4,5]:
    data=bytes(u.mem_read(arg+8,128));events.append([cmd,params,data.hex()])
    if cmd==4:latch=data
    else:assert data==latch;u.mem_write((params[0]>>16)*128,data)
   else:events.append([cmd,params])
   u.mem_write(0x40100008,struct.pack('<I',0xa0000000))
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 def snap(label):return {'label':label,'record':u.mem_read(0x200009d0,8).hex(),'gesture':u.mem_read(0x20000940,80).hex(),'tx':u.mem_read(0x200009b0,16).hex(),'flags':u.mem_read(0x200009c8,8).hex(),'events':list(events),'storage':u.mem_read(0xe400,2048).hex(),'i2c':u.mem_read(0x200008ec,84).hex()}
 if command is not None:
  u.mem_write(0x200009a0,bytes([7,command&255,command>>8])+bytes(13));u.mem_write(0x200008ec+64,struct.pack('<I',3));call(u,symbols['app_event'] if native else 0x3700,[0x20]);assert not events;frames.append(snap('command7-before-deferred'));call(u,symbols['touch_deferred'] if native else 0x3a80,[]);frames.append(snap('after-deferred'))
 for active,position,counter in trace:
  u.mem_write(0x20005000+60+35,bytes([active]));u.mem_write(0x20006300,struct.pack('<H',position));u.mem_write(0x200008e8,struct.pack('<I',counter));call(u,symbols['touch_calibration_report'] if native else 0x3b24,[]);frames.append(snap([active,position,counter]))
 return frames
traces={
 'tap_and_baseline':([(1,100,100),(0,100,150),(0,100,450),(0,100,451)],False),
 'pending_calibration_idle':([(0,100,100),(1,100,101),(0,100,150)],True),
 'hold_and_motion':([(1,100,100),(1,124,1099),(1,124,1100),(1,200,1200),(0,200,1300)],False),
 'wrapped_hold':([(1,100,0xfffffff0),(1,100,984),(0,100,1020)],False)}
out=[]
for name,(trace,pending) in traces.items():
 a=session(False,trace,pending_idle=pending);b=session(True,trace,pending_idle=pending);assert a==b,(name,[(x,y) for x,y in zip(a,b) if x!=y]);out.append({'name':name,'frames':a})
for parameter in [0,1,1000,65535]:
 trace=[(1,100,100),(1,100,101),(0,100,102)];a=session(False,trace,command=parameter);b=session(True,trace,command=parameter);assert a==b,parameter;out.append({'name':'command7-reset','parameter':parameter,'frames':a})
(D/'report-sequence-results.json').write_text(json.dumps({'status':'PASS_COMPOSED_COMMAND_DEFERRED_GESTURE_CALIBRATION_REPORT_SEQUENCES','sequences':len(out),'comparisons':out,'limits':['Actual stock/native callback,deferred,storage,gesture/report bodies; SROM and sensor data synthetic.','Calls explicitly sequenced; no IRQ concurrency, analog scan or transportdelivery proof.']},indent=2)+'\n');print('PASS',len(out),'composed command/deferred/report sequences')
