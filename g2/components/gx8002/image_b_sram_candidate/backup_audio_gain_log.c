/* SPDX-License-Identifier: MIT
 * Image-B 0x10003254: native dmic gain diagnostic. Values and format text
 * are authenticated at 0x100128fc..0x10012959 in the pinned image-B corpus.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *, ...);
static const uint32_t gains_db[9] = {6u, 12u, 18u, 24u, 30u,
                                     36u, 42u, 48u, 54u};

void gx8002_image_b_audio_gain_log_10003254(void)
{
    gx8002_image_b_heap_log_10009934("[AB]dmic          [%d Channel]\n", 2);
    uint32_t state = *(volatile uint16_t *)(uintptr_t)UINT32_C(0x200167f0);
    uint32_t index = ((state & 0x1ffu) >> 6) - 1u;
    gx8002_image_b_heap_log_10009934(
        "[AB]dmic Ain_gain:[%d dB]\n", index < 9u ? gains_db[index] : 0u);
}
