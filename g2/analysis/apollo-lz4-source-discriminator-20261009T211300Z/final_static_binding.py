from pathlib import Path
import json,hashlib,sys,importlib.metadata,unicorn,capstone
from capstone import *
r=Path('/repo');d=Path('/out');raw=(r/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];rows=[];lines=[];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for a,b,n in [(0x54ee18,0x54ee2a,'read-alignment helper'),(0x54ee2a,0x54ee3e,'aligned 16bit read helper'),(0x4e0c0c,0x4e0c34,'locked caller wrapper')]:
 data=raw[a-0x438000:b-0x438000];row={'name':n,'start':hex(a),'end':hex(b),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};rows.append(row);lines.append('\n'+n);lines += [f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(data,a)]
(d/'extra-bound-ranges.json').write_text(json.dumps(rows,indent=2)+'\n');(d/'caller-and-extra-helper-disassembly.txt').write_text('\n'.join(lines)+'\n');libs=list(Path(unicorn.__file__).parent.glob('lib/libunicorn*'));(d/'linux-runtime-identity.json').write_text(json.dumps({'python':sys.version,'packages':{x:importlib.metadata.version(x) for x in ['unicorn','capstone','pyelftools']},'native_engine_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in libs if p.is_file()},'comparison_libraries':{v:hashlib.sha256((d/v/'liblz4.so').read_bytes()).hexdigest() for v in ['v1.9.4','v1.10.0']},'firmware_image_sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
