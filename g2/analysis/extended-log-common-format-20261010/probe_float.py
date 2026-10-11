"""Record authenticated float ABI and the emulator's precise stop frontier."""
import hashlib,json,struct
from pathlib import Path
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_CPU_ARM_CORTEX_M7,UC_CPU_ARM_CORTEX_M33
import verify

HERE=Path(__file__).resolve().parent
dis=(verify.ROOT/'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt').read_text()
for instruction in ('49d53e:','49d542:','49d54e:','49d552:','49d55e:','49d562:','49d580:'):
    assert instruction in dis
assert verify.signature(0x748bec)=='day_high:%f, day_low:%f, dark_price:%f'
lo,hi=struct.unpack('<II',struct.pack('<d',1.5))
stops=[]
for name,cpu in [('M4',UC_CPU_ARM_CORTEX_M4),('M7',UC_CPU_ARM_CORTEX_M7),('M33',UC_CPU_ARM_CORTEX_M33)]:
    try:
        verify.run(True,0x788490,128,(lo,hi),cpu)
        stops.append({'cpu':name,'status':'returned'})
    except RuntimeError as exc:
        stops.append({'cpu':name,'status':'emulator_exception','pc':str(exc),
                      'cause':type(exc.__cause__).__name__})
assert all(x.get('pc')=='0x4d435c' for x in stops)
result={'status':'bounded emulator frontier','image_sha256':hashlib.sha256(verify.raw).hexdigest(),
        'caller':'0x49d580','format':'0x748bec',
        'static_abi':'Three float32 values are converted with vcvt.f64.f32 and stored as d0 at stack offsets +8, +16, +24 before BL; each %f therefore occupies two 32-bit stack words at this caller.',
        'stops':stops,
        'instruction_at_stop':'0x4d435c vmul.f64 d0,d0,d1',
        'limit':'Unicorn Cortex-M4/M7/M33 models do not execute this FP64 instruction; no float output/source comparison or complete float formatter semantics established.'}
(HERE/'float_probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['stops']))
