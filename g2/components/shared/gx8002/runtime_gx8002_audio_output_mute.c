/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef union {
    uint32_t word;
    struct { unsigned low:9,mute:1,high:22; } output;
    struct { unsigned low:11,mute11:1,middle:3,mute15:1,high:16; } control;
} mute_word;
/* Preserve three separate word RMWs and the unconditional halfword status1.
 * Unlike fixed-source controls, this internal callback dereferences its handle. */
int open_cfw_gx8002_aout_set_mute(void *handle, int mute)
{
    volatile uint32_t *base=(volatile uint32_t *)0xa0b00000u;
    unsigned enabled=mute!=0;
    mute_word edit;
    edit.word=base[1];edit.output.mute=enabled;base[1]=edit.word;
    edit.word=base[5];edit.control.mute11=enabled;base[5]=edit.word;
    edit.word=base[5];edit.control.mute15=enabled;base[5]=edit.word;
    *(volatile uint16_t *)((uintptr_t)handle+16)=1;
    return 0;
}
/* Stock getter sign-extends the cached halfword. It does not read MMIO. */
int open_cfw_gx8002_aout_get_mute(void *handle)
{
    return *(volatile int16_t *)((uintptr_t)handle+16);
}
