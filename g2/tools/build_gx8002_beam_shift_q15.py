# SPDX-License-Identifier: MIT
"""Compile adapted pinned ARM/T-HEAD Q15 shift C with the native macOS compiler."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    relative='utility/libdsp/Source/BasicMathFunctions/csky_shift_q15.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    payload=subprocess.check_output(['git','-C',str(sdk),'cat-file','blob',blob])
    out=ROOT/'build/gx8002-beam-shift-q15';out.mkdir(exist_ok=True)
    original=payload.decode()
    left='__SSAT_16(((q31_t) * pSrc++ << shiftBits))'
    right='(*pSrc++ >> -shiftBits)'
    assert original.count(left)==1 and original.count(right)==2
    modified=original.replace(left,'beam_left(*pSrc++, shiftBits)').replace(right,'beam_right(*pSrc++, -shiftBits)')
    (out/'csky_shift_q15.c').write_text(modified)
    (out/'csky_math.h').write_text("""#include <stdint.h>
typedef int16_t q15_t;
typedef int32_t q31_t;
static inline q15_t beam_left(q15_t value, unsigned shift) {
    if (shift > 15) shift = 15;
    int32_t scaled = (int32_t)value * (int32_t)(1u << shift);
    return scaled > 32767 ? 32767 : scaled < -32768 ? -32768 : (q15_t)scaled;
}
static inline q15_t beam_right(q15_t value, unsigned shift) {
    shift &= 31u; // Decoded vendor PASR uses the low five count bits.
    if (shift > 15) shift = 15;
    return (q15_t)((int32_t)value >> shift);
}
""")
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-guess-branch-probability','-DCSKY_MATH_NO_SIMD','-Dcsky_shift_q15=beam_shift_q15','-I',str(out),'-c',str(out/'csky_shift_q15.c'),'-o',str(out/'shift.o')],check=True)
    (out/'shift.ld').write_text('SECTIONS { .beam_shift_q15 0x1000f0c0 : { *(.text*) } }\n')
    target=out/'shift.elf'
    subprocess.run([pre+'ld','-T',str(out/'shift.ld'),str(out/'shift.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'shift');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'shift.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'adapted_source_sha256':sha((out/'csky_shift_q15.c').read_bytes()),'header_sha256':sha((out/'csky_math.h').read_bytes()),'elf_sha256':sha(target.read_bytes()),'sdk_commit':SDK_COMMIT,'upstream_path':relative,'upstream_blob':blob,'source_sha256':sha(payload),'license':'Apache-2.0','source_modifications':['Replace scalar signed left shift with bounded multiplication and Q15 saturation.','Mask scalar right-shift count to five bits, matching decoded vendor PASR, then bound before target signed shift.'],'extra_flags':['-fno-tree-loop-optimize','-fno-guess-branch-probability'],'configuration':['CSKY_MATH_NO_SIMD','csky_shift_q15=beam_shift_q15'],'header_adapter':'Integer types and explicit scalar saturating-shift helpers; target signed right shift retained.','bytes':sections[0]['size'],'envelope_bytes':116,'fits':sections[0]['size']<=116,'source_admitted':False,'limits':['Standalone upstream C build; decoded shift equivalence and integration remain pending.','Scalar accesses differ from stock packed accesses; partial overlap/MMIO and out-of-range stock shift counts are not qualified.']}
    (ROOT/'docs/research/gx8002-beam-shift-q15.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
