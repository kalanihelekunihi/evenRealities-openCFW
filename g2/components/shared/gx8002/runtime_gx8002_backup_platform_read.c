/* SPDX-License-Identifier: MIT */
/* Recovered getter at backup package 0x3c81c. Caller records must provide the
 * halfword/word alignment of the original accesses. Volatile preserves IO
 * and output ordering, including the two final reads before case-0 stores. */
#include <stdint.h>
#define REG(a) (*(volatile uint32_t *)(a))
/* Explicit narrow stores avoid backend zero-extension before a store that
 * already truncates. These are readable target instructions, not binary data. */
#define STORE_BYTE(o,v) __asm__ volatile("st.b %0, (%1, %2)" :: "r"((uint32_t)(v)), "r"(record), "i"(o) : "memory")
#define STORE_HALF(o,v) __asm__ volatile("st.h %0, (%1, %2)" :: "r"((uint32_t)(v)), "r"(record), "i"(o) : "memory")
#define WORD(o) (*(volatile uint32_t *)((volatile uint8_t *)record+(o)))
int open_cfw_gx8002_platform_read(unsigned operation, volatile void *record)
{
    switch (operation) {
    case 0: {
        STORE_HALF(0,REG(0xa0000004u));
        STORE_HALF(2,REG(0xa0000008u));
        STORE_HALF(4,REG(0xa000000cu));
        STORE_HALF(6,REG(0xa0000010u));
        STORE_HALF(8,REG(0xa0000014u));
        STORE_HALF(10,REG(0xa0000018u));
        uint32_t penultimate=REG(0xa000001cu);
        uint32_t last=REG(0xa0000020u);
        STORE_HALF(12,penultimate);
        STORE_HALF(14,last);
        return 0;
    }
    case 1: WORD(0)=REG(0xa0000024u); break;
    case 2: WORD(0)=REG(0xa0000028u); break;
    case 3: WORD(0)=REG(0xa000002cu)&15u; break;
    case 4: WORD(0)=REG(0xa0000034u)&15u; break;
    case 5:
        STORE_BYTE(0,REG(0xa0010058u)&1u);
        WORD(4)=REG(0xa001005cu);
        break;
    case 6: WORD(0)=REG(0xa0000030u); break;
    case 7: {
        uint32_t packed=REG(0xa0000048u);
        register uint32_t enabled __asm__("r0")=REG(0xa0000040u);
        /* In-place mask keeps this value in a short-encoding register. */
        __asm__("andi %0, %0, 1" : "+r"(enabled));
        STORE_BYTE(0,enabled);
        STORE_BYTE(1,REG(0xa0000044u));
        STORE_HALF(4,REG(0xa000004cu));
        STORE_BYTE(2,packed&15u);
        STORE_BYTE(3,(packed>>4)&15u);
        STORE_BYTE(6,REG(0xa0000050u));
        STORE_BYTE(7,REG(0xa0000054u));
        break;
    }
    case 8: WORD(0)=REG(0xa0000038u); break;
    case 9: WORD(0)=REG(0x20017398u); break;
    default: return -1;
    }
    return 0;
}
