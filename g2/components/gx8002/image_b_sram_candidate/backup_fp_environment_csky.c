/* CK804EF floating-point environment bridge for pinned compiler-rt.
 *
 * The register addresses, rounding codes, and inexact operation follow the
 * C-SKY glibc hard-float port, sysdeps/csky/{bits/fenv.h,fpu_control.h} and
 * sysdeps/csky/fpu/fraiseexcpt.c (Mao Han, 2018 math-support patch).
 * LLVM compiler-rt fp_mode.h uses a different enum order, hence the mapping.
 * This unit reads live FCR state; it does not assume a default rounding mode.
 */
#include <stdint.h>

#if !defined(__CSKYABIV2__) || !defined(__csky_fpuv2__)
#error "The CK804EF hard-float FPUv2 register contract is required"
#endif

int __fe_getround(void)
{
    uint32_t fcr;
    __asm__ volatile("mfcr %0, cr<1, 2>" : "=a"(fcr));
    /* C-SKY: nearest, zero, up, down.  LLVM: nearest, down, up, zero. */
    static const unsigned char llvm_mode[4] = {0, 3, 2, 1};
    return llvm_mode[(fcr >> 24) & 3u];
}

int __fe_raise_inexact(void)
{
    volatile float one = 1.0f;
    volatile float three = 3.0f;
    volatile float quotient;
    /* The pinned glibc FPUv2 path raises inexact with 1 / 3.  Volatile
     * operands preserve a runtime FP division with this compiler version. */
    quotient = one / three;
    (void)quotient;
    return 0;
}
