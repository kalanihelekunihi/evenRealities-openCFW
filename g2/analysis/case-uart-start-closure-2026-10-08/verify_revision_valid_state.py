"""Held-out public revision controls with a valid prior IDLE event value2."""
from pathlib import Path
import sys,struct,json,hashlib,itertools
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('rows=[]')[0],ns);rows=[]
for width,rto,version in itertools.product([1,2],[0,1],['v140','v143','v144','v145','v146','v147']):
 vals=[]
 for a,stock in [(ns['entries'][width][0],True),(ns['symbols']['case_public_rx'+str(width*8)+'_'+version],False)]:
  u=ns['guest'](0x22,1,0xff,0x5a,1,1,0,rto);u.mem_write(ns['H']+0x70,struct.pack('<I',2));vals.append(ns['run'](u,a,stock,require_atomic=stock))
 matches=vals[0]==vals[1];expected=version=='v145' or (version in ['v146','v147'] and rto==0);assert matches==expected;rows.append(dict(width=width,rto_enabled=rto,version=version,initial_valid_rx_event=2,matches_stock=matches,stock_writes=vals[0][0],candidate_writes=vals[1][0],stock_event=struct.unpack_from('<I',vals[0][1],0x70)[0],candidate_event=struct.unpack_from('<I',vals[1][1],0x70)[0]))
(D/'valid-event-revision-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'accepted':sum(x['matches_stock'] for x in rows),'rejected':sum(not x['matches_stock'] for x in rows),'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Valid earlier IDLE RxEventType2 replaces arbitrary sentinel55 from prior broad fixture.','Candidate1.4.6/7 agrees when RTOEN is clear but differs when set; no unique producer claim.','Same explicit product-callback boundary and synthetic MMIO limitations as sealed receive batch.']},indent=2)+'\n');print('PASS',len(rows),'revision controls')
