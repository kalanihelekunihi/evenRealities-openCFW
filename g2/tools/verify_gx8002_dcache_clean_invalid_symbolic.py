# SPDX-License-Identifier: MIT
"""Symbolic bulk, entry, residual and signed-path checks for clean/invalidate."""
import json
from verify_gx8002_dcache_clean_invalid_range import verify as qualify,programs,ROOT
from verify_gx8002_dcache_invalid_loop import block
from verify_gx8002_dcache_invalid_tail import tail,sequence
from verify_gx8002_dcache_invalid_signed import nonpositive

def verify():
    evidence=qualify();old,new=programs();d=0xb8
    stock=block(old,0x1763a+d,0x1766c+d,'r0','r3',0x17628+d)
    source=block(new,0x10025624+d,0x10025656+d,'r3','r2',0x10025612+d)
    assert sequence(old,0x1761c+d,0x17628+d)==[('movi','r3, 0'),('subi','r3, 16'),('and','r0, r3'),('ori','r0, r0, 10'),('lrw','r3, 0xe000f000')]
    assert sequence(new,0x10025608+d,0x10025612+d)==[('andni','r0, r0, 15'),('ori','r3, r0, 10'),('lrw','r2, 0xe000f000')]
    for remaining in range(128):
        assert tail(old,0x1762e+d,'r0','r3',remaining)==tail(new,0x10025618+d,'r3','r2',remaining)
    negative_stock=nonpositive(old,0x17628+d,'r0','r3')
    negative_source=nonpositive(new,0x10025612+d,'r3','r2')
    return {'evidence':evidence,'stock_bulk':stock,'source_bulk':source,'symbolic_tail_lengths':128,'stock_nonpositive':negative_stock,'source_nonpositive':negative_source,'source_admitted':False,'limits':['Entry aligns to 16 bytes and sets operation bits 10. Arbitrary modulo-32 command expressions cover bulk transitions and every residual length. Positive signed size strictly decreases by 128 until a residual below 128; nonpositive signed interval returns without memory access. Architectural semantics assumed; no physical cache coherence or timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-clean-invalid-symbolic.json').write_text(json.dumps(r,indent=2)+'\n');print('Clean/invalidate symbolic entry, bulk, 128 tails and nonpositive interval passed')
