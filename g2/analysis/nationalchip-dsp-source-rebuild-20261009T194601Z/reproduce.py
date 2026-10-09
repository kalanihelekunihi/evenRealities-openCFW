"""Replay authentic assembly sources into a caller-selected unsealed output directory."""
from pathlib import Path
import argparse,json,subprocess,hashlib
from elftools.elf.elffile import ELFFile
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
d=Path(__file__).resolve().parent;r=d.parents[2];out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
receipt=json.loads((d/'assembly-results.json').read_text());raw=(r/'g2/blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()
assembler=r/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-as'
assert hashlib.sha256(assembler.read_bytes()).hexdigest()==receipt['assembler_sha256']
comparisons=[]
for entry in receipt['results']:
 src=r/entry['source'];assert hashlib.sha256(src.read_bytes()).hexdigest()==entry['source_sha256']
 pp=out/(src.stem+'.s');obj=out/(src.stem+'.o')
 subprocess.run(['/usr/bin/clang','-E','-P','-x','assembler-with-cpp',str(src),'-o',str(pp)],check=True)
 subprocess.run([str(assembler),'-mcpu=ck804ef','-mhard-float','-EL',str(pp),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  elf=ELFFile(f)
  for c in entry['comparisons']:
   sec=elf.get_section_by_name(c['section']);b=sec.data();assert len(b)==c['expected_bytes'];assert hashlib.sha256(b).hexdigest()==c['expected_sha256']
   comparisons.append(dict(symbols=c['symbols'],bytes=len(b),sha256=c['expected_sha256'],match=True))
assert len(comparisons)==9 and sum(x['bytes'] for x in comparisons)==1606
(out/'replay-results.json').write_text(json.dumps(comparisons,indent=2)+'\n');print('PASS 9 complete code sections, 1606 bytes')
