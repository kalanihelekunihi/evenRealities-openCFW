#!/usr/bin/env python3
"""Local-only lossless L8 extraction; no firmware modification or renderer claim."""
import hashlib, json, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SHA = '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
BASE = 0x437fe0
def digest(b): return hashlib.sha256(b).hexdigest()
def chunk(t, b):
    return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t+b))
def encode(w, h, pixels):
    assert len(pixels) == w*h
    rows = b''.join(b'\0'+pixels[y*w:(y+1)*w] for y in range(h))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', w,h,8,0,0,0,0))+chunk(b'IDAT', zlib.compress(rows))+chunk(b'IEND', b'')
def decode(png):
    assert png[:8] == b'\x89PNG\r\n\x1a\n'
    pos=8; compressed=b''; w=h=None
    while pos<len(png):
        n=struct.unpack_from('>I', png,pos)[0]; t=png[pos+4:pos+8]; b=png[pos+8:pos+8+n]
        assert zlib.crc32(t+b)==struct.unpack_from('>I',png,pos+8+n)[0]
        if t==b'IHDR':
            w,h,depth,color,comp,filt,inter=struct.unpack('>IIBBBBB',b)
            assert (depth,color,comp,filt,inter)==(8,0,0,0,0)
        if t==b'IDAT': compressed+=b
        pos+=n+12
    rows=zlib.decompress(compressed); assert len(rows)==(w+1)*h
    assert all(rows[y*(w+1)]==0 for y in range(h))
    return w,h,b''.join(rows[y*(w+1)+1:(y+1)*(w+1)] for y in range(h))
def extract(image,a):
    off=a['descriptor_payload_offset']; header=image[off:off+28]
    magic,color,flags,w,h,stride,res,size,ptr,storage,handlers=struct.unpack('<BBHHHHHIIII',header)
    assert (magic,color,flags,res,storage,handlers)==(25,6,0,0,0,0)
    assert (w,h,stride)==(a['width'],a['height'],a['stride'])
    lo,hi=a['data_payload_range']; assert ptr-BASE==lo and size==hi-lo==stride*h
    assert stride==w and 0<=lo<hi<=len(image)
    pixels=image[lo:hi]; assert digest(pixels)==a['pixel_sha256']
    return header,pixels,encode(w,h,pixels)
def main():
    image=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
    assert digest(image)==SHA
    proof_path=ROOT/'g2/analysis/firmware-byte-map-2026-10-05/display-proof/validation.json'
    proof=json.loads(proof_path.read_text()); assert proof['firmware_sha256']==SHA
    records=[]
    # Five development cases, then sixth held out from format development.
    for i,f in enumerate(proof['family']):
        a=f['asset']; header,pixels,png=extract(image,a)
        w,h,decoded=decode(png); assert (w,h)==(a['width'],a['height']) and decoded==pixels
        name=f"asset-{a['descriptor_runtime']:08x}"
        (OUT/(name+'.png')).write_bytes(png)
        (OUT/(name+'.l8')).write_bytes(pixels)
        records.append(dict(asset=name,test_role='held_out' if i==5 else 'development',payload_sha256=SHA,descriptor_payload_range=[a['descriptor_payload_offset'],a['descriptor_payload_offset']+28],descriptor_runtime=hex(a['descriptor_runtime']),descriptor_sha256=digest(header),pixel_payload_range=a['data_payload_range'],pixel_runtime_range=a['data_runtime_range'],width=w,height=h,stride=a['stride'],pixel_sha256=digest(pixels),png_sha256=digest(png),consumer_chain=['0x5bf332','0x5bf2f8','0x498680','0x4c79d0','0x4c7b24','0x48b762','0x48aef8'],origin='locked official firmware; artwork author unknown',license='proprietary firmware extraction; redistribution permission not established',role='immutable L8 UI image storage; not runtime framebuffer',rebuild_recipe='retain exact .l8 bytes and descriptor/address relocation; PNG is analysis export, not a firmware replacement',dependencies=['LVGL-compatible binary decoder and draw-buffer ABI','constructor/runtime relocation','panel/render pipeline'],limits='Lossless storage decoding; no panel rendering, semantic icon naming or author attribution.'))
    intervals=sorted(r['pixel_payload_range'] for r in records)
    assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
    # Negative control proves wrong color layout is rejected, not silently rendered.
    bad=bytearray(image); bad[proof['family'][5]['asset']['descriptor_payload_offset']+1]=7
    try: extract(bad,proof['family'][5]['asset'])
    except AssertionError: negative=True
    else: raise AssertionError('wrong format accepted')
    report=dict(status='PASS',script_sha256=digest(Path(__file__).read_bytes()),prior_proof_sha256=digest(proof_path.read_bytes()),assets=records,roundtrip_cases=6,held_out_cases=1,wrong_format_rejection=negative,unique_pixel_bytes=sum(b-a for a,b in intervals),newly_classified_bytes=0,extraction_bundle_percent=sum(b-a for a,b in intervals)/4301227*100,limits='Six already admitted assets newly exported standalone; no new code/data coverage or global resource census.')
    (OUT/'extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: six lossless PNG/L8 exports, held-out roundtrip and wrong-format rejection; 28872 existing pixel bytes, zero newly classified bytes')
if __name__=='__main__': main()
