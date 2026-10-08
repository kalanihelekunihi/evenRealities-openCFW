from pathlib import Path
import sys,json,struct
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('rng=random.Random')[0],ns)
traces={
 'single_tap':[(1,100,100),(0,100,200),(0,100,500),(0,100,501)],
 'double_tap':[(1,100,100),(0,100,150),(1,100,450),(0,100,500),(0,100,801)],
 'late_second_tap':[(1,100,100),(0,100,150),(1,100,451),(0,100,500),(0,100,801)],
 'hold_stationary':[(1,100,100),(1,124,1099),(1,124,1100),(1,200,1200),(0,200,1300)],
 'drag_positive':[(1,100,100),(1,125,199),(1,140,200),(1,154,300),(1,155,301),(0,170,302)],
 'drag_negative':[(1,150,100),(1,125,200),(1,110,300),(0,90,301)],
 'wrap_hold':[(1,100,0xfffffff0),(1,100,(0xfffffff0+999)&0xffffffff),(1,100,(0xfffffff0+1000)&0xffffffff),(0,100,1020)],
 'release_299':[(1,100,100),(0,100,399),(0,100,700)],
 'release_300':[(1,100,100),(0,100,400),(0,100,701)],
 'five_taps':[(a,100,t) for i in range(5) for a,t in [(1,100+i*100),(0,150+i*100)]]+[(0,100,851)]}
results=[]
for name,trace in traces.items():
 states=[bytearray(80),bytearray(80)];events=[]
 for a,p,t in trace:
  values=[ns['run'](bool(n),states[n],a,p,t,0) for n in [0,1]];assert values[0]==values[1],(name,a,p,t,values)
  states=[bytearray.fromhex(v['state']) for v in values];events.append({'input':[a,p,t],'event':states[0][77:80].hex(),'state':states[0].hex(),'gpio':values[0]['gpio']})
 results.append({'name':name,'trace':events})
# Initialization/deferred reset contract: caller zeros80 bytes and installs threshold;
# test restarting from an active hold/motion independently of previous state.
reset=[]
for value in [0,1,1000,65535]:
 s=bytearray(80);struct.pack_into('<H',s,0,value);a=ns['run'](False,s,1,100,2000,1);b=ns['run'](True,s,1,100,2000,1);assert a==b;reset.append({'parameter':value,'first_event':bytes.fromhex(a['state'])[77:80].hex(),'state':a['state']})
(D/'sequence-results.json').write_text(json.dumps({'status':'PASS_ORIGINAL_NATIVE_SEQUENTIAL_GESTURE_TRACES','sequences':len(results),'invocations':sum(len(x['trace']) for x in results),'reset_cases':len(reset),'traces':results,'resets':reset,'limits':['Sequential samples/counters and externally reset state; no asynchronous IRQ/ADC/scheduler model.','All software delay instructions execute; GPIO writes observed in synthetic guest memory.']},indent=2)+'\n');print('PASS',len(results),'sequences;',sum(len(x['trace']) for x in results),'steps;',len(reset),'resets')
