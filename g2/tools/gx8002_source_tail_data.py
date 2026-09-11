# SPDX-License-Identifier: MIT
"""Explicitly partition authenticated source-envelope fill for source data."""
from hashlib import sha256


def sha(data):
    return sha256(data).hexdigest()


def partition(stock, replacements, data, host_symbol, host_sha256):
    """Return disjoint replacements; callers must separately qualify placement."""
    hosts=[r for r in replacements if r['symbol']==host_symbol]
    if len(hosts)!=1:raise ValueError('Tail data requires one host')
    host=hosts[0]
    start=host['package_offset'];end=start+host['bytes']
    compiled=host.get('compiled_bytes',host['bytes'])
    if host.get('ownership_kind','compiled_c') not in ('compiled_c','compiled_assembly'):
        raise ValueError('Tail host must be executable source')
    if host['sha256']!=host_sha256 or sha(stock[start:end])!=host_sha256:
        raise ValueError('Tail host stock identity')
    payload=host['payload']
    if len(payload)!=host['bytes'] or not 0<compiled<host['bytes'] or sha(payload[:compiled])!=host['compiled_sha256']:
        raise ValueError('Tail host payload identity')
    if payload[compiled:]!=bytes(host['bytes']-compiled):raise ValueError('Tail host fill is not zero')
    lo=data['package_offset'];hi=lo+data['bytes']
    if lo!=start+compiled or hi!=end or lo%4:
        raise ValueError('Tail data must exactly occupy aligned host fill')
    if data.get('ownership_kind')!='generated_source_data' or data.get('compiled_bytes',data['bytes'])!=data['bytes']:
        raise ValueError('Tail data ownership')
    if data['bytes']<=0 or len(data['payload'])!=data['bytes'] or sha(data['payload'])!=data['compiled_sha256']:
        raise ValueError('Tail data payload identity')
    if sha(stock[lo:hi])!=data['sha256']:raise ValueError('Tail data stock identity')
    for other in replacements:
        if other is not host and other['package_offset']<hi and other['package_offset']+other['bytes']>lo:
            raise ValueError('Tail data overlaps another replacement')
    shortened=dict(host,bytes=compiled,payload=payload[:compiled],sha256=sha(stock[start:lo]))
    return [shortened if r is host else r.copy() for r in replacements]+[data.copy()]
