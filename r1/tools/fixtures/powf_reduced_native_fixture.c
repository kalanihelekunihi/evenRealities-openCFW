#include <stdint.h>
/* Verification-only adapter: native core returns through its original frame.
 * This is not a reconstructed provider and is excluded from source runtime. */
__attribute__((naked)) float r1_powf_reduced(uint32_t x __attribute__((unused)),int32_t adjustment __attribute__((unused)),float base __attribute__((unused)),float exponent __attribute__((unused)),float sign __attribute__((unused)))
{
 __asm__ volatile("push {r4,lr}\n\tvpush {d8-d10}\n\tvmov.f32 s16,s2\n\tvmov.f32 s2,#1.0\n\tmov r3,#0\n\tvmov s19,r3\n\tmov r2,r1\n\tmov r4,#0xff000000\n\tb.w r1_stock_powf_reduced");
}
