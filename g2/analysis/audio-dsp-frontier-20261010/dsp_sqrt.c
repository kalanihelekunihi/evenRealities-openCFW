#include <stdint.h>

/* Source candidate for stock 0x59c800. The absolute errno slot is supplied
 * by the state layout; the oracle binds it to authenticated RAM 0x20074f14.
 */
extern volatile uint32_t g2_audio_errno_slot;

double g2_audio_dsp_sqrt(double value) {
    int negative;
    __asm__ volatile (
        "vcmpe.f64 %P1, #0\n\t"
        "vmrs APSR_nzcv, FPSCR\n\t"
        "ite mi\n\t"
        "movmi %0, #1\n\t"
        "movpl %0, #0"
        : "=r"(negative) : "w"(value) : "cc"
    );
    if (negative) {
        union { uint64_t bits; double value; } result;
        result.value = value;
        result.bits = (result.bits & UINT64_C(0xffffffff)) |
                      UINT64_C(0x7fffffff00000000);
        g2_audio_errno_slot = 33;
        return result.value;
    }
    double result;
    __asm__ volatile ("vsqrt.f64 %P0, %P1" : "=w"(result) : "w"(value));
    return result;
}
