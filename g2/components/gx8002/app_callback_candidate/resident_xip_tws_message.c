/* SPDX-License-Identifier: MIT
 * Native XIP 0x1020b250 is an exact NUL-terminated TWS diagnostic
 * format consumed by SRAM callback 0x100263dc. Semantic source data,
 * with final XIP placement left to the image linker.
 */
#include <stdint.h>

const uint8_t gx8002_xip_tws_message_buffer_1020b250[] =
    "[LVP_TWS]Ctx:%d, Vad:%d, Ns:%d, R:%d\n";
