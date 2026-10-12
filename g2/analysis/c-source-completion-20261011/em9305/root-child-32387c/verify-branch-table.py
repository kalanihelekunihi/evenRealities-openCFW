from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[4];T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump'
target=subprocess.check_output([str(T),'-dr','-Mcpu=em,dsp',str(P/'source.o')],text=True)
labels={int(b,16):int(a,16) for a,b in re.findall(r'([0-9a-f]+) <L([0-9a-f]+)>:',target)};labels[0x32387c]=0
native=(P/'native.txt').read_text()
assert re.search(r'323888:.*bmsk_s\s+r0,r0,0x2',native)
assert re.search(r'32389c:.*brhs.d.nt\s+r0,0x7,38\s+;0x3238c2',native)
assert re.search(r'3238a4:.*bih\s+\[r0\]',native)
slots=[0x3238a8+2*i for i in range(7)];base=labels[0x3238a4]+4
assert [labels[a]-base for a in slots]==[2*i for i in range(7)]
destinations=[0x323910,0x3238b6,0x3238b6,0x3238c2,0x323950,0x3238b6,0x3238b6]
for a,d in zip(slots,destinations):
 assert re.search(rf'3238{a&255:02x}:.*b_s.*;0x{d:x}',native)
 assert f'<L{d:x}>' in next(l for l in target.splitlines() if re.match(rf'\s*{labels[a]:x}:',l) and 'b_s' in l)
assert re.search(r'32390a:.*st\s+r17,\[sp\]',native)
assert re.search(rf'\s*{labels[0x32390a]:x}:.*st\s+r17,\[sp\]',target)
r={'status':'PASS_SEVEN_SLOT_BIH_GUARD_GEOMETRY_AND_NINTH_ARGUMENT_STORE','index_domain_before_guard':'low three bits 0..7','guard':'unsigned index >=7 skips BIH','reachable_slots':7,'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'object_sha256':hashlib.sha256((P/'source.o').read_bytes()).hexdigest(),'limits':['Compositor ABI, incoming register meaning, lifecycle and hardware remain separate gates.']};(P/'branch-table-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
