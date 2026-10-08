from pathlib import Path
import sys,json,itertools
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[]\nfor b,delta')[0],ns)
initialization=[];traces=[]
for value,nulls in itertools.product([0,1,1000,65535],[0,1,2,3]):
 outputs=[]
 for native in [False,True]:
  u=ns['guest'](native);u.mem_write(0x20006000,b'\xab'*80);u.mem_write(0x20006200,ns['struct'].pack('<H',value));ns['call'](u,ns['symbols']['touch_gesture_initialize'] if native else 0x404c,[0 if nulls&1 else 0x20006000,0 if nulls&2 else 0x20006200]);outputs.append(u.mem_read(0x20006000,80).hex())
 assert outputs[0]==outputs[1];initialization.append({'parameter':value,'nulls':nulls,'state':outputs[0]})
for value in [0,1,1000,65535]:
 threshold=value or 1000
 for elapsed in sorted(set([max(0,threshold-1),threshold,threshold+1])):
  u=ns['guest'](False);u.mem_write(0x20006200,ns['struct'].pack('<H',value));ns['call'](u,0x404c,[0x20006000,0x20006200]);ns['call'](u,0x4070,[0x20006000,1,100,100]);pointer=ns['call'](u,0x4070,[0x20006000,1,100,100+elapsed]);state=u.mem_read(0x20006000,80);traces.append({'input_parameter':value,'effective_threshold':threshold,'elapsed_counter_units':elapsed,'result_pointer':pointer,'event_bytes':u.mem_read(pointer,3).hex(),'state':state.hex()})
(D/'parameter-results.json').write_text(json.dumps({'status':'PASS_16_NATIVE_ORIGINAL_INIT_AND_12_STOCK_THRESHOLD_TRACES','initialization_cases':len(initialization),'original_only_gesture_traces':len(traces),'initialization':initialization,'traces':traces,'limits':['Gesture4070 is original code, not independent native reconstruction.','Elapsed values use counter0x200008e8 units; interrupt cadence not established here.']},indent=2)+'\n');print('PASS',len(initialization),'initializations;',len(traces),'stock threshold traces')
