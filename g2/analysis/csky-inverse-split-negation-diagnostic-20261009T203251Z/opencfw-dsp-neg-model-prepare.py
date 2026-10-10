from pathlib import Path
import datetime,json,hashlib
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis'/('csky-inverse-split-negation-diagnostic-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));d.mkdir();Path('/tmp/opencfw-neg-model-path').write_text(str(d));old=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';src=r/'third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source/TransformFunctions/csky_split_rfft_q15.c';text=src.read_text();needle='outI = __SMLSDX(*__SIMD32(pCoefA), *__SIMD32(pSrc1)++, -outI);';assert text.count(needle)==1
helper='''/* ANALYSIS DIAGNOSTIC ONLY. Original source retained unchanged elsewhere.
 * One semantic intervention: negate the Q31 cross product as two signed
 * saturating 16-bit lanes, matching the observed pneg.s16.s backend result.
 * This helper has no signed overflow, negative shifts or implementation-defined
 * unsigned-to-signed conversion. The rest of the authentic algorithm is retained.
 */
#include <stdint.h>
static uint32_t diagnostic_packed_neg16(uint32_t value)
{
    uint32_t lo_bits = value & UINT32_C(0xffff);
    uint32_t hi_bits = value >> 16;
    int32_t lo = lo_bits < UINT32_C(0x8000) ? (int32_t)lo_bits : (int32_t)lo_bits - INT32_C(65536);
    int32_t hi = hi_bits < UINT32_C(0x8000) ? (int32_t)hi_bits : (int32_t)hi_bits - INT32_C(65536);
    lo = lo == -INT32_C(32768) ? INT32_C(32767) : -lo;
    hi = hi == -INT32_C(32768) ? INT32_C(32767) : -hi;
    return ((uint32_t)lo & UINT32_C(0xffff)) | (((uint32_t)hi & UINT32_C(0xffff)) << 16);
}
'''
text=text.replace('void csky_split_rfft_q15(',helper+'\nvoid diagnostic_csky_split_rfft_q15(',1).replace('void csky_split_rifft_q15(','void diagnostic_csky_split_rifft_q15(',1).replace(needle,'outI = __SMLSDX(*__SIMD32(pCoefA), *__SIMD32(pSrc1)++, diagnostic_packed_neg16((uint32_t)outI));');(d/'inverse_split_diagnostic.c').write_text(text)
harness=(old/'harness.c').read_text().replace('text("START ck804ef\\n");','text("DIAGNOSTIC packed-neg-only START\\n");cases=256;goto diagnostic_fft;').replace('for(pat=0;pat<14;pat++)','diagnostic_fft:\nfor(pat=0;pat<14;pat++)').replace('for(real=0;real<2;real++){reset();state=0x471512;','for(real=0;real<2;real++){if(pat*4+inv*2+real<23)continue;reset();state=0x471512;').replace('text("PASS cases=");number(cases);','text("DIAGNOSTIC PASS cases=");number(cases-256);');(d/'diagnostic-harness.c').write_text(harness)
for name in ['tables.h','startup.S','harness.ld']:(d/name).write_bytes((old/name).read_bytes())
(d/'source-intervention.json').write_text(json.dumps({'original_source':str(src.relative_to(r)),'original_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'diagnostic_source_sha256':hashlib.sha256((d/'inverse_split_diagnostic.c').read_bytes()).hexdigest(),'semantic_changes':[{'branch':'little endian inverse split only','original':needle,'diagnostic':'outI = __SMLSDX(*__SIMD32(pCoefA), *__SIMD32(pSrc1)++, diagnostic_packed_neg16((uint32_t)outI));'}],'symbol_namespace':'diagnostic_* exports, original authentic functions retained in original objects','rest_of_authentic_C':'unchanged; original signed-arithmetic limitations are not claimed repaired','cases':'original failing zero-based case256 plus remaining32 FFT cases; no bypass of a new first discrepancy'},indent=2)+'\n');print(d)
