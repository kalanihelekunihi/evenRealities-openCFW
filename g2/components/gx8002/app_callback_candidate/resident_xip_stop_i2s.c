/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020913c..0x102091a4 I2S shutdown. Ordered
 * application-state, shared GPIO byte, padmux, AOUT and final clears.
 */
#include <stdint.h>
#include "resident_sample_product_data.h"

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern int32_t gx8002_xip_padmux_set_102065dc(uint32_t, uint32_t);
extern uint32_t gx8002_xip_audio_out_free_102053b0(uint32_t);
extern uint32_t gx8002_xip_audio_out_exit_10205574(void);

static volatile uint32_t *const application =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e8c4);
static volatile uint8_t *const shared_channel =
    (volatile uint8_t *)(void *)&gx8002_sample_registration_26d30;

void gx8002_xip_stop_i2s_1020913c(void)
{
    (void)gx8002_xip_tws_publish_10206c24(
        "[YW_APP]:%s, %d\n", "close_i2s", 307);
    if (application[5] == 0u) return;
    application[5] = 0u;
    shared_channel[4] = 0u;
    (void)gx8002_xip_padmux_set_102065dc(7u, 1u);
    (void)gx8002_xip_padmux_set_102065dc(8u, 1u);
    (void)gx8002_xip_padmux_set_102065dc(9u, 1u);
    (void)gx8002_xip_padmux_set_102065dc(10u, 1u);
    if (application[1] != UINT32_MAX) {
        (void)gx8002_xip_tws_publish_10206c24(
            "[YW_APP]:%s, %d, handle = %d\n",
            "close_i2s", 329, (int32_t)application[1]);
        (void)gx8002_xip_audio_out_free_102053b0(application[1]);
        (void)gx8002_xip_audio_out_exit_10205574();
        application[1] = UINT32_MAX;
    }
    application[6] = 0u;
    application[7] = 0u;
    application[0] = 0u;
}
