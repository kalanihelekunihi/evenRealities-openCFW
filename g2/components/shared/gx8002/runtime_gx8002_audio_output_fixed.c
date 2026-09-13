/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Internal callback ABI includes an unused first handle argument. */
int open_cfw_gx8002_aout_set_fixed_src(int handle, short value)
{
    (void)handle;
    volatile uint32_t *reg=(volatile uint32_t *)0xa0b00010u;
    *reg=*reg|0x80000000u;
    union { uint32_t word; struct { unsigned payload:24, upper:8; } bits; } edit;
    edit.word=*reg;
    edit.bits.payload=(uint32_t)(uint16_t)value<<8;
    *reg=edit.word;
    return 0;
}
uint32_t open_cfw_gx8002_aout_get_sdc_addr(int handle)
{
    (void)handle;
    return *(volatile uint32_t *)0xa0b80010u;
}
