/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
extern void *memcpy(void *, const void *, size_t);
extern void open_cfw_gx8002_aout_play_check_idle(uint32_t, uint32_t);
extern void open_cfw_gx8002_aout_set_r1_frame_over_int_enable(uint32_t, uint32_t);
/* Reconstructed from stock e734 and pinned SDK aout_push_frame.
 * Configured byte stride at handle+25 must be nonzero. The stock uses
 * signed division after wrapping the inclusive address difference. */
int open_cfw_gx8002_aout_push_frame(void *handle, const void *frame)
{
    if (!frame) return -1;
    uint8_t *state=(uint8_t *)handle;
    memcpy(state+32,frame,8);
    uint32_t end=*(volatile uint32_t *)(state+36);
    uint32_t start=*(volatile uint32_t *)(state+32);
    uint32_t stride=*(const uint8_t *)(state+25);
    uint32_t count=(uint32_t)((int32_t)(end+1u-start)/(int32_t)stride);
    volatile uint32_t *sdc=(volatile uint32_t *)0xa0b80000u;
    (void)sdc[5];sdc[5]=start;
    end=*(volatile uint32_t *)(state+36);
    (void)sdc[6];sdc[6]=end;
    sdc[9]=(sdc[9]&0xff000000u)|(count&0xffffffu);
    sdc[11]=sdc[11]|2u;
    __asm__ volatile ("" ::: "memory");
    if (!state[26] && *(volatile uint32_t *)(state+44)) {
        *(volatile uint8_t *)(state+26)=1;
        open_cfw_gx8002_aout_play_check_idle(0xa0b00000u,1);
        open_cfw_gx8002_aout_set_r1_frame_over_int_enable(0xa0b00000u,1);
    }
    return 0;
}
