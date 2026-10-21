#include <stdint.h>

/* Nonzero arithmetic is the unchanged pinned LLVM compiler-rt C provider.
 * Stock Arm runtime zero-divisor results are deliberately supplied here. */
extern uint64_t __udivmoddi4(uint64_t,uint64_t,uint64_t *);
uint64_t r1_runtime_udivmod(uint64_t numerator,uint64_t denominator,uint64_t *remainder)
{
    if (!denominator) {
        if (remainder) *remainder=numerator;
        return UINT64_MAX;
    }
    return __udivmoddi4(numerator,denominator,remainder);
}
uint64_t r1_runtime_sdivmod(uint64_t numerator,uint64_t denominator,uint64_t *remainder)
{
    uint32_t negative_n=(uint32_t)(numerator>>63),negative_d=(uint32_t)(denominator>>63);
    uint64_t magnitude_n=negative_n ? UINT64_C(0)-numerator : numerator;
    uint64_t magnitude_d=negative_d ? UINT64_C(0)-denominator : denominator;
    uint64_t rest,quotient=r1_runtime_udivmod(magnitude_n,magnitude_d,&rest);
    if (remainder) *remainder=negative_n ? UINT64_C(0)-rest : rest;
    return negative_n!=negative_d ? UINT64_C(0)-quotient : quotient;
}

/* EABI returns quotient in r0:r1 and remainder in r2:r3, unlike a normal C
 * aggregate return. This C-compilable inline-assembly glue marshals only that
 * register/stack interface; it contains no original firmware instructions. */
__attribute__((naked)) void __aeabi_uldivmod(void)
{
    __asm__ volatile (
        "push {r4, r5, r12, lr}\n"
        "sub sp, sp, #16\n"
        "add r4, sp, #8\n"
        "str r4, [sp]\n"
        "bl r1_runtime_udivmod\n"
        "ldrd r2, r3, [sp, #8]\n"
        "add sp, sp, #16\n"
        "pop {r4, r5, r12, pc}\n");
}
__attribute__((naked)) void __aeabi_ldivmod(void)
{
    __asm__ volatile (
        "push {r4, lr}\n"
        "sub sp, sp, #16\n"
        "add r4, sp, #8\n"
        "str r4, [sp]\n"
        "bl r1_runtime_sdivmod\n"
        "ldrd r2, r3, [sp, #8]\n"
        "mov r12, r3\n"
        "mov lr, r0\n"
        "add sp, sp, #16\n"
        "pop {r4, pc}\n");
}

static uint32_t arm_lsl(uint32_t value,uint32_t count)
{ count&=255u;return count<32 ? value<<count : 0; }
static uint32_t arm_lsr(uint32_t value,uint32_t count)
{ count&=255u;return count<32 ? value>>count : 0; }
/* Preserve the actual register-shift behavior for all 32-bit count words,
 * including values outside the C/compiler-rt shift precondition [0,63]. */
uint64_t __aeabi_llsl(uint64_t value,uint32_t count)
{
    uint32_t low=(uint32_t)value,high=(uint32_t)(value>>32);
    if (!(count&UINT32_C(0x80000000)) && count>=32) {
        high=arm_lsl(low,count-32u);low=0;
    } else {
        high=arm_lsl(high,count)|arm_lsr(low,32u-count);
        low=arm_lsl(low,count);
    }
    return ((uint64_t)high<<32)|low;
}
uint64_t __aeabi_llsr(uint64_t value,uint32_t count)
{
    uint32_t low=(uint32_t)value,high=(uint32_t)(value>>32);
    if (!(count&UINT32_C(0x80000000)) && count>=32) {
        low=arm_lsr(high,count-32u);high=0;
    } else {
        low=arm_lsr(low,count)|arm_lsl(high,32u-count);
        high=arm_lsr(high,count);
    }
    return ((uint64_t)high<<32)|low;
}
