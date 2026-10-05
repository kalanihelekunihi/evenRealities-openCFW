#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Export/validate/losslessly repack six authenticated local vendor L8 resources.

This optional tool never changes the reference manifest or firmware provider.
PGM is an inspection format; exact .l8 bytes are the repack input.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
import tempfile
from pathlib import Path

MAP = Path(__file__).with_name('manifests') / 'g2-l8-resource-map.json'
MAP_SHA = '33115d16c9917b0908943c4f2c91b0f8955b3b255bf5a06fe10adf736841595d'
def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)
def load_map() -> dict:
    data = MAP.read_bytes()
    require(digest(data) == MAP_SHA, 'resource map identity mismatch')
    return json.loads(data)
def validate_payload(payload: bytes, spec: dict) -> None:
    require(len(payload) == spec['payload_size'] and digest(payload) == spec['payload_sha256'], 'payload identity mismatch')
    ranges = []
    names = set()
    for a in spec['assets']:
        name = a['asset']
        require(name not in names and Path(name).name == name and name not in ('', '.', '..'), 'invalid asset name')
        names.add(name)
        d0,d1 = a['descriptor_payload_range']; lo,hi = a['pixel_payload_range']
        require(0 <= d0 < d1 <= len(payload) and d1-d0 == 28 and 0 <= lo < hi <= len(payload), 'resource range invalid')
        header = payload[d0:d1]
        require(digest(header) == a['descriptor_sha256'], 'descriptor identity mismatch')
        magic,color,flags,w,h,stride,res,size,ptr,storage,handlers = struct.unpack('<BBHHHHHIIII', header)
        require((magic,color,flags,res,storage,handlers)==(25,6,0,0,0,0), 'unsupported descriptor format')
        require((w,h,stride)==(a['width'],a['height'],a['stride']) and w>0 and h>0 and stride==w, 'resource geometry mismatch')
        require(size==hi-lo==stride*h and ptr-spec['runtime_base']==lo, 'resource pointer/size mismatch')
        require(int(a['descriptor_runtime'],16)==d0+spec['runtime_base'] and a['pixel_runtime_range']==[lo+spec['runtime_base'],hi+spec['runtime_base']], 'resource address-domain mismatch')
        require(digest(payload[lo:hi])==a['pixel_sha256'], 'pixel identity mismatch')
        ranges.extend([(d0,d1),(lo,hi)])
    ranges.sort()
    require(all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])), 'overlapping resources')
def pgm(a: dict, pixels: bytes) -> bytes:
    require(len(pixels)==a['width']*a['height'], 'pixel size mismatch')
    return f"P5\n{a['width']} {a['height']}\n255\n".encode('ascii')+pixels
def validate_resources(directory: Path, spec: dict) -> dict[str,bytes]:
    result = {}
    for a in spec['assets']:
        raw = (directory/(a['asset']+'.l8')).read_bytes()
        require(len(raw)==a['width']*a['height'] and digest(raw)==a['pixel_sha256'], 'local resource identity mismatch: '+a['asset'])
        require((directory/(a['asset']+'.pgm')).read_bytes()==pgm(a,raw), 'PGM roundtrip mismatch: '+a['asset'])
        result[a['asset']] = raw
    return result
def export(payload_path: Path, destination: Path, spec: dict) -> None:
    payload = payload_path.read_bytes()
    validate_payload(payload,spec)
    require(not destination.exists(), 'export destination already exists')
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.l8-',dir=destination.parent))
    try:
        for a in spec['assets']:
            lo,hi = a['pixel_payload_range']; raw=payload[lo:hi]
            (stage/(a['asset']+'.l8')).write_bytes(raw)
            (stage/(a['asset']+'.pgm')).write_bytes(pgm(a,raw))
        validate_resources(stage,spec)
        (stage/'provenance.json').write_text(json.dumps(spec,indent=2)+'\n')
        # Exclusive directory creation prevents overwriting a concurrent export.
        destination.mkdir()
        for f in stage.iterdir():
            f.rename(destination/f.name)
    finally:
        shutil.rmtree(stage)
def repack(payload_path: Path, resources: Path, destination: Path, spec: dict) -> None:
    payload = payload_path.read_bytes()
    validate_payload(payload,spec)
    raw = validate_resources(resources,spec)
    result = bytearray(payload)
    for a in spec['assets']:
        lo,hi = a['pixel_payload_range']; result[lo:hi]=raw[a['asset']]
    require(bytes(result)==payload and digest(result)==spec['payload_sha256'], 'lossless repack identity mismatch')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(result)
def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    e=sub.add_parser('export');e.add_argument('--payload',type=Path,required=True);e.add_argument('--output-dir',type=Path,required=True)
    v=sub.add_parser('verify');v.add_argument('--resources',type=Path,required=True)
    r=sub.add_parser('repack');r.add_argument('--payload',type=Path,required=True);r.add_argument('--resources',type=Path,required=True);r.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        spec=load_map()
        if args.command=='export': export(args.payload,args.output_dir,spec)
        elif args.command=='verify': validate_resources(args.resources,spec)
        else: repack(args.payload,args.resources,args.output,spec)
    except (OSError,ValueError,KeyError,struct.error) as error:
        parser.exit(1,f'resource preservation failed: {error}\n')
    print('PASS: '+args.command+' authenticated local L8 resources; official provider unchanged')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
