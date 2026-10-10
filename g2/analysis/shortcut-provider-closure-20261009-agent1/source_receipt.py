"""Retain bounded native/source discriminators; makes no producing-source claim."""
from pathlib import Path
import json, hashlib, struct, re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];PRE=OUT.parent/'shortcut-provider-archive-20261009-agent1'
UP=ROOT/'third-party/upstream/nationalchip-lvp-kws'
IP=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images'
def digest(b):return hashlib.sha256(b).hexdigest()
spans=[('strlen','xip',0x10206ca0,0x10206cb0),('strncmp','xip',0x10206c7c,0x10206ca0),('printf_','xip',0x10206c24,0x10206c42),('memset','xip',0x102099cc,0x10209a6c),('clk_switch_1m','sram',0x10025a14,0x10025a7a),('gx_request_irq','sram',0x1002553c,0x1002555a),('gx_irq_handler','sram',0x10025574,0x100255ba)]
rows=[]
for sym,image,a,z in spans:
 base=0x10203004 if image=='xip' else 0x10023400
 data=(IP/('binh_a_stage2_'+image+'.bin')).read_bytes();native=(PRE/(image+'-native.txt')).read_text()
 lines=[]
 for line in native.splitlines():
  m=re.match(r'^([0-9a-f]+):',line)
  if m and a<=int(m[1],16)<z:lines.append(line)
 rows.append(dict(symbol=sym,image=image,start=a,end=z,bytes_sha256=digest(data[a-base:z-base]),native=lines,extent_status='bounded inspection, not canonical function boundary'))
sources=['utility/libc/strlen.c','utility/libc/strncmp.c','utility/libc/memset.c','utility/libc/tinyprintf.c','utility/libc/printf.c','boards/nationalchip/grus_gx8002b_aiot_1v/clock_board.c','include/driver/gx_clock/gx_clock_v2.h']
sr=[dict(path=str((UP/p).relative_to(ROOT)),sha256=digest((UP/p).read_bytes())) for p in sources]
sram=(IP/'binh_a_stage2_sram.bin').read_bytes()
table=list(struct.unpack_from('<4I',sram,0x10025cd0-0x10023400));assert table==[28,0,18,1],table
data=dict(source_hashes=sr,bodies=rows,clock_source_table=dict(address=0x10025cd0,words=table),source_correlations={'strlen':'byte scan to NUL then pointer subtraction; generic equivalence, not unique source identity','strncmp':'unsigned-byte subtraction, n==0 returns zero, stops at mismatch or NUL; generic equivalence','printf_':'three-argument call (0,fmt,varargs) agrees with tinyprintf vfprintf wrapper and rejects direct five-argument _vsnprintf wrapper; callee semantics remain open','memset':'stock first aligns an unaligned destination and then word-fills; public C keeps originally unaligned destinations on byte-only path, so not direct producing-source identity','clk_switch_1m':'source table [28,0,18,1], two gx_clock_set_source calls, gate scan module11..25, PLL disable/restore agree with board source family; board and configuration identity unresolved'})
(OUT/'source-receipt.json').write_text(json.dumps(data,indent=2)+'\n')
(OUT/'SHA256MANIFEST.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256MANIFEST.json'},indent=2)+'\n')
print(json.dumps(dict(inspected_bodies=len(rows),source_files=len(sr),source_table=table)))
