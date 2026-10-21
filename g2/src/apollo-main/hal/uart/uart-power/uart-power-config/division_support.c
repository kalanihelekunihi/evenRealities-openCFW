/* SPDX-License-Identifier: MIT */
/* Native Apollo Main unsigned quotient/remainder contract 0x47cc60..0x47ce90.
 * R1:R0 numerator,R3:R2 denominator; quotient R1:R0,remainder R3:R2.
 * Zero divisor reaches native no-op 0x4d2b98 and preserves numerator;
 * remainder registers remain zero. Named ARM instructions implement AAPCS. */
#include <stdint.h>

__attribute__((used,noinline)) static void opencfw_uart_udivmod64_words(
    uint32_t nlo,uint32_t nhi,uint32_t dlo,uint32_t dhi,uint32_t *result)
{
    if((dlo|dhi)==0u){result[0]=nlo;result[1]=nhi;result[2]=0u;result[3]=0u;return;}
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

__attribute__((naked)) void __aeabi_uldivmod(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "sub sp, #24\n"
        "add r4, sp, #4\n"
        "str r4, [sp, #0]\n"
        "bl opencfw_uart_udivmod64_words\n"
        "ldmia r4!, {r0, r1, r2, r3}\n"
        "add sp, #24\n"
        "pop {r4, pc}\n");
}
