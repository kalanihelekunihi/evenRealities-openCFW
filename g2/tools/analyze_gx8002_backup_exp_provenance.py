# SPDX-License-Identifier: MIT
"""Identify fdlibm exponential constants without claiming implementation equivalence."""
import json,re,struct
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/upstream-fdlibm/e_exp.c';source=path.read_text()
    assert sha(path.read_bytes())=='43e238d65d2372039675acb01957614c9d152b7e93d8b9477732795720d9fbbf'
    rows=[]
    for name,off in [('P1',0x48414),('P2',0x4840c),('P3',0x48404),('P4',0x483fc),('P5',0x483f4)]:
        match=re.search(r'static const double '+name+r' = ([^;]+);',source);assert match
        upstream=struct.unpack('<Q',struct.pack('<d',float(match[1])))[0]
        observed=struct.unpack_from('<Q',stock,off)[0]
        assert observed==(upstream&0x7fffffffffffffff)
        rows.append({'coefficient':name,'package_offset':off,'upstream_bits':hex(upstream),'stock_bits':hex(observed),
                     'comparison':'exact magnitude; negative P2/P4 represented as positive literals with subtraction call sites'})
    result={'stock_sha256':IMAGE_SHA,'entry_offset':0x4818c,'candidate':'fdlibm-derived IEEE double exponential',
            'upstream_repository':'https://github.com/freemint/fdlibm','upstream_commit':'61c059fed98e2ed8d26ca39617321134b33e535a',
            'upstream_path':'e_exp.c','upstream_sha256':sha(path.read_bytes()),'coefficients':rows,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Five polynomial coefficient magnitudes match, with observed argument-reduction and overflow threshold high words supporting identification.',
                      'Does not establish exact origin revision or full behavior. Upstream explicit exception raising and NaN return behavior require comparison with stock; software-double callees remain to be reconstructed.']}
    (ROOT/'docs/research/gx8002-backup-exp-provenance.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
