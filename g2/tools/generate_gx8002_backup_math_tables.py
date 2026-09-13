# SPDX-License-Identifier: MIT
"""Generate semantic arithmetic tables without reading firmware or using libm."""
from decimal import Decimal,localcontext,ROUND_HALF_EVEN

def coefficients(precision=80, complex_fft=False):
    with localcontext() as context:
        context.prec=precision
        epsilon=Decimal(10)**(-precision+8)
        def atan_inverse(n):
            x=Decimal(1)/n;power=x;total=x;k=1
            while True:
                power*=-x*x;term=power/(2*k+1);total+=term;k+=1
                if abs(term)<epsilon:return total
        pi=16*atan_inverse(5)-4*atan_inverse(239)
        result=[];margin=Decimal(1)
        for n in (range(192) if complex_fft else range(-128,128)):
            x=Decimal(n)*pi/(128 if complex_fft else 256)
            def series(cosine):
                term=Decimal(1) if cosine else x;total=term;k=1
                while True:
                    divisor=(2*k-1)*(2*k) if cosine else (2*k)*(2*k+1)
                    term*=-x*x/divisor;total+=term;k+=1
                    if abs(term)<epsilon:return total
            for value in ((32768*series(True),32768*series(False)) if complex_fft else (16384*(1-series(True)),16384*series(False))):
                rounded=value.to_integral_value(rounding=ROUND_HALF_EVEN)
                margin=min(margin,Decimal('0.5')-abs(value-rounded))
                result.append(max(-32768,min(32767,int(rounded))) if complex_fft else int(rounded))
        return result,str(margin)

def generate():
    values,margin=coefficients(80);other,_=coefficients(110)
    assert values==other and Decimal(margin)>Decimal('0.00001')
    complex_values,complex_margin=coefficients(80,True);complex_other,_=coefficients(110,True)
    assert complex_values==complex_other and Decimal(complex_margin)>Decimal('0.00001')
    lengths=[n.bit_length() for n in range(256)]
    def declaration(name,ctype,section,items):
        lines=[', '.join(map(str,items[i:i+16])) for i in range(0,len(items),16)]
        return '__attribute__((section("'+section+'"),used))\nconst '+ctype+' '+name+'[] = {\n    '+',\n    '.join(lines)+'\n};\n'
    source='/* SPDX-License-Identifier: MIT */\n/* Generated from mathematical definitions, never firmware bytes. */\n#include <stdint.h>\n'
    source+=declaration('open_cfw_gx8002_backup_q14_pairs','int16_t','.q14_pairs',values)
    source+=declaration('open_cfw_gx8002_backup_complex_coefficients','int16_t','.complex_coefficients',complex_values)
    reversal=[]
    for index in range(256):
        reverse=int(f'{index:08b}'[::-1],2)
        if index<reverse:reversal.extend((index*8,reverse*8))
    assert len(reversal)==240
    source+=declaration('open_cfw_gx8002_backup_bit_reverse','uint16_t','.bit_reverse',reversal)
    source+=declaration('open_cfw_gx8002_backup_bit_lengths','uint8_t','.bit_lengths',lengths)
    return source,{'decimal_precisions':[80,110],'minimum_rounding_margin':margin,'complex_rounding_margin':complex_margin}
