#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
p=ROOT/'g2/analysis/case-frame-callback-closure-2026-10-08/verify.py';sys.argv=[str(p),str(HERE/'case.elf')];s=p.read_text()
s=s.replace("exec(text,ns);symbols=ns['symbols'];", "text=text.replace('u.mem_map(0x08000000,0x10000)','u.mem_map(0x08000000,0x20000)');exec(text,ns);symbols=ns['symbols'];SOURCE_SEGMENTS=ns['segments'];ns['segments']=[];")
s=s.replace("def run(u,entry,args):\n", "def run(u,entry,args):\n source_run=entry in [symbols[x] for x in ['case_frame_callback','case_frame_resync','case_frame_de_prefix']]\n if source_run:\n  for a,b in SOURCE_SEGMENTS:u.mem_write(a,b)\n")
s=s.replace("if a in (0x080063ec,0x0800a888):", "if a in ((symbols['case_bulk_receive']&~1,symbols['case_event_post']&~1) if source_run else (0x080063ec,0x0800a888)):")
s=s.replace("'bulk_receive' if a==0x080063ec else 'event_post'", "'bulk_receive' if a==(symbols['case_bulk_receive']&~1 if source_run else 0x080063ec) else 'event_post'")
s=s.replace("[:4 if a==0x080063ec else 2]", "[:4 if a==(symbols['case_bulk_receive']&~1 if source_run else 0x080063ec) else 2]")
s=s.replace("return (state,writes,bytes(u.mem_read(0x20000000,0x2000)),", "ram=bytearray(u.mem_read(0x20000000,0x2000))\n if source_run:\n  ptr=struct.unpack_from('<I',ram,UART-0x20000000+0x74)[0]\n  for native,name in [(0x08008759,'case_boot_sensor_callback_8758'),(0x08008809,'case_boot_sensor_callback_8808'),(0x08008999,'case_boot_sensor_callback_8998'),(0x08008a49,'case_boot_sensor_callback_8a48')]:\n   if ptr==symbols[name]:struct.pack_into('<I',ram,UART-0x20000000+0x74,native)\n return (state,writes,bytes(ram),")
s=s.replace("(D/'results.json').write_text", "(OUTPUT/'frame-regression.json').write_text")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'OUTPUT':HERE})
f=HERE/'frame-regression.json';r=json.loads(f.read_text());r['limits']=['Actual integrated selected source graph; native bulk/event entry cuts qualify caller args/state, not child effects or callback suffix after completion.','Source relocated receive callback pointer normalized only by4 explicit native/provider identity joins.','Synthetic coherent USART/MMIO/IRQ states; no physical execution or whole-image proof.'];r['adapted_harness_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();f.write_text(json.dumps(r,indent=2)+'\n')
