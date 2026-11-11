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


def add_r1_frontier_bindings(symbol_addresses, known_addresses, rows, stock_size):
    """A native callee need not have compilable source to bind a caller.

    Use the application frontier independently of the selected compilation
    units. Entry-only rows can supply addresses, never selected callee bytes.
    Ambiguous names retain all addresses so bind() continues to reject them.
    """
    payload, base = 'r1-application', 0x27000
    for row in rows:
        if row.get('image') != 'application':
            continue
        try:
            address = int(row['entry'], 16)
        except (KeyError, TypeError, ValueError):
            continue
        if address & 1 or not base <= address < base + stock_size:
            continue
        known_addresses[payload].add(address)
        name = row.get('candidate_symbol')
        if name:
            symbol_addresses[payload][name].add(address | 1)


def candidates():
    """Every ARM unit in the device source manifests, anchored to its payload's stock map."""
    import sources
    units = []
    frontier = list(csv.DictReader((ROOT/'r1/symbols/function-frontier.csv').open()))
    bases = {'g2-apollo-main': ('apollo_main', 0x437fe0), 'g2-apollo-bootloader': ('bootloader', 0x410000),
             'g2-case': ('case', 0x8000000-32), 'g2-touch': ('touch', 0x3300-32)}
    inventories = {}
    for device in ('r1', 'g2'):
        manifest = sources.load(device)
        generated = ROOT/'build/generated'/device
        if manifest.get('generated'):
            sources.generate(manifest, generated)
        for unit in sources.units_of(manifest):
            source = unit['source']
            # Analysis harness bodies are not firmware providers.
            if Path(source).name.startswith(('test_', 'probe', 'entry', 'seams')) or Path(source).name == 'decoder.c':
                continue
            flags = [f.replace('{gen}', str(generated)) for f in
                     manifest['profiles'][unit['profile']] + unit.get('flags', [])]
            if unit['toolchain'] == 'clang':
                argv = ['clang', *flags]
            elif unit['toolchain'] == 'gcc9':
                argv = ['python3', *flags]
            elif unit['toolchain'] == 'arm-gcc14':
                spec = manifest['toolchains']['arm-gcc14']
                gcc = ROOT / spec['docker']['mounts']['/tool'] / Path(spec['cc']).relative_to('/tool')
                compiler = str(gcc).replace(str(ROOT), '{root}')
                argv = ['python3', '{root}/tools/build/linux_gcc.py', '--compiler', compiler,
                        '--read-root', '{root}/g2', '--read-root', '{root}/third-party',
                        '--read-root', '{root}/vendor-cache/g2', '--', *flags]
            else:
                continue  # C-SKY and ARC payloads have no stock cut for byte comparison yet
            if unit['payload'] == 'r1-application':
                matches = [r for r in frontier if r['image'] == 'application' and r['candidate_symbol'] and r['size']
                           and source in r['candidate_sources'].split(';')]
                if not matches:
                    continue
                anchors = [dict(symbol=r['candidate_symbol'], start=int(r['entry'], 16)-0x27000, size=int(r['size']))
                           for r in matches]
                evidence = 'r1/symbols/function-frontier.csv'
            elif unit['payload'] in bases:
                symbolfile, base = bases[unit['payload']]
                if symbolfile not in inventories:
                    rows = csv.DictReader((ROOT/f'g2/symbols/{symbolfile}.tsv').open(), delimiter='\t')
                    inventories[symbolfile] = [dict(symbol=r['name'], address=int(r['address'], 16),
                                                    start=int(r['address'], 16)-base, size=int(r['size']))
                                               for r in rows if r['size']]
                anchors = inventories[symbolfile]
                evidence = f'g2/symbols/{symbolfile}.tsv'
            else:
                continue
            candidate = dict(source=source, argv=argv, payload=unit['payload'], evidence=evidence, anchors=anchors)
            if (len(argv) > 3 and argv[:3] ==
                    ['python3', '{root}/tools/build/linux_gcc.py', '--compiler']):
                compiler = argv[3]
                candidate['compiler_path'] = compiler
                candidate['compiler_sha256'] = hashlib.sha256(
                    Path(compiler.replace('{root}', str(ROOT))).read_bytes()).hexdigest()
            if source.startswith('{gen}/'):
                # Match manifest/frontier identities above, but compile the same
                # materialized input that the firmware builder regenerates.
                candidate['manifest_source'] = source
                candidate['source'] = str((generated / source[len('{gen}/'):]).relative_to(ROOT))
            units.append(candidate)
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
    p.add_argument('--source', action='append', help='qualify only this exact manifest source path (repeatable)')
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
            if unit['payload']!='r1-application' or unit['argv'][0]!='clang':continue
            converted=dict(unit)
            converted['argv']=['python3','{root}/tools/build/linux_gcc.py','--compiler',str(gcc).replace(str(ROOT),'{root}'),*[v for p in ('r1','third-party/upstream','vendor-cache/r1','build/generated/r1') for v in ('--read-root','{root}/'+p)],'--',*[a for a in unit['argv'][1:] if not a.startswith('--target=')]]
            converted.update(compiler_path=str(gcc).replace(str(ROOT),'{root}'),compiler_sha256=sha(gcc))
            derived.append(converted)
        original+=derived
    if args.profile in ('g2-gcc','all'):
        from source_providers import sha
        gcc=ROOT/'vendor-cache/g2/touch-gcc-matrix/12.2.Rel1/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-gcc'
        for unit in candidates():
            if not unit['payload'].startswith('g2-') or unit['argv'][0]!='clang':continue
            converted=dict(unit)
            converted['argv']=['python3','{root}/tools/build/linux_gcc.py','--compiler',str(gcc).replace(str(ROOT),'{root}'),'--read-root','{root}/g2','--read-root','{root}/third-party','--',*[a for a in unit['argv'][1:] if not a.startswith('--target=')]]
            converted.update(compiler_path=str(gcc).replace(str(ROOT),'{root}'),compiler_sha256=sha(gcc))
            original.append(converted)
    if args.only_fp_sources:
        original=[u for u in original if any(a.startswith('-mfloat-abi=') for a in u['argv']) and re.search(r'\b(float|double)\b',(ROOT/u['source']).read_text())]
    if args.float_abi!='recorded':
        original=[dict(u,argv=[a for a in u['argv'] if not a.startswith('-mfloat-abi=')]+['-mfloat-abi='+args.float_abi]) for u in original]
    if args.source:
        wanted=set(args.source)
        original=[u for u in original if u['source'] in wanted]
        missing=wanted-{u['source'] for u in original}
        if missing:p.error('no candidate for source: '+', '.join(sorted(missing)))
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
    with (ROOT/'r1/symbols/function-frontier.csv').open() as stream:
        add_r1_frontier_bindings(
            symbol_addresses, known_addresses, csv.DictReader(stream),
            len(stocks['r1-application']))
    native_entries={}
    for payload,base in bases.items():
        if payload=='r1-application':
            rows=csv.DictReader((ROOT/'r1/research/decompilation/application/functions.csv').read_text().splitlines())
            # Manual function-frontier supplements are named entry evidence too.
            # Keep them available for validating recovered branch targets;
            # decompiler inventory alone omits small table-referenced thunks.
            native_entries[payload]=({int(r['entry'],16)-base for r in rows} |
                                     {a-base for a in known_addresses[payload]})
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
        if 'manifest_source' in unit:
            result['manifest_source'] = unit['manifest_source']
        try:
            funcs, receipt = compile_unit(unit, folder)
            (folder/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
            (folder/'unit.json').write_text(json.dumps({k:v for k,v in unit.items() if k!='anchors'},indent=2)+'\n')
            result['compiled'] = True
            selected = []
            reasons=defaultdict(int)
            local_functions = {f['symbol']: f for f in funcs if f['executable']}
            def linked_bindings(found):
                """Include stock-anchored bindings of referenced local C functions."""
                from match_compiled import match
                expanded = dict(found['bindings'])
                pending = list(expanded)
                visited = set()
                while pending:
                    name = pending.pop()
                    if name in visited or name not in local_functions:
                        continue
                    visited.add(name)
                    target = local_functions[name]
                    address = expanded[name] & ~1
                    entry = address - bases[unit['payload']]
                    dependency = match(target, stocks[unit['payload']],
                                       native_entries[unit['payload']] | {entry},
                                       bases[unit['payload']], anchored_entry=entry)
                    if not dependency:
                        raise ValueError('local callee lacks stock-anchored body')
                    for symbol, value in dependency['bindings'].items():
                        if symbol in expanded and expanded[symbol] != value:
                            raise ValueError('conflicting local callee binding')
                        if symbol not in expanded:
                            expanded[symbol] = value
                            pending.append(symbol)
                return expanded
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
                                       binding_evidence='r1/symbols/function-frontier.csv' if unit['payload']=='r1-application' else unit['evidence'])
                        except ValueError:
                            if not args.match_functions:
                                reasons['native_bindings_or_isolated_link_unresolved']+=1
                                continue
                            from match_compiled import match
                            # A named inventory anchor disambiguates repeated bodies.
                            # Recover only relocation scalars, then compile/link the
                            # complete body at that exact entry and require equality.
                            found=match(f,stocks[unit['payload']],
                                        native_entries[unit['payload']]|{lo},
                                        bases[unit['payload']],anchored_entry=lo)
                            if not found:
                                reasons['anchored_relocation_pattern_not_exact']+=1
                                continue
                            try:
                                found['bindings'] = linked_bindings(found)
                                data,_=link_function(folder/'unit.o',f,found['address'],
                                                     found['bindings'],folder/('anchor-'+f['symbol']+'-'+str(lo)))
                            except ValueError:
                                reasons['anchored_relocation_link_unresolved']+=1
                                continue
                            extra={k:found[k] for k in ('bindings','address','match_evidence')}
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
                            found['bindings'] = linked_bindings(found)
                            data,_=link_function(folder/'unit.o',f,found['address'],found['bindings'],folder/('unique-'+f['symbol'])) if f['relocations'] else (f['data'],None)
                            if data==stocks[unit['payload']][found['start']:found['end']]:
                                found.update(payload=unit['payload'],symbol=f['symbol'],sha256=hashlib.sha256(data).hexdigest(),evidence=unit['evidence'])
                                selected.append(found)
                        except ValueError:reasons['recovered_binding_link_not_exact']+=1
            result['rejections']=dict(reasons)
            result['source_implementation_completeness']='not established by compilation or byte matching'
            result['selected'] = selected
            result['reason'] = 'exact selected bodies' if selected else 'no exact anchored body under tested production bindings; integration remains unfinished'
            clean = {k:unit[k] for k in ('source','manifest_source','argv','compiler_path','compiler_sha256') if k in unit}
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
