/* SPDX-License-Identifier: MIT */
#include <stdint.h>
static inline void pulse(volatile uint32_t *reg)
{
    *reg=*reg|2u;
    *reg=*reg&~2u;
}
/* Recovered serial DAC programming sequence. Constants are command words,
 * not executable data. The source switch replaces the stock jump table. */
void open_cfw_gx8002_aout_set_lodac(void)
{
    volatile uint32_t *base=(volatile uint32_t *)0xa0b00000u;
    volatile uint32_t *reg=base+10;
    *reg=*reg|1u;
    pulse(reg);
    pulse(reg);
    uint32_t command;
    switch ((base[1]>>4)&7u) {
    case 1: command=0x985; break;
    case 2: command=0x885; break;
    case 3: command=0xb85; break;
    case 4: command=0xa05; break;
    case 5: command=0x905; break;
    case 6: command=0x805; break;
    case 7: command=0xe05; break;
    default: command=0xa85; break;
    }
    *reg=command; pulse(reg);
    *reg=9; pulse(reg);
    uint32_t level=(base[9]<<4)&~31u;
    *reg=level|5; pulse(reg);
    *reg=0x3765; pulse(reg);
    *reg=level|21; pulse(reg);
    *reg=0x3765; pulse(reg);
    *reg=0x2385; pulse(reg);
}
