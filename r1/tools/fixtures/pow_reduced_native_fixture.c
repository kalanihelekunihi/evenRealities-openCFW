#include <stdint.h>
/* Verification only. Recreate the original 192-byte pow frame and handoff;
 * this adapter and native target do not satisfy the missing C core provider. */
__attribute__((naked)) double r1_pow_reduced(uint64_t absolute __attribute__((unused)),uint64_t exponent __attribute__((unused)),uint64_t sign __attribute__((unused)))
{
 __asm__ volatile("push.w {r4,r5,r6,r7,r8,r10,r11,lr}\n\tvpush {d0-d1}\n\tvpush {d8-d14}\n\tsub sp,sp,#88\n\tstrd r0,r1,[sp,#56]\n\tstrd r0,r1,[sp,#144]\n\tstrd r2,r3,[sp,#152]\n\tvmov d0,r0,r1\n\tmov r6,r1\n\tmov r10,r0\n\tmov r4,r3\n\tbic r8,r3,#0x80000000\n\tvldr d8,[sp,#192]\n\tmov r0,#0\n\tmovw r1,#0\n\tmovt r1,#0x3ff0\n\tmov r11,r1\n\tvmov d9,r0,r1\n\tmovt r1,#0x7ff0\n\tvmov d10,r0,r1\n\tb.w r1_stock_pow_reduced");
}
