/* SPDX-License-Identifier: MIT
 * UART boot stage-1 initialized data, with the values of the stock image
 * (firmware_codec.bin g2-2.2.6.10 stage-1 offsets 0x2004..0x2017 and
 * 0x2274). Placement: see uart_stage1_state.h and link/g2-codec-a.ld.
 */
#include "uart_stage1_state.h"

__attribute__((section(".stage1.state"), used))
volatile struct gx8002_uart_stage1_state gx8002_uart_stage1_state = {
    .flags = {1, 1, 0, 0},
    .boot_info = {8, 0},             /* non-zero until a UART boot is seen */
    .host_word = 115200,
    .uart_base = UINT32_C(0xa0100000),
};

__attribute__((section(".stage1.data.dma_base"), used))
volatile uint32_t gx8002_uart_stage1_dma_base = UINT32_C(0xa1000000);
