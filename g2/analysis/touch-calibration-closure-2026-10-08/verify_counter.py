from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'verify.py')};exec((D/'verify.py').read_text().split('cases=[]\nfor b,delta')[0],ns)
u=ns['guest'](False);u.mem_map(0xe000e000,0x1000);u.mem_write(0x200008e8,ns['struct'].pack('<I',123));ns['call'](u,0x3638,[0])
result={'counter_after_init':int.from_bytes(u.mem_read(0x200008e8,4),'little'),'systick_ctrl':int.from_bytes(u.mem_read(0xe000e010,4),'little'),'systick_load':int.from_bytes(u.mem_read(0xe000e014,4),'little'),'callback_slot0':int.from_bytes(u.mem_read(0x20000f40,4),'little')}
assert result=={'counter_after_init':0,'systick_ctrl':3,'systick_load':40,'callback_slot0':0x35e5},result
traces=[]
for value in [0,123,0xffffffff]:
 u.mem_write(0x200008e8,ns['struct'].pack('<I',value));ns['call'](u,0x35e4,[]);after=int.from_bytes(u.mem_read(0x200008e8,4),'little');assert after==(value+1)&0xffffffff;traces.append({'before':value,'after':after})
(D/'counter-results.json').write_text(json.dumps({'status':'PASS_STOCK_COUNTER_SETUP_AND_INCREMENT','setup':result,'increments':traces,'source_clock_enum':'0: clk_lf per pinned cy_systick.h','limits':['SysTick registers synthetic memory; no actual interrupts, time or LF clock frequency measured.','Counter increment is callback invocation count; application/library initialization and clock calibration remain separate.']},indent=2)+'\n');print(result)
