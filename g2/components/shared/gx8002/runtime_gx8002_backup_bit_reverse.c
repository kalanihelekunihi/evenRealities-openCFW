/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Recovered packed-Q15 swap leaf at package 0x48164.
 * Caller supplies the descriptor's positive, even table-entry count.
 * Volatile accesses preserve the stock table/sample read and write order. */
void open_cfw_gx8002_backup_bit_reverse(void *samples,unsigned entries,
                                      const volatile uint16_t *table)
{
    unsigned pairs=(entries+1u)>>1;
    do {
        unsigned second=table[1]>>1;
        unsigned first=table[0]>>1;
        volatile uint32_t *b=(volatile uint32_t *)((uint8_t *)samples+second);
        volatile uint32_t *a=(volatile uint32_t *)((uint8_t *)samples+first);
        uint32_t bv=*b,av=*a;
        table+=2;
        *a=bv;
        *b=av;
    } while (--pairs);
}
