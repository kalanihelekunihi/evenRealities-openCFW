/* IAR DLIB double-precision sqrt, native 0x59c800..0x59c81c, firmware
 * 2.2.6.10. No source path is retained.
 *
 * Stock: VCMPE.F64 d0,#0 (signalling compare, so a NaN raises Invalid but is
 * not "less than"); non-negative or NaN -> VSQRT.F64. Negative -> the high
 * word of d0 is forced to 0x7fffffff (low word kept) and the routine
 * tail-calls the EDOM setter 0x439ca4 (errno 33 at 0x20074f14), which
 * preserves d0. Used by the audio correlation helper (findings-audio.md §4).
 *
 * Hard-float D0 calling convention with a double-precision FPU: profile
 * g2-apollo-main-20 (-mfpu=fpv5-d16). The VCMPE N flag is the ordered
 * x < 0 test (__builtin_isless); __builtin_elementwise_sqrt is the bare
 * VSQRT.F64 (__builtin_sqrt would call sqrt for errno). The stock signalling
 * compare's cumulative IOC flag on NaN is not reproduced; nothing reads it
 * (ldexp/scale paths clear the FPSCR flags before their own check). */
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_float_domain_error_439ca4(void); /* errno = EDOM (33) */

IAR_VFP double iar_sqrt_59c800(double x)
{
    if (__builtin_isless(x, 0.0)) {
        union { double d; uint64_t u; } bits = { .d = x };

        bits.u = (bits.u & 0xffffffffull) | ((uint64_t)0x7fffffffu << 32);
        audio_uart_float_domain_error_439ca4();
        return bits.d;
    }
    return __builtin_elementwise_sqrt(x);
}
