# SPDX-License-Identifier: MIT
"""Aggregate reply-state evidence without admitting unpromoted helper rewrites."""
import json,re
from build_gx8002_reply_defaults import ROOT,sha
from verify_gx8002_reply_defaults_startup import verify as startup
from verify_gx8002_reply_defaults_response import verify as response
from verify_gx8002_reply_defaults_ack import verify as ack
from verify_gx8002_reply_sdk_response import verify as arbitrary_response
from verify_gx8002_reply_sdk_ack import verify as arbitrary_ack
from verify_gx8002_reply_enqueue_composition import verify as enqueue_response
from verify_gx8002_ack_enqueue_composition import verify as enqueue_ack


def verify():
    evidence={name:fn() for name,fn in [('startup',startup),('response',response),('ack',ack),('arbitrary_response',arbitrary_response),('arbitrary_ack',arbitrary_ack),('enqueue_response',enqueue_response),('enqueue_ack',enqueue_ack)]}
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()))):
        if name=='gx8002-reply-defaults-source-verification.json':continue
        r=json.loads((ROOT/'docs/research'/name).read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a,n=occurrence.get('package_offset'),occurrence.get('bytes')
                if a is not None and n is not None:assert not (a<0x18d90 and 0x18d70<a+n),(name,occurrence)
    promotion={}
    for name in ('app_reply','i2s_ack'):
        live=ROOT/'components/shared/gx8002'/('runtime_gx8002_'+name+'.c');staged=ROOT/'build/gx8002-reply-sdk-types'/(name+'.c')
        promotion[name]={'live_sha256':sha(live.read_bytes()),'staged_sha256':sha(staged.read_bytes()),'identical':live.read_bytes()==staged.read_bytes()}
    return {'evidence':evidence,'helper_promotion':promotion,'source_admitted':False,'hardware_qualified':False,
            'limits':['Staged typed reply packet, startup, arbitrary/initialized helper behavior, enqueue binding and nested enqueue checks pass. Package range is disjoint from registered replacements.',
                      'Readiness only: must promote checked helper sources/compiler flags, refresh their qualification and ownership reports, then admit packet storage and complete full firmware build. Staged tests alone do not qualify currently registered helper types.']}
if __name__=='__main__':
    r=verify();assert json.loads(json.dumps(r))==r;(ROOT/'docs/research/gx8002-reply-defaults-readiness.json').write_text(json.dumps(r,indent=2)+'\n');print('Reply packet readiness checks passed; source admission remains pending')
