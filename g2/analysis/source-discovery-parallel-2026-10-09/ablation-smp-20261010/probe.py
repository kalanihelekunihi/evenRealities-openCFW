"""Analysis-only ELF envelope; never a firmware build or executable replacement."""
from pathlib import Path
import struct, hashlib, json, dataclasses
from ablation.analyzers.binary_context import BinaryContext
from ablation.analyzers.func_profiler import FuncProfiler

out = Path(__file__).resolve().parent
root = out.parents[3]
stock = root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
# Resolve repository root independently of output directory nesting.
stock = next(p for p in out.parents if (p / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').exists()) / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
raw = stock.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
start, end = 0x537d0c, 0x537e9e
code = raw[start-0x437fe0:end-0x437fe0]
assert hashlib.sha256(code).hexdigest() == 'c6c182f8937a91efc42995289820d0589b5ae839960cde0d83aec3f40ba0dbba'
names = b'\0.text\0.symtab\0.strtab\0.shstrtab\0'
strings = b'\0SmpHandler_analysis_label\0'
symbols = bytes(16) + struct.pack('<IIIBBH', 1, start|1, len(code), 0x12, 0, 1)
parts = [code, symbols, strings, names]
data = bytearray(bytes(84)); offsets=[]
for part in parts:
    data.extend(bytes((-len(data)) % 4)); offsets.append(len(data)); data.extend(part)
data.extend(bytes((-len(data)) % 4)); shoff=len(data)
sections = [(0,0,0,0,0,0,0,0,0,0), (1,1,6,start,offsets[0],len(code),0,0,2,0), (7,2,0,0,offsets[1],len(symbols),3,1,4,16), (15,3,0,0,offsets[2],len(strings),0,0,1,0), (23,3,0,0,offsets[3],len(names),0,0,1,0)]
for section in sections: data.extend(struct.pack('<10I', *section))
data[:52] = struct.pack('<16sHHIIIIIHHHHHH', b'\x7fELF\x01\x01\x01'+bytes(9), 2,40,1,start|1,52,shoff,0x5000000,52,32,1,40,5,4)
data[52:84] = struct.pack('<8I',1,offsets[0],start,start,len(code),len(code),5,2)
elf=out/'smp-analysis-only.elf'; elf.write_bytes(data)
(out/'stock-function.bin').write_bytes(code)
ctx=BinaryContext.build(str(elf))
# Core discovers static exports, but only collects Thumb bits from dynamic symbols.
# Explicit bounded adapter supplies the same verified static ELF symbol state.
discovered_thumb = sorted(ctx.thumb_funcs)
ctx.thumb_funcs.add(start)
profile=FuncProfiler.from_context(ctx).profile(start,end_va=end)
(out/'profile.txt').write_text(profile.fmt())
(out/'profile.json').write_text(json.dumps(dataclasses.asdict(profile),indent=2,default=str)+'\n')
(out/'receipt.json').write_text(json.dumps({'stock_sha256':hashlib.sha256(raw).hexdigest(),'function_sha256':hashlib.sha256(code).hexdigest(),'elf_sha256':hashlib.sha256(data).hexdigest(),'range':[hex(start),hex(end)],'discovered_thumb_funcs':discovered_thumb,'adapter_thumb_funcs':[hex(x) for x in sorted(ctx.thumb_funcs)],'scope':'402 original bytes only; no external literal memory or callees; authored symbol and explicit Thumb adapter are analysis metadata; context call graph excluded because built before adapter'},indent=2)+'\n')
print(profile.fmt())
