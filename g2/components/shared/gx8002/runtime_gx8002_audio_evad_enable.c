/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <gx_audio_in/gx_audio_in_v2.h>
typedef struct {
    uint32_t window:16, reserved0:8, bit24:1, zcr_bypass:1;
    uint32_t reset:1, vad_bypass:1, bit28:1, reserved1:2, state_valid:1;
} evad_control;
typedef struct { uint32_t interval:16, offset:8, reserved:8; } evad_timing;
typedef struct {
    uint32_t reserved0:18, sadc:1, pdm:1, i2s:1, reserved1:11;
} evad_interrupt;
_Static_assert(sizeof(GX_AUDIO_IN_EVAD)==12,"EVAD aggregate ABI");

/* Recovered package 0xd988. Valid source precondition: exactly SADC/PDM/I2S.
 * Invalid sources return -1 instead of the stock null MMIO access.
 * Reset completion is polled without a timeout, as in the original. */
int open_cfw_gx8002_audio_evad_enable(GX_AUDIO_IN_SOURCE source,GX_AUDIO_IN_EVAD config)
{
    volatile evad_interrupt *irq=(volatile evad_interrupt *)(uintptr_t)0xa0a00100u;
    volatile evad_control *control;
    if (source==AUDIO_IN_SADC) {
        control=(volatile evad_control *)(uintptr_t)0xa0a00010u;
        irq->sadc=config.evad_enable;
    } else if (source==AUDIO_IN_PDM) {
        control=(volatile evad_control *)(uintptr_t)0xa0a00030u;
        control->bit28=0;
        irq->pdm=config.evad_enable;
    } else if (source==AUDIO_IN_I2S) {
        control=(volatile evad_control *)(uintptr_t)0xa0a00050u;
        control->bit28=0;
        irq->i2s=config.evad_enable;
    } else return -1;
    control->reset=1;
    while (*(volatile uint32_t *)((uintptr_t)control+20u)) {}
    control->reset=0;
    control->vad_bypass=!config.evad_enable;
    control->zcr_bypass=!config.zcr_enable;
    control->bit24=1;
    volatile uint32_t *words=(volatile uint32_t *)control;
    union { uint32_t word; evad_control fields; } value;
    value.word=words[0];
    value.fields.window=24576;
    words[0]=value.word;
    control->state_valid=config.state_valid_enable;
    union { uint32_t word; evad_timing fields; } timing;
    timing.word=words[1];
    timing.fields.offset=0;
    words[1]=timing.word;
    timing.word=words[1];
    timing.fields.interval=16;
    words[1]=timing.word;
    return 0;
}
