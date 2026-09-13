/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef struct {
    uint32_t frames:7, reserved0:17, zcr_bypass:1, bit25:1;
    uint32_t reserved1:4, bit30:1, bypass:1;
} fftvad_control;
typedef struct { uint32_t reserved0:16, start:1, finish:1, reserved1:14; } fftvad_interrupt;
/* Recovered package 0xdafc. Preserve separate status-clear writes and
 * distinguish raw low-bit enable fields from boolean bypass fields. */
int open_cfw_gx8002_audio_fftvad_enable(unsigned int vad_enable,unsigned int zcr_enable,unsigned int frame_num)
{
    volatile fftvad_control *control=(volatile fftvad_control *)(uintptr_t)0xa0a00158u;
    volatile fftvad_interrupt *irq=(volatile fftvad_interrupt *)(uintptr_t)0xa0a00100u;
    volatile uint32_t *clear=(volatile uint32_t *)(uintptr_t)0xa0a00104u;
    control->frames=frame_num?(uint8_t)(frame_num-1u):0;
    control->zcr_bypass=!zcr_enable;
    *clear=1u<<16;
    *clear=1u<<17;
    irq->start=1;
    irq->finish=1;
    control->bit25=vad_enable;
    control->bit30=vad_enable;
    control->bypass=!vad_enable;
    return 0;
}
