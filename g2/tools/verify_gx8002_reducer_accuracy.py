# SPDX-License-Identifier: MIT
"""Independent high-precision Machin-pi oracle for recorded reducer execution."""
import json
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
from build_gx8002_backup_cfft import ROOT,sha
from verify_gx8002_double_addsub_target import floating


def pi(precision):
    with localcontext() as ctx:
        ctx.prec=precision+20
        def atan_inverse(n):
            x=Decimal(1)/n;xx=x*x;term=x;total=x;k=1
            while True:
                term *= -xx;updated=total+term/(2*k+1)
                if updated==total:return total
                total=updated;k+=1
        value=16*atan_inverse(5)-4*atan_inverse(239)
        ctx.prec=precision
        return +value


def oracle(row,precision):
    with localcontext() as ctx:
        ctx.prec=precision
        half_pi=pi(precision)/2
        x=Decimal.from_float(floating(int(row['input'],16)))
        q=(x/half_pi).to_integral_value(rounding=ROUND_HALF_EVEN)
        remainder=x-q*half_pi
        actual=sum((Decimal.from_float(floating(int(row[k],16))) for k in ('high','low')),Decimal(0))
        return int(q),remainder,abs(actual-remainder)


def verify():
    path=ROOT/'docs/research/gx8002-reducer-execution.json';report=json.loads(path.read_text())
    elf=ROOT/'build/gx8002-reducer-execution/probe.elf'
    assert sha(elf.read_bytes())==report['execution_elf_sha256']
    rows=[];errors=[];maximum=Decimal(0)
    for row in report['cases']:
        q,remainder,error=oracle(row,440);q2,r2,e2=oracle(row,520)
        assert q==q2
        assert abs(remainder-r2)<Decimal('1e-120')
        assert row['quadrant_integer']%8==q%8
        if error>=Decimal(2)**-85:errors.append({'input':row['input'],'absolute_remainder_error':str(error)})
        maximum=max(maximum,error)
        rows.append({'input':row['input'],'quotient_mod8':q%8,'absolute_remainder_error':str(error),'precision_crosscheck_difference':str(abs(remainder-r2))})
    result={'execution_report_sha256':sha(path.read_bytes()),'execution_elf_sha256':report['execution_elf_sha256'],'oracle':'Machin identity, independent Decimal arctangent series at 440 and 520 digits; exact binary64 input conversion.','cases':len(rows),'maximum_absolute_remainder_error':str(maximum),'diagnostic_absolute_error_threshold':'2^-85','threshold_exceedances':errors,'details':rows,'source_admitted':False,'limits':['Checks the recorded 16-input execution set only, including +/-1e300. Quotient compared modulo 8 because large reducer returns low bits. Not full-domain accuracy or correct rounding; expanded cases, placement and hardware pending.']}
    (ROOT/'docs/research/gx8002-reducer-accuracy.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],r['maximum_absolute_remainder_error'],len(r['threshold_exceedances']))
