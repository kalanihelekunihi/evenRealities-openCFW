#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inventory authenticated upstream model declarations without admitting arrays."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import SDK_COMMIT, IMAGE, IMAGE_SHA, authenticated_blob, sha

ROOT=Path(__file__).resolve().parents[1]


def analyze(sdk):
    if subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],text=True).strip()!=SDK_COMMIT:
        raise ValueError('SDK revision changed')
    if sha(IMAGE.read_bytes())!=IMAGE_SHA:
        raise ValueError('firmware oracle changed')
    tree=subprocess.check_output(['git','-C',str(sdk),'ls-tree','-r','HEAD','lvp/vui/kws/models'],text=True)
    records=[]
    for line in tree.splitlines():
        metadata,name=line.split('\t',1)
        mode,kind,digest=metadata.split()
        if Path(name).name not in ('model.h','model_xip.h'): continue
        if mode!='100644' or kind!='blob': raise ValueError('unexpected model file type')
        data=authenticated_blob(sdk/name,digest)
        text=data.decode('utf-8')
        sizes={}
        for field in ('cmd','weight'):
            matches=re.findall(r'unsigned\s+char\s+(?:xip_)?kws_'+field+r'_content\[(\d+)\]',text)
            if len(matches)!=1: raise ValueError('model declaration not understood: '+name)
            sizes[field]=int(matches[0])
        version=re.search(r'kws_version\s*=\s*"([^"\n]+)"',text)
        info=re.search(r'model_info\s*=\s*"([^"\n]+)"',text)
        records.append({'path':name,'git_blob':digest,'source_sha256':sha(data),
                        'version':version[1] if version else None,'model_info':info[1] if info else None,
                        'declared_command_bytes':sizes['cmd'],'declared_weight_bytes':sizes['weight'],
                        'matches_codec_declared_sizes':sizes=={'cmd':9164,'weight':120800}})
    if not records: raise ValueError('no upstream models inspected')
    return {'sdk_commit':SDK_COMMIT,'firmware_sha256':IMAGE_SHA,
            'codec_command_bytes':9164,'codec_weight_bytes':120800,
            'models_inspected':len(records),'size_candidates':sum(r['matches_codec_declared_sizes'] for r in records),
            'models':records,'source_admitted':False,'firmware_bytes_emitted':0,
            'conclusion':'Declared sizes provide an exclusion screen, not model semantic equivalence.',
            'next_boundary':'Recover codec model/task interfaces and graph semantics; do not substitute an unrelated wake-word model.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk',type=Path,default=ROOT/'build/upstream-nationalchip-lvp-kws')
    p.add_argument('--output',type=Path,default=ROOT/'build/gx8002-upstream-model-inventory.json')
    args=p.parse_args();report=analyze(args.sdk.resolve())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='models'},indent=2))


if __name__=='__main__':main()
