#!/usr/bin/env python3
"""Recover bounded Thumb callback CFGs from an authenticated analysis image."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-event-callbacks';out.mkdir(exist_ok=True);elf=BASE/'i2c5/stock-analysis-exec.elf';assert sha(elf)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';raw=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address=0x42108','--stop-address=0x42bd0',str(elf)],text=True);(out/'native-callback-disassembly.txt').write_text(raw);ins={}
 for line in raw.splitlines():
  m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)(\S+)\s*(.*)',line)
  if m:ins[int(m[1],16)]=dict(address=hex(int(m[1],16)),size=2*len(m[2].split()),mnemonic=m[3],operands=m[4])
 front=json.loads((BASE/'native-event-table-prefixes/callback-frontier.json').read_text());entries=sorted(int(x['address'],16) for x in front['callbacks']);rows=[]
 for entry in entries:
  stop=next((x for x in entries if x>entry),0x42bd0);pending=[entry];seen={};deps=set()
  while pending:
   a=pending.pop()
   if a in seen:continue
   assert entry<=a<stop,(hex(entry),hex(a),hex(stop));v=ins[a];seen[a]=v;m=v['mnemonic'];op=v['operands'];nxt=a+v['size'];terminal=((m.startswith('pop') or m.startswith('ldm')) and 'pc' in op) or (m=='bx' and op.strip()=='lr');branch=(m.startswith('b') and m not in ['bic','bic.w','bics','bfc','bfi','bkpt','bl','blx','bx']) or m in ['cbz','cbnz'];call=m in ['bl','blx']
   if call or branch:
    target=re.search(r'([0-9a-f]+)\s*<',op);assert target,v;dest=int(target[1],16)
    if call or not entry<=dest<stop:deps.add(dest)
    else:pending.append(dest)
   if not terminal and m not in ['b','b.n','b.w']:pending.append(nxt)
  rows.append(dict(address=hex(entry),symbol='r1_event_callback_%08x'%entry,instructions=[seen[x] for x in sorted(seen)],dependencies=[hex(x) for x in sorted(deps)],reachable_bytes=sum(x['size'] for x in seen.values()),next_observed_entry_bound=hex(stop),original_ghidra_body_available=False))
 (out/'callback-contracts.json').write_text(json.dumps(dict(analysis_elf_sha256=sha(elf),disassembly_sha256=sha(out/'native-callback-disassembly.txt'),callbacks=rows),indent=2)+'\n')
 for row in rows:print(row['address'],row['reachable_bytes'],row['dependencies'])
if __name__=='__main__':main()
