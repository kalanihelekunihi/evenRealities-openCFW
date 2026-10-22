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
 * g2-apollo-main-20 (-mfpu=fpv5-d16). */
#include <stdint.h>

#define IAR_VFP __attribute__((pcs("aapcs-vfp")))

extern void audio_uart_float_domain_error_439ca4(void); /* errno = EDOM (33) */

IAR_VFP double iar_sqrt_59c800(double x)
{
    uint32_t status;
    double result;

    __asm__ volatile("vcmpe.f64 %P1, #0.0\n\tvmrs %0, fpscr" : "=r"(status) : "w"(x));
    if ((status & 0x80000000u) != 0u) {
        union { double d; uint64_t u; } bits = { .d = x };

        bits.u = (bits.u & 0xffffffffull) | ((uint64_t)0x7fffffffu << 32);
        audio_uart_float_domain_error_439ca4();
        return bits.d;
    }
    __asm__("vsqrt.f64 %P0, %P1" : "=w"(result) : "w"(x));
    return result;
}
