"""Bounded TLSF attribution probe; analysis ELF carries original image bytes."""
from pathlib import Path
import struct, hashlib, json, dataclasses, subprocess
from ablation.analyzers.binary_context import BinaryContext
from ablation.analyzers.func_profiler import FuncProfiler

out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'g2/workflow/target.json').exists())
stock=root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
raw=stock.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
base,start,end=0x437fe0,0x4cff6c,0x4cff9a
body=raw[start-base:end-base]
assert hashlib.sha256(body).hexdigest()=='c1275ed4397a9e46d7c3fe8b57a6f7e434c5a4ac6764d3786235b05c6a401b79'
names=b'\0.text\0.symtab\0.strtab\0.shstrtab\0'; strings=b'\0bounded_original_thumb\0'
symbols=bytes(16)+struct.pack('<IIIBBH',1,start|1,len(body),0x12,0,1)
data=bytearray(bytes(84)); offsets=[]
for part in [raw,symbols,strings,names]:
    data.extend(bytes((-len(data))%4)); offsets.append(len(data)); data.extend(part)
data.extend(bytes((-len(data))%4)); shoff=len(data)
for section in [(0,0,0,0,0,0,0,0,0,0),(1,1,6,base,offsets[0],len(raw),0,0,2,0),(7,2,0,0,offsets[1],len(symbols),3,1,4,16),(15,3,0,0,offsets[2],len(strings),0,0,1,0),(23,3,0,0,offsets[3],len(names),0,0,1,0)]:
    data.extend(struct.pack('<10I',*section))
data[:52]=struct.pack('<16sHHIIIIIHHHHHH',b'\x7fELF\x01\x01\x01'+bytes(9),2,40,1,start|1,52,shoff,0x5000000,52,32,1,40,5,4)
data[52:84]=struct.pack('<8I',1,offsets[0],base,base,len(raw),len(raw),5,2)
elf=out/'main-analysis-only.elf'; elf.write_bytes(data)
ctx=BinaryContext.build(str(elf)); initial=sorted(ctx.thumb_funcs); ctx.thumb_funcs.add(start)
profile=FuncProfiler.from_context(ctx).profile(start,end_va=end)
(out/'profile.txt').write_text(profile.fmt())
(out/'profile.json').write_text(json.dumps(dataclasses.asdict(profile),indent=2,default=str)+'\n')
listing=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb',f'--start-address={start}',f'--stop-address={end}',str(elf)],text=True)
(out/'gnu-thumb.txt').write_text(listing)
# Corroborating helper is analyzed in original address space, not re-labelled.
helper=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb','--start-address=0x4cfd18','--stop-address=0x4cfd70',str(elf)],text=True)
(out/'gnu-helper.txt').write_text(helper)
(out/'receipt.json').write_text(json.dumps({'image_sha256':hashlib.sha256(raw).hexdigest(),'body_sha256':hashlib.sha256(body).hexdigest(),'elf_sha256':hashlib.sha256(data).hexdigest(),'range':[start,end],'mapping':{'base':base,'payload_offset':start-base},'thumb_before_adapter':initial,'thumb_after_adapter':sorted(ctx.thumb_funcs),'metadata':'Authored analysis-only ELF envelope; entire original payload mapped linearly; section executable flag is analysis metadata and makes no whole-image code classification claim.'},indent=2)+'\n')
print(profile.fmt()); print(listing); print(helper)
