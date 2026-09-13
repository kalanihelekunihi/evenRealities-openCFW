/* SPDX-License-Identifier: MIT */
#include <stdint.h>
typedef struct {
    uint32_t reserved:28, hamming:1, bit29:1, bit30:1, bypass:1;
} logfbank_control;
/* Recovered package 0xdab8. Enable bits use the raw low bit, whereas bypass
 * uses the inverse boolean value. Each update remains a separate word RMW. */
int open_cfw_gx8002_audio_logfbank_enable(unsigned int module_enable,unsigned int hmt_enable)
{
    volatile logfbank_control *control=(volatile logfbank_control *)(uintptr_t)0xa0a00180u;
    control->hamming=hmt_enable;
    control->bit29=module_enable;
    control->bit30=module_enable;
    control->bypass=!module_enable;
    return 0;
}
