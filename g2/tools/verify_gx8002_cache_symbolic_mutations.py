# SPDX-License-Identifier: MIT
"""Ensure symbolic cache checks reject altered decoded control/data flow."""
import json
from verify_gx8002_dcache_invalid_range import programs,ROOT
from verify_gx8002_dcache_invalid_loop import block
from verify_gx8002_dcache_invalid_tail import tail
from verify_gx8002_dcache_invalid_signed import nonpositive

def verify():
    _,code=programs();cases=[]
    checks={
        'bulk':lambda c:block(c,0x10025624,0x10025656,'r3','r2',0x10025612),
        'tail':lambda c:tail(c,0x10025618,'r3','r2',17),
        'negative':lambda c:nonpositive(c,0x10025612,'r3','r2')}
    mutations=[('bulk',0x10025628,'st.w','r3, (r2, 0x0)'),
      ('bulk',0x10025624,'addi','r0, r3, 32'),
      ('bulk',0x10025650,'addi','r3, 64'),
      ('bulk',0x10025652,'subi','r1, 64'),
      ('bulk',0x10025654,'br','0x10025618'),
      ('bulk',0x10025654,'addi','r0, 0'),
      ('bulk',0x10025612,'cmplti','r1, 127'),
      ('tail',0x10025658,'subi','r1, 32'),
      ('tail',0x10025656,'st.w','r2, (r0, 0x0)'),
      ('negative',0x10025618,'addu','r1, r3')]
    for kind,pc,op,args in mutations:
        changed=code.copy();changed[pc]=(op,args,code[pc][2])
        try:checks[kind](changed)
        except (AssertionError,ValueError,KeyError):cases.append({'check':kind,'address':pc,'opcode':op,'operands':args})
        else:raise ValueError(('Mutation escaped',kind,hex(pc),op,args))
    return {'rejected_mutations':cases,'count':len(cases),'limits':['Negative checks of verifier sensitivity, not additional firmware equivalence or hardware evidence.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-cache-symbolic-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['count'])
