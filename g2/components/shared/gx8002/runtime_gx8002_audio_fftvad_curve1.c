/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Recovered package 0xdbbc. Preserve two independent full-word updates. */
int open_cfw_gx8002_audio_fftvad_curve1(unsigned short a,unsigned short b)
{
    if (a>3072u || b>17920u) return -1;
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0xa0a00184u;
    union { uint32_t word; struct { uint32_t low:16,high:16; } fields; } value;
    value.word=*control;
    value.fields.low=a;
    *control=value.word;
    value.word=*control;
    value.fields.high=b;
    *control=value.word;
    return 0;
}
