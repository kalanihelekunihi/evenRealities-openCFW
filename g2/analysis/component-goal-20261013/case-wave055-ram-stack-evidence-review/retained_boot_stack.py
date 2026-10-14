from pathlib import Path
import struct,json,hashlib
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3]
F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
E=H.parent/'case-wave039-list-cursor-contract/final/case.elf'
b=F.read_bytes()[32:]
with E.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value']&~1 for s in e.get_section_by_name('.symtab').iter_symbols()}
def source_bytes(a,n):
 for start,data in segments:
  if start<=a and a+n<=start+len(data):return data[a-start:a-start+n]
 raise ValueError(hex(a))
def delta(words):
 d=0
 for w in words:
  if w&0xfe00==0xb400:d+=4*((w&255).bit_count()+((w>>8)&1))
  elif w&0xff80==0xb080:d+=4*(w&127)
  else:raise ValueError(hex(w))
 return d
spec=[(0xa598,'case_application_entry_a598',[0xb088],[0xb088]),(0xa900,'case_boot_scheduler_start',[0xb510],[0xb580]),(0xc284,'case_boot_scheduler_activate',[0xb530,0xb087],[0xb5bf]),(0xc57c,'case_boot_scheduler_run',[0xb510],[0xb580])]
rows=[]
for a,name,nw,sw in spec:
 assert list(struct.unpack('<'+'H'*len(nw),b[a:a+2*len(nw)]))==nw
 sa=symbols[name];assert list(struct.unpack('<'+'H'*len(sw),source_bytes(sa,2*len(sw))))==sw
 rows.append(dict(native_entry=hex(0x08000000+a),source_entry=hex(sa),source_symbol=name,native_prologue_words=list(map(hex,nw)),source_prologue_words=list(map(hex,sw)),native_retained_bytes=delta(nw),source_retained_bytes=delta(sw)))
nt=sum(x['native_retained_bytes'] for x in rows);st=sum(x['source_retained_bytes'] for x in rows)
assert (nt,st)==(88,80)
r=dict(status='PASS_RAW_PROLOGUE_STACK_ACCOUNTING',chain=rows,native_retained_bytes=nt,source_retained_bytes=st,native_post_handoff_MSP_if_entry_initial='0x20002c30',source_post_handoff_MSP_if_entry_initial='0x20002c38',native_remaining_window_bytes=1024-nt,source_remaining_window_bytes=1024-st,qualification_correction='1024 is the initial arithmetic window, not the post-boot IRQ budget. Direct handoff fixtures omit retained boot frames.',scope='Successful scheduler-start path from application entry; prior reset/CRT retained frames and dynamic IRQ nesting not bounded. Child calls which return do not remain in this baseline.',handoff='CONTROL.SPSEL changes to PSP before POP; no MSP restoration. Preserve stock-compatible behavior; resetting MSP would be an intentional change.',limits='392-byte synchronous logging sample is not an IRQ path/global stack bound. Do not subtract it as a proved post-boot IRQ margin.',inputs=[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [F,E]])
(H/'retained-boot-stack.json').write_text(json.dumps(r,indent=2)+'\n');print(nt,st,1024-nt,1024-st)
