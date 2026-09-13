/* SPDX-License-Identifier: MIT */
/* Recovered ten-operation platform register dispatcher at image-B 0x4e08c.
 * Caller records require the halfword/word alignment used by each operation.
 * Volatile loads preserve the repeated operation-9 input read. */
#include <stdint.h>
#define REG(a) (*(volatile uint32_t *)(a))
#define BYTE(o) (*(const volatile uint8_t *)((const volatile uint8_t *)record+(o)))
#define HALF(o) (*(const volatile uint16_t *)((const volatile uint8_t *)record+(o)))
#define WORD(o) (*(const volatile uint32_t *)((const volatile uint8_t *)record+(o)))
int open_cfw_gx8002_platform_config(unsigned operation, const volatile void *record)
{
    switch (operation) {
    case 0:
        for (unsigned i=0; i<8; ++i)
            REG(0xa0000004u+i*4)=HALF(i*2);
        break;
    case 1: REG(0xa0000024u)=WORD(0); break;
    case 2: REG(0xa0000028u)=WORD(0); break;
    case 3: REG(0xa000002cu)=WORD(0); break;
    case 4: REG(0xa0000034u)=WORD(0); break;
    case 5:
        REG(0xa0010058u)=BYTE(0)&1u;
        REG(0xa001005cu)=WORD(4);
        break;
    case 6: return -1;
    case 7: {
        unsigned packed=BYTE(3)<<4;
        packed |= BYTE(2);
        unsigned second=BYTE(1);
        unsigned first=BYTE(0);
        unsigned period=HALF(4);
        REG(0xa000004cu)=period;
        REG(0xa0000048u)=packed;
        REG(0xa0000044u)=second!=0;
        REG(0xa0000040u)=first!=0;
        break;
    }
    case 8: REG(0xa0000038u)=WORD(0); break;
    case 9:
        REG(0xa000003cu)=WORD(0)&1u;
        REG(0x20017398u)=WORD(0)&1u;
        break;
    default: return -1;
    }
    return 0;
}
