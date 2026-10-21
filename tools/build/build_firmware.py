#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build authenticated hybrid firmware with exclusive byte provenance."""
from __future__ import annotations
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from source_providers import build_selected
from firmware_coverage import coverage
import sources
from compiler_mode import validate_license_free

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/cutting'))
import firmware_cut as cut

CATALOG = ROOT / 'tools/build/resources.json'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def safe_name(value):
    if not value or Path(value).name != value or value in ('.', '..'):
        raise cut.CutError(f'unsafe name: {value}')
    return value


def compose(manifest, stock, source_dir, recipes, resources, stage, providers=None):
    """Resource spans split the accounting, never overlap or inflate totals."""
    payload = safe_name(manifest['payload'])
    image = bytearray(stock)
    owners = []
    for region in manifest['regions']:
        lo, hi = int(region['start'], 16), int(region['end'], 16)
        label = safe_name(region['label'])
        owner = 'binary-pull-through'
        receipt = {}
        if region['state'] == 'source':
            key = payload + '/' + label
            recipe = recipes.get(key)
            if not recipe or not recipe.get('argv') or not recipe.get('inputs'):
                raise cut.CutError(f'{key}: source requires argv and input files in --recipes')
            inputs = {p: cut.sha256((ROOT / p).read_bytes()) for p in recipe['inputs']}
            target = source_dir / payload / (label + '.bin')
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise cut.CutError(f'{target}: source output must be fresh')
            argv = [str(a).replace('{output}', str(target)) for a in recipe['argv']]
            subprocess.run(argv, cwd=ROOT, check=True)
            if inputs != {p: cut.sha256((ROOT / p).read_bytes()) for p in inputs}:
                raise cut.CutError(f'{key}: inputs changed during build')
            built = target.read_bytes()
            if built != stock[lo:hi]:
                raise cut.CutError(f'{key}: source output differs from locked region')
            image[lo:hi] = built
            owner = 'source-built'
            receipt = {'argv': argv, 'inputs': inputs}
        elif region['state'] == 'vendor-binary':
            owner = 'vendor-binary'
        owners.append({'start': lo, 'end': hi, 'owner': owner, 'label': label,
                       'blockers': region.get('blockers', []), **receipt})
    compiled = sorted(providers or [], key=lambda r: r['start'])
    previous = 0
    for provider in compiled:
        lo, hi = provider['start'], provider['end']
        if not 0 <= lo < hi <= len(stock) or lo < previous:
            raise cut.CutError(f'{payload}: invalid/overlapping source provider')
        previous = hi
        if provider['data'] != stock[lo:hi] or cut.sha256(provider['data']) != provider['sha256']:
            raise cut.CutError(f'{payload}: compiled provider differs from locked bytes')
        if any(o['owner'] == 'source-built' and o['start'] < hi and lo < o['end'] for o in owners):
            raise cut.CutError(f'{payload}: duplicate source ownership')
        image[lo:hi] = provider['data']
    assets = sorted(resources, key=lambda r: r['start'])
    previous = 0
    for index, asset in enumerate(assets):
        lo, hi = asset['start'], asset['end']
        if not 0 <= lo < hi <= len(stock) or lo < previous:
            raise cut.CutError(f'{payload}: overlapping/invalid resource range')
        previous = hi
        if asset['payload_sha256'] != manifest['sha256'] or cut.sha256(stock[lo:hi]) != asset['sha256']:
            raise cut.CutError(f'{payload}: resource identity mismatch')
        if any(o['owner'] == 'source-built' and o['start'] < hi and lo < o['end'] for o in owners) or any(o['start'] < hi and lo < o['end'] for o in compiled):
            raise cut.CutError(f'{payload}: resource overlaps source region')
        relative = f'resources/{payload}/{index:04d}.bin'
        path = stage / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(stock[lo:hi])
        # Consume the extracted resource file, preserving exact storage encoding.
        image[lo:hi] = path.read_bytes()
        asset['file'] = relative
    boundaries = sorted({0, len(stock)} | {v for o in owners for v in (o['start'], o['end'])}
                        | {v for a in assets for v in (a['start'], a['end'])}
                        | {v for a in compiled for v in (a['start'], a['end'])})
    rows = []
    for lo, hi in zip(boundaries, boundaries[1:]):
        base = next(o for o in owners if o['start'] <= lo < o['end'])
        asset = next((a for a in assets if a['start'] <= lo < a['end']), None)
        row = dict(base, start=lo, end=hi, size=hi-lo, sha256=cut.sha256(image[lo:hi]))
        provider = next((p for p in compiled if p['start'] <= lo < p['end']), None)
        if provider:
            row.update(owner='source-built', label=provider['symbol'], blockers=[],
                       source_provider={k:v for k,v in provider.items() if k != 'data'})
        if asset:
            row.update(owner='resource-file', resource=asset)
        rows.append(row)
    totals = Counter()
    for row in rows:
        totals[row['owner']] += row['size']
    if sum(totals.values()) != len(stock) or cut.sha256(image) != manifest['sha256']:
        raise cut.CutError(f'{payload}: final accounting/identity mismatch')
    resource_totals = Counter()
    for row in rows:
        if row['owner'] == 'resource-file': resource_totals[row['resource']['kind']] += row['size']
    return bytes(image), {'resource_totals': dict(resource_totals), 'payload': payload, 'size': len(image), 'sha256': cut.sha256(image),
                         'totals': dict(totals), 'regions': rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['g2', 'r1', 'all'], default='all')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/hybrid')
    parser.add_argument('--recipes', type=Path, help='legacy JSON recipes; rejected in license-free mode')
    parser.add_argument('--source-plan', type=Path, default=ROOT/'tools/build/source-plan.json')
    parser.add_argument('--compiler-mode', choices=['license-free'], default='license-free')
    args = parser.parse_args(argv)
    try:
        destination = args.out.resolve()
        if destination.exists():
            raise cut.CutError('output already exists; choose a fresh --out directory')
        manifests = [m for m in cut.load_manifests() if args.device == 'all' or m['device'] == args.device]
        recipes = json.loads(args.recipes.read_text()) if args.recipes else {}
        source_plan = json.loads(args.source_plan.read_text())
        compiler_mode = validate_license_free(source_plan, recipes)
        catalog = json.loads(CATALOG.read_text())
        # Authenticate all inputs before running recipes or publishing output.
        stocks = {}
        for m in manifests:
            cut.check_manifest(m, cut.blocker_ids())
            stocks[m['payload']] = cut.official_bytes(m)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.hybrid-', dir=destination.parent) as tmp:
            stage = Path(tmp)
            report = {'schema': 1, 'mode': 'hybrid', 'source_completeness_proven': False, 'compiler_mode': compiler_mode,
                      'integration_status': json.loads((ROOT/'tools/build/integration-status.json').read_text()),
                      'scope': 'G2 locked six-payload OTA; R1 application OTA only, excludes resident bootloader/SoftDevice/UICR',
                      'resource_catalog_sha256': cut.sha256(CATALOG.read_bytes()),
                      'resource_inventory': json.loads(CATALOG.with_name('resource-inventory.json').read_text()),
                      'source_qualification_sha256': cut.sha256(CATALOG.with_name('source-qualification.json').read_bytes()),
                      'payloads': []}
            devices = {'g2','r1'} if args.device == 'all' else {args.device}
            # Patched vendor headers that the source plan includes from {root}/build/generated/<device>.
            report['generated_inputs'] = {d: sources.generate(sources.load(d), ROOT / 'build/generated' / d)
                                          for d in sorted(devices) if sources.load(d).get('generated')}
            providers, receipts = build_selected(source_plan, stage, devices)
            report['source_builds'] = receipts
            report['source_plan_sha256'] = cut.sha256(args.source_plan.read_bytes())
            images = {}
            for m in manifests:
                image, entry = compose(m, stocks[m['payload']], stage / 'compiled', recipes,
                                       [dict(r) for r in catalog if r['payload'] == m['payload']], stage,
                                       [p for p in providers if p['payload'] == m['payload']])
                path = stage / 'payloads' / Path(m['official']).name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(image)
                entry['file'] = str(path.relative_to(stage))
                entry['binary_fallback_reason'] = 'No selected byte-identical provider: includes both unfinished implementation and compiler/ABI/placement debt; not a source-completeness claim.'
                entry['cut_manifest_sha256'] = cut.sha256(m['_path'].read_bytes())
                report['payloads'].append(entry)
                images[Path(m['official']).name] = image
            if args.device in ('g2', 'all'):
                pack = load_module('opencfw_hybrid_pack', ROOT / 'g2/tools/open_cfw.py')
                manifest = json.loads((ROOT / 'g2/manifests/g2-2.2.6.10.json').read_text())
                data, _ = pack.assemble_evenota(manifest, {c['name']: images[Path(c['provider']['path']).name] for c in manifest['components']})
                pack.validate_evenota_image(data, manifest)
                if cut.sha256(data) != manifest['package']['expected_sha256']:
                    raise cut.CutError('G2 bundle differs from locked target')
                (stage / manifest['package']['output_name']).write_bytes(data)
                report['g2_bundle'] = {'file': manifest['package']['output_name'], 'size': len(data), 'sha256': cut.sha256(data)}
            report['coverage'] = coverage(report,stage)
            (stage / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
            stage.rename(destination)
        for entry in report['payloads']:
            print(entry['payload'] + ': ' + json.dumps(entry['totals']))
        print(f'Build and provenance: {destination}')
        return 0
    except (cut.CutError, OSError, ValueError, RuntimeError, KeyError, subprocess.CalledProcessError) as error:
        print(f'build_firmware: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
