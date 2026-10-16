#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile existing candidates and select exact, anchored firmware bodies.

This does not create or modify firmware source. Nonmatching candidates remain
explicit integration debt, even when bounded behavior tests passed previously.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess
from source_providers import ROOT, compile_unit, link_function
sys.path.insert(0, str(ROOT/'tools/cutting'))
import firmware_cut as cut


def candidates():
    units = []
    rows = list(csv.DictReader((ROOT/'r1/research/source-build/function-frontier.csv').open()))
    for report in sorted((ROOT/'r1/research/source-build').glob('*/report.json')):
        value = json.loads(report.read_text())
        for unit in value.get('units', []):
            source = unit.get('source', '')
            command = unit.get('command')
            if not source or not command or '-c' not in command: continue
            if Path(source).is_absolute():
                try: source = str(Path(source).relative_to(ROOT))
                except ValueError: continue
            matches = [r for r in rows if r['image']=='application' and r['candidate_symbol'] and r['size'] and
                       source in r['candidate_sources'].split(';')]
            if not matches: continue
            argv = []; skip = False
            for a in command:
                if skip: skip = False; continue
                if a in ('-c','-o','-MF','-MT','-MQ'): skip = True; continue
                if a in ('-MD','-MMD'): continue
                argv.append(a.replace(str(ROOT), '{root}'))
            units.append(dict(source=source, argv=argv, payload='r1-application',
                              evidence=str(report.relative_to(ROOT)),
                              anchors=[dict(symbol=r['candidate_symbol'], start=int(r['entry'],16)-0x27000,
                                            size=int(r['size'])) for r in matches]))
    configurations = [
        ('g2-apollo-main', 'apollo_main', 0x437fe0, 'cortex-m55',
         list((ROOT/'g2/components/audio/uart_thread_source_candidate').glob('*.c')) +
         [ROOT/p for p in json.loads((ROOT/'g2/firmware_c/experimental-sources.json').read_text())['apollo_main']]),
        ('g2-apollo-bootloader', 'bootloader', 0x410000, 'cortex-m55',
         list((ROOT/'g2/components/bootloader').glob('*/*.c'))),
        ('g2-case', 'case', 0x8000000-32, 'cortex-m0plus',
         list((ROOT/'g2/components/case/source_candidate_20261010').glob('*.c'))),
        ('g2-touch', 'touch', 0x3300-32, 'cortex-m0plus',
         list((ROOT/'g2/components/touch').glob('*_offline/*.c'))),
    ]
    for payload, symbolfile, base, cpu, sources in configurations:
        inventory = list(csv.DictReader((ROOT/f'g2/symbols/{symbolfile}.tsv').open(), delimiter='\t'))
        anchors = [dict(symbol=r['name'], address=int(r['address'],16), start=int(r['address'],16)-base,
                        size=int(r['size'])) for r in inventory if r['size']]
        for source in sorted(set(sources)):
            # Analysis harness bodies are not firmware providers.
            if source.name.startswith(('test_', 'probe', 'entry', 'seams')) or 'decoder.c' == source.name: continue
            flags = ['clang','--target=arm-none-eabi', '-mcpu='+cpu, '-mthumb', '-std=c11',
                     '-O2', '-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections']
            if cpu == 'cortex-m55': flags += ['-mfpu=fpv5-sp-d16','-mfloat-abi=softfp']
            units.append(dict(source=str(source.relative_to(ROOT)), argv=flags,
                              payload=payload, evidence=f'g2/symbols/{symbolfile}.tsv', anchors=anchors))
    seen = set(); result = []
    for u in units:
        key = (u['source'], tuple(u['argv']))
        if key not in seen: result.append(u); seen.add(key)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=6)
    p.add_argument('--optimizations', nargs='+', default=['recorded'], choices=['recorded','O2','Os','Oz','Og'])
    p.add_argument('--link-functions', action='store_true', help='qualify links against unambiguous stock function symbols')
    p.add_argument('--match-functions', action='store_true', help='recover unique native entries and relocation scalar bindings, then verify full linked equality')
    p.add_argument('--profile', choices=['generic','touch-gcc','r1-gcc','g2-gcc','all'], default='generic')
    p.add_argument('--float-abi', choices=['recorded','soft','softfp','hard'], default='recorded')
    p.add_argument('--only-fp-sources', action='store_true', help='test existing sources containing float/double with an explicit FPU ABI')
    args = p.parse_args()
    if args.out.exists(): p.error('choose a fresh output directory')
    stocks = {m['payload']: cut.official_bytes(m) for m in cut.load_manifests()}
    original = candidates() if args.profile in ('generic','all') else []
    if args.profile in ('touch-gcc','all'):
        from touch_gcc import candidates as gcc_candidates
        original += gcc_candidates()
    if args.profile in ('r1-gcc','all'):
        from source_providers import sha
        gcc=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/bin/arm-none-eabi-gcc'
        derived=[]
        for unit in candidates():
            if unit['payload']!='r1-application':continue
            converted=dict(unit)
            converted['argv']=['python3','{root}/tools/build/linux_gcc.py','--compiler',str(gcc).replace(str(ROOT),'{root}'),*[v for p in ('r1','third-party/upstream','vendor-cache/r1') for v in ('--read-root','{root}/'+p)],'--',*[a for a in unit['argv'][1:] if not a.startswith('--target=')]]
            converted.update(compiler_path=str(gcc).replace(str(ROOT),'{root}'),compiler_sha256=sha(gcc))
            derived.append(converted)
        original+=derived
    if args.profile in ('g2-gcc','all'):
        from source_providers import sha
        gcc=ROOT/'g2/analysis/touch-compiler-matrix-2026-10-09/tools/12.2.Rel1/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-gcc'
        for unit in candidates():
            if not unit['payload'].startswith('g2-'):continue
            converted=dict(unit)
            converted['argv']=['python3','{root}/tools/build/linux_gcc.py','--compiler',str(gcc).replace(str(ROOT),'{root}'),'--read-root','{root}/g2','--read-root','{root}/third-party','--',*[a for a in unit['argv'][1:] if not a.startswith('--target=')]]
            converted.update(compiler_path=str(gcc).replace(str(ROOT),'{root}'),compiler_sha256=sha(gcc))
            original.append(converted)
    if args.only_fp_sources:
        original=[u for u in original if any(a.startswith('-mfloat-abi=') for a in u['argv']) and re.search(r'\b(float|double)\b',(ROOT/u['source']).read_text())]
    if args.float_abi!='recorded':
        original=[dict(u,argv=[a for a in u['argv'] if not a.startswith('-mfloat-abi=')]+['-mfloat-abi='+args.float_abi]) for u in original]
    units = []
    for unit in original:
        for optimization in args.optimizations:
            candidate = dict(unit)
            if optimization != 'recorded':
                candidate['argv'] = [a for a in unit['argv'] if not re.fullmatch(r'-O[0-3sgz]',a)] + ['-'+optimization]
            units.append(candidate)
    args.out.mkdir(parents=True)
    bases={'g2-apollo-main':0x437fe0,'g2-apollo-bootloader':0x410000,
           'g2-case':0x8000000-32,'g2-touch':0x3300-32,'r1-application':0x27000}
    symbol_addresses=defaultdict(lambda:defaultdict(set))
    known_addresses=defaultdict(set)
    for unit in original:
        for anchor in unit['anchors']:
            address=anchor['start']+bases[unit['payload']]
            known_addresses[unit['payload']].add(address)
            if anchor['symbol']: symbol_addresses[unit['payload']][anchor['symbol']].add(address|1)
    native_entries={}
    for payload,base in bases.items():
        if payload=='r1-application':
            rows=csv.DictReader((ROOT/'r1/research/decompilation/application/functions.csv').read_text().splitlines())
            native_entries[payload]={int(r['entry'],16)-base for r in rows}
        else:
            native_entries[payload]={a-base for a in known_addresses[payload]}
    def bind(unit, function):
        bindings={}
        for name in function['relocation_symbols']:
            options=symbol_addresses[unit['payload']].get(name,set())
            suffix=re.search(r'_([0-9a-fA-F]{6,8})$',name)
            if not options and suffix and int(suffix[1],16) in known_addresses[unit['payload']]:
                options={int(suffix[1],16)|1}
            if len(options)!=1: raise ValueError('no unambiguous stock function binding')
            bindings[name]=next(iter(options))
        return bindings
    def check(pair):
        index, unit = pair
        folder = args.out/'compilation'/f'{index:04d}'
        result = dict(source=unit['source'], payload=unit['payload'], evidence=unit['evidence'], selected=[])
        try:
            funcs, receipt = compile_unit(unit, folder)
            (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
            (folder/'unit.json').write_text(json.dumps({k:v for k,v in unit.items() if k!='anchors'},indent=2)+'\n')
            result['compiled'] = True
            selected = []
            reasons=defaultdict(int)
            for f in funcs:
                if not f['executable'] or (f['relocations'] and not (args.link_functions or args.match_functions)): continue
                suffix = re.search(r'_([0-9a-fA-F]{6,8})$', f['symbol'])
                targets = [a for a in unit['anchors'] if a['symbol'] == f['symbol'] or
                           (suffix and a.get('address') == int(suffix[1],16))]
                if not targets:reasons['native_symbol_anchor_missing']+=1
                for a in targets:
                    lo, hi = a['start'], a['start']+f['size']
                    if lo < 0 or hi > len(stocks[unit['payload']]): continue
                    data=f['data']; extra={}
                    if f['relocations']:
                        try:
                            bindings=bind(unit,f)
                            address=lo+bases[unit['payload']]
                            data, _ = link_function(folder/'unit.o',f,address,bindings,folder/('link-'+f['symbol']))
                            extra=dict(bindings=bindings,address=address,
                                       binding_evidence='r1/research/source-build/function-frontier.csv' if unit['payload']=='r1-application' else unit['evidence'])
                        except ValueError:
                            reasons['native_bindings_or_isolated_link_unresolved']+=1
                            continue
                    if data != stocks[unit['payload']][lo:hi]:
                        reasons['compiled_bytes_differ']+=1
                        continue
                    selected.append(dict(payload=unit['payload'], symbol=f['symbol'], start=lo, end=hi,
                                         sha256=hashlib.sha256(data).hexdigest(), evidence=unit['evidence'], **extra))
                if args.match_functions:
                    from match_compiled import match
                    found=match(f,stocks[unit['payload']],native_entries[unit['payload']],bases[unit['payload']])
                    if found:
                        try:
                            data,_=link_function(folder/'unit.o',f,found['address'],found['bindings'],folder/('unique-'+f['symbol'])) if f['relocations'] else (f['data'],None)
                            if data==stocks[unit['payload']][found['start']:found['end']]:
                                found.update(payload=unit['payload'],symbol=f['symbol'],sha256=hashlib.sha256(data).hexdigest(),evidence=unit['evidence'])
                                selected.append(found)
                        except ValueError:reasons['recovered_binding_link_not_exact']+=1
            result['rejections']=dict(reasons)
            result['source_implementation_completeness']='not established by compilation or byte matching'
            result['selected'] = selected
            result['reason'] = 'exact selected bodies' if selected else 'no exact anchored body under tested production bindings; integration remains unfinished'
            clean = {k:unit[k] for k in ('source','argv','compiler_path','compiler_sha256') if k in unit}
            clean['regions'] = selected
            return clean, result
        except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as e:
            result.update(compiled=False, reason=str(e))
            return None, result
    selected, audits, ranges = [], [], {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for unit, audit in pool.map(check, enumerate(units)):
            audits.append(audit)
            if unit and unit['regions']:
                kept=[]
                for r in unit['regions']:
                    occupied=ranges.setdefault(r['payload'],[])
                    if any(r['start'] < hi and lo < r['end'] for lo,hi in occupied): continue
                    occupied.append((r['start'],r['end'])); kept.append(r)
                if kept: unit['regions']=kept;selected.append(unit)
    plan = dict(schema=1, qualification='exact anchored compiled bodies; optional links use unambiguous inventory function addresses', units=selected)
    (args.out/'source-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (args.out/'qualification.json').write_text(json.dumps(dict(candidate_units=len(units), compiled_units=sum(a['compiled'] for a in audits), units=audits),indent=2)+'\n')
    print(json.dumps(dict(candidate_units=len(units), selected_units=len(selected), selected_regions=sum(len(u['regions']) for u in selected))))
    return 0

if __name__ == '__main__': sys.exit(main())
