/* SPDX-License-Identifier: MIT
 * Native CASE 0x08000210 unsigned 64-bit quotient/remainder helper.
 * AAPCS input is R1:R0 dividend and R3:R2 divisor; quotient returns in
 * R1:R0 and remainder in R3:R2. The divide-by-zero native behavior is
 * retained: quotient all ones, remainder equal to dividend.
 */
#include <stdint.h>

__attribute__((used,noinline)) static void case_boot_udivmod64_words(
    uint32_t nlo,uint32_t nhi,uint32_t dlo,uint32_t dhi,uint32_t *result)
{
    uint32_t rlo=0u,rhi=0u,qlo=0u,qhi=0u;
    for(int32_t bit=63;bit>=0;--bit){
        uint32_t input=bit>=32?(nhi>>(bit-32))&1u:(nlo>>bit)&1u;
        uint32_t carry=rhi>>31;
        rhi=(rhi<<1)|(rlo>>31);
        rlo=(rlo<<1)|input;
        qhi=(qhi<<1)|(qlo>>31);
        qlo<<=1;
        if(carry!=0u || rhi>dhi || (rhi==dhi && rlo>=dlo)){
            uint32_t borrow=rlo<dlo;
            rlo-=dlo;
            rhi=rhi-dhi-borrow;
            qlo|=1u;
        }
    }
    result[0]=qlo;result[1]=qhi;result[2]=rlo;result[3]=rhi;
}

/* Stock 0x08000210 (case_boot_udivmod64) */
__attribute__((naked)) void case_boot_udivmod64(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "sub sp, #24\n"
        "add r4, sp, #4\n"
        "str r4, [sp, #0]\n"
        "bl case_boot_udivmod64_words\n"
        "ldmia r4!, {r0, r1, r2, r3}\n"
        "add sp, #24\n"
        "pop {r4, pc}\n");
}
