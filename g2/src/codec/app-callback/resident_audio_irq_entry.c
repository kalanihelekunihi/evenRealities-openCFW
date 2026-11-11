/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10025e48, the audio-in IRQ handler registered by
 * gx8002_resident_request_irq_2553c(2, handler, 0). The IRQ dispatcher
 * calls it as handler(irq, data); it returns 0.
 *
 * The C core takes the two values the stock body keeps in r0 and r4 on
 * its "status bit disabled" paths. They are not inputs from the caller:
 * the stock computes r0 = (enable >> 18) & 1 or (status >> 18) & 1 and
 * branches only when it is 0, and computes r4 = enable & 1 and branches
 * only when it is 0 (0x10025e70..0x10025e84, 0x10025f00..0x10025f08).
 * Both are therefore 0 where they are used. The former assembly bridge
 * forwarded the caller's r0/r4 instead.
 */
#include <stdint.h>

extern void gx8002_resident_audio_irq_core_25e48(uint32_t ambient_r0,
                                                 uint32_t ambient_r4);

/* Stock 0x10025E48 (gx8002_audio_irq) */
int32_t gx8002_resident_audio_irq_25e48(void)
{
    gx8002_resident_audio_irq_core_25e48(0u, 0u);
    return 0;
}
