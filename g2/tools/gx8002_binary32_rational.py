# SPDX-License-Identifier: MIT
"""Exact finite binary32 division with explicit round-to-nearest-even policy."""
from verify_gx8002_scalbnf_finite import parts

def divide(a,b):
    sa,ma,pa=parts(a);sb,mb,pb=parts(b)
    assert mb, 'Zero divisor requires separate exceptional policy'
    sign=sa^sb
    if not ma:return sign<<31
    power=pa-pb
    high=ma.bit_length()-mb.bit_length()
    if high>=0:
        if ma < mb<<high:high-=1
    elif ma<<-high < mb:high-=1
    high+=power
    if high>127:return (sign<<31)|0x7f800000
    quantum=max(high-23,-149)
    shift=power-quantum
    numerator=ma<<max(shift,0);denominator=mb<<max(-shift,0)
    q,r=divmod(numerator,denominator)
    q+=2*r>denominator or (2*r==denominator and q&1)
    if not q:return sign<<31
    high=q.bit_length()-1+quantum
    if high>127:return (sign<<31)|0x7f800000
    if high< -126:return (sign<<31)|q
    if q.bit_length()>24:q>>=1
    return (sign<<31)|((high+127)<<23)|(q&0x7fffff)

def add(a,b):
    """Finite addition; exact cancellation is positive zero in nearest-even mode."""
    from verify_gx8002_scalbnf_finite import rounded
    sa,ma,pa=parts(a);sb,mb,pb=parts(b)
    power=min(pa,pb)
    total=(-1 if sa else 1)*(ma<<(pa-power))+(-1 if sb else 1)*(mb<<(pb-power))
    sign=int(total<0) if total else sa&sb
    return rounded(sign,abs(total),power)

def operation(op,a,b=None,accumulator=None):
    from verify_gx8002_scalbnf_finite import operation as multiply
    if op=='fcmpznes':
        parts(a)
        return bool(a&0x7fffffff)
    if op in ('fcmphss','fcmplts'):
        sa,ma,pa=parts(a);sb,mb,pb=parts(b);p=min(pa,pb)
        av=(-1 if sa else 1)*(ma<<(pa-p));bv=(-1 if sb else 1)*(mb<<(pb-p))
        return av>=bv if op=='fcmphss' else av<bv
    if op=='fnegs':
        parts(a) # Explicitly restrict this arithmetic model to finite inputs.
        return a^0x80000000
    if op=='fstosi.rz':
        sign,mant,power=parts(a)
        integer=mant<<power if power>=0 else mant>>-power
        integer=-integer if sign else integer
        assert -(1<<31)<=integer<(1<<31), 'Out-of-range conversion policy required'
        return integer&0xffffffff
    if op=='fsitos':
        from verify_gx8002_scalbnf_finite import rounded
        signed=a-(1<<32) if a>>31 else a
        return rounded(int(signed<0),abs(signed),0)
    if op in ('fmacs','fnmacs','fmscs','fnmscs'):
        product=multiply('fmuls',a,b)
        if op in ('fnmacs','fnmscs'):product^=0x80000000
        if op in ('fmscs','fnmscs'):accumulator^=0x80000000
        return add(product,accumulator)
    if op=='fadds':return add(a,b)
    if op=='fsubs':return add(a,b^0x80000000)
    if op=='fdivs':return divide(a,b)
    if op=='frecips':return divide(0x3f800000,a)
    return multiply(op,a,b)

def fused_operation(op,a,b=None,accumulator=None):
    """Alternative single-rounding accumulator policy; not a hardware claim."""
    if op not in ('fmacs','fnmacs','fmscs','fnmscs'):
        return operation(op,a,b,accumulator)
    from verify_gx8002_scalbnf_finite import rounded
    sa,ma,pa=parts(a);sb,mb,pb=parts(b);sc,mc,pc=parts(accumulator)
    sp=sa^sb^(op in ('fnmacs','fnmscs'));sc^=op in ('fmscs','fnmscs')
    pp=pa+pb;power=min(pp,pc)
    total=(-1 if sp else 1)*((ma*mb)<<(pp-power))+(-1 if sc else 1)*(mc<<(pc-power))
    sign=int(total<0) if total else sp&sc
    return rounded(sign,abs(total),power)
