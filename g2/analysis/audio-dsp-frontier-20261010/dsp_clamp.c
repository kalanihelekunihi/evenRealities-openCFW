#include <stdint.h>

/* Stock 0x59188e: d0=value, d1=lower, d2=upper, result in d0.
 * GCC lowers ordinary C comparisons to VCMPE, which changes FPSCR IOC for
 * quiet NaNs. This narrow inline assembly retains stock VCMP semantics.
 */
static inline int stock_less(double a, double b) {
    int less;
    __asm__ volatile (
        "vcmp.f64 %P1, %P2\n\t"
        "vmrs APSR_nzcv, FPSCR\n\t"
        "ite mi\n\t"
        "movmi %0, #1\n\t"
        "movpl %0, #0"
        : "=r"(less) : "w"(a), "w"(b) : "cc"
    );
    return less;
}

double g2_audio_dsp_clamp(double value, double lower, double upper) {
    if (stock_less(value, lower)) return lower;
    if (stock_less(upper, value)) return upper;
    return value;
}
