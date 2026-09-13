/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Package 0xdf3c: PDM channel delay, identified by command270 diagnostic
 * and its direct call with index0/value1 at package0x12bc6.
 * Preserve the firmware's unsigned index wrapping and six-bit truncation. */
int open_cfw_gx8002_audio_channel_field(uint32_t index, uint32_t value)
{
    uintptr_t address = 0xa0a00000u + ((index + 10u) << 2);
    volatile uint32_t *reg = (volatile uint32_t *)address;
    union { uint32_t word; struct { unsigned low:10, field:6, high:16; } bits; } edit;
    edit.word = *reg;
    edit.bits.field = value;
    *reg = edit.word;
    return 0;
}
