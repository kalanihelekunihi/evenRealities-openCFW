#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify reviewed existing R1 numeric/lookup C data, not instruction arrays."""
import argparse
import hashlib
import json
from pathlib import Path
from source_providers import ROOT,compile_unit,functions

# Explicit semantic scope: voltage calibration, character classification and
# floating-point reduction/approximation constants. Do not scan arbitrary blobs.
SOURCES=['board/native_battery_discharge.c','board/native_battery_initial_curve.c',
         'runtime/native_ctype.c',*[f'runtime/native_{name}.c' for name in (
             'tanh','pow_core','double_directed','atan2f','cosf','atan','tanf',
             'trig_reduce','math_round','exp','math_selection','pow_dispatch',
             'expm1','atanf','expf_tanhf','sinf','log','powf_dispatch','powf_core')]]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():p.error('choose a fresh output directory')
    args.out.mkdir(parents=True)
    plan=json.loads((ROOT/'tools/build/source-plan.json').read_text())
    assets=json.loads((ROOT/'tools/build/resources.json').read_text())
    occupied=[(r['start'],r['end']) for u in plan['units'] for r in u['regions'] if r['payload']=='r1-application']+[(r['start'],r['end']) for r in assets if r['payload']=='r1-application']
    stock=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
    if hashlib.sha256(stock).hexdigest()!='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a':raise ValueError('R1 identity mismatch')
    audits=[]
    flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-I{root}/r1/src/vendor','-isystem','{root}/vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include']
    for index,source in enumerate(SOURCES):
        unit=dict(source='r1/src/application/'+source,argv=flags,regions=[]);folder=args.out/f'{index:04d}'
        _,receipt=compile_unit(unit,folder)
        (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        for symbol in functions(folder/'unit.o',include_objects=True):
            if symbol['symbol_kind']!='data':continue
            audit=dict(source=unit['source'],symbol=symbol['symbol'],size=symbol['size']);audits.append(audit)
            if symbol['executable'] or symbol['writable'] or symbol['relocations'] or symbol['size']<12:
                audit['status']='not immutable literal object of sufficient size';continue
            lo=stock.find(symbol['data']);hi=lo+symbol['size']
            if lo<0 or stock.find(symbol['data'],lo+1)>=0:
                audit['status']='absent or ambiguous placement';continue
            if any(lo<b and a<hi for a,b in occupied):
                audit['status']='already owned or overlaps resource';continue
            occupied.append((lo,hi));audit.update(status='selected',start=lo,end=hi)
            unit['regions'].append(dict(payload='r1-application',symbol=symbol['symbol'],symbol_kind='data',start=lo,end=hi,sha256=hashlib.sha256(symbol['data']).hexdigest(),evidence='tools/build/qualify_data.py',placement_evidence='Unique full immutable numeric/lookup object; byte-equal stored application span'))
        if unit['regions']:plan['units'].append(unit)
    (args.out/'source-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (args.out/'qualification.json').write_text(json.dumps(audits,indent=2)+'\n')
    selected=[r for r in audits if r['status']=='selected'];print(json.dumps(dict(new_regions=len(selected),new_bytes=sum(r['size'] for r in selected))))

if __name__=='__main__':main()
