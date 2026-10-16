# SPDX-License-Identifier: MIT
"""Exclusive stored-byte provenance with conservative executable classification.

Function envelopes are an estimate, not instruction-level proof. Unknown bytes
remain unknown; compressed executable content is not counted twice as RAM code.
"""
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASELINE='g2/analysis/coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/full-accounting.json'
COMPONENTS={'codec':'g2-codec','ble_em9305':'g2-em9305','touch':'g2-touch',
            'case':'g2-case','apollo_bootloader':'g2-apollo-bootloader','apollo_main':'g2-apollo-main'}
CATEGORIES=['c_compiled_executable','assembly_source_executable','compiled_non_executable_data',
            'compiled_unclassified','pulled_executable_confirmed','pulled_non_executable_confirmed','pulled_compressed_initializers',
            'pulled_unclassified','generated_non_executable_container']


def coverage(report, stage):
    baseline=json.loads((ROOT/BASELINE).read_text())
    if report.get('g2_bundle') and baseline['bundle']['sha256']!=report['g2_bundle']['sha256']:
        raise ValueError('coverage baseline belongs to another G2 artifact')
    baseline_components={COMPONENTS[c['component']]:c for c in baseline['componentsExclusive']}
    details=[]
    for payload in report['payloads']:
        size=payload['size']
        cursor=0
        for row in payload['regions']:
            if row['start']!=cursor or not cursor<row['end']<=size or row['size']!=row['end']-cursor:
                raise ValueError('provenance regions must form an exclusive partition')
            cursor=row['end']
        if cursor!=size:raise ValueError('provenance partition incomplete')
        classes=bytearray(size);envelopes=bytearray(size)
        # classes: 0 unclassified, 1 confirmed instructions, 2 confirmed data,
        # 3 compressed initializers whose expanded runtime role is separate.
        if payload['payload'] in baseline_components:
            component=baseline_components[payload['payload']]
            if component['bytes']!=size:raise ValueError('coverage baseline size mismatch')
            end=0
            for lo,hi,kind in component['runs']:
                if lo!=end or not lo<hi<=size:raise ValueError('baseline gap/overlap')
                classes[lo:hi]=bytes([1 if kind==0 else 2 if kind==1 else 0])*(hi-lo);end=hi
            if end!=size:raise ValueError('baseline incomplete')
            for claim in component['claims']:
                if 'compressed' in claim['kind']:
                    lo,hi=claim['range']
                    if not 0<=lo<hi<=size:raise ValueError('invalid compressed initializer span')
                    classes[lo:hi]=b'\3'*(hi-lo)
        # Inventory ranges may contain literal pools/data. Keep this overlay
        # separate from the strict classification and never call it confirmed.
        if payload['payload']=='r1-application':
            path=ROOT/'r1/research/decompilation/application/functions.csv'
            for row in csv.DictReader(io.StringIO(path.read_text())):
                lo=int(row['entry'],16)-0x27000;hi=lo+int(row['size'])
                if 0<=lo<hi<=size:envelopes[lo:hi]=b'\1'*(hi-lo)
        elif payload['payload'].startswith('g2-'):
            names={'g2-apollo-main':('apollo_main',0x437fe0),'g2-apollo-bootloader':('bootloader',0x410000),
                   'g2-case':('case',0x8000000-32),'g2-touch':('touch',0x3300-32)}
            if payload['payload'] in names:
                name,base=names[payload['payload']]
                for row in csv.DictReader(io.StringIO((ROOT/f'g2/symbols/{name}.tsv').read_text()),delimiter='\t'):
                    if not row['size']:continue
                    lo=int(row['address'],16)-base;hi=lo+int(row['size'])
                    if 0<=lo<hi<=size:envelopes[lo:hi]=b'\1'*(hi-lo)
        for row in payload['regions']:
            if row['owner']=='resource-file':classes[row['start']:row['end']]=b'\2'*row['size']
        totals=Counter({k:0 for k in CATEGORIES});estimated=0;regions=[]
        for row in payload['regions']:
            lo,hi=row['start'],row['end']
            if row['owner']=='source-built':
                provider=row.get('source_provider')
                if provider:
                    offset=lo-provider.get('start',lo)
                    parts=[dict(start=max(0,p['start']-offset),end=min(hi-lo,p['end']-offset),kind=p['kind'])
                           for p in provider['content_ranges'] if p['start']<offset+hi-lo and offset<p['end']]
                    origin=provider['instruction_origin']
                    end=0
                    for part in parts:
                        if part['start']!=end or not part['start']<part['end']<=hi-lo:raise ValueError('source content map incomplete')
                        start,finish=lo+part['start'],lo+part['end'];end=part['end']
                        category=('c_compiled_executable' if origin=='c' else 'assembly_source_executable') if part['kind']=='code' else 'compiled_non_executable_data' if part['kind']=='data' else 'compiled_unclassified'
                        totals[category]+=finish-start
                        regions.append(dict(start=start,end=finish,category=category,evidence=provider['file']))
                    if end!=hi-lo:raise ValueError('source content map gap')
                else:
                    totals['compiled_unclassified']+=hi-lo
                    regions.append(dict(start=lo,end=hi,category='compiled_unclassified',evidence='legacy recipe without ELF mapping symbols'))
            else:
                # Count intersections exactly, then emit compact runs.
                start=lo;previous=None
                for offset in range(lo,hi):
                    kind=classes[offset]
                    category='pulled_executable_confirmed' if kind==1 else 'pulled_non_executable_confirmed' if kind==2 else 'pulled_compressed_initializers' if kind==3 else 'pulled_unclassified'
                    totals[category]+=1
                    if kind==0 and envelopes[offset]:estimated+=1
                    if category!=previous:
                        if previous is not None:regions.append(dict(start=start,end=offset,category=previous))
                        start=offset;previous=category
                if previous is not None:regions.append(dict(start=start,end=hi,category=previous))
        if sum(totals.values())!=size:raise ValueError('coverage does not reconcile')
        details.append(dict(payload=payload['payload'],size=size,totals=dict(totals),
                            unclassified_bytes_inside_function_envelopes=estimated,regions=regions))
    def aggregate(name, selected, overhead=0):
        total=sum(x['size'] for x in selected)+overhead
        counts=Counter({k:0 for k in CATEGORIES})
        for x in selected:counts.update(x['totals'])
        counts['generated_non_executable_container']+=overhead
        if sum(counts.values())!=total:raise ValueError('aggregate denominator mismatch')
        executable_lower=sum(counts[k] for k in ('c_compiled_executable','assembly_source_executable','pulled_executable_confirmed'))
        executable_upper=executable_lower+counts['pulled_unclassified']+counts['compiled_unclassified']
        code_share=[100*counts['c_compiled_executable']/bound if bound else None for bound in (executable_upper,executable_lower)]
        return dict(stored_executable_denominator_bounds_bytes=[executable_lower,executable_upper],
                    compiled_c_share_of_stored_executable_bounds_percent=code_share,
                    scope=name,denominator_bytes=total,bytes=dict(counts),
                    percent_of_stored_firmware={k:100*v/total for k,v in counts.items()},
                    unclassified_bytes_inside_function_envelopes=sum(x['unclassified_bytes_inside_function_envelopes'] for x in selected))
    summaries=[]
    for device in ('g2','r1'):
        selected=[x for x in details if x['payload'].startswith(device+'-')]
        if selected:
            overhead=report['g2_bundle']['size']-sum(x['size'] for x in selected) if device=='g2' and report.get('g2_bundle') else 0
            summaries.append(aggregate(device,selected,overhead))
    overhead=sum(s['bytes']['generated_non_executable_container'] for s in summaries)
    summaries.append(aggregate('combined',details,overhead))
    from classify_remaining import classify
    remaining=classify(details,report,stage,baseline,COMPONENTS)
    result=dict(remaining_classification=remaining,schema=1,denominator_policy='Stored G2 OTA bundle plus R1 application OTA; no absent R1 resident images, expanded RAM bytes or external flash.',
                classification_policy='Only authenticated baseline confirmed instructions/data, verified resource spans and ELF ARM mapping symbols establish strict classes. Function envelopes remain an explicitly estimated overlay.',
                baseline_sha256=hashlib.sha256((ROOT/BASELINE).read_bytes()).hexdigest(),
                baseline_path=BASELINE,all_executable_bytes_identified=False,summaries=summaries,payloads=details)
    from report_coverage import markdown
    (stage/'coverage.md').write_text(markdown(result))
    (stage/'coverage.json').write_text(json.dumps(result,indent=2)+'\n')
    output=io.StringIO();writer=csv.writer(output);writer.writerow(['scope','denominator_bytes','category','bytes','percent_of_stored_firmware'])
    for summary in summaries:
        for key in CATEGORIES:writer.writerow([summary['scope'],summary['denominator_bytes'],key,summary['bytes'][key],summary['percent_of_stored_firmware'][key]])
    (stage/'coverage.csv').write_text(output.getvalue())
    return {k:v for k,v in result.items() if k!='payloads'}
