/* SPDX-License-Identifier: MIT
 * UART boot stage-1 initialized data shared between stage-1 units. The
 * codec-a linker script places .stage1.state at 0x20002004 (D-bus view of
 * the stage-1 image offset 0x2004, loaded with the image); stage 2 reads
 * flags[1] (0x20002005) and host_word (0x20002010) at those addresses.
 */
#ifndef OPENCFW_UART_STAGE1_STATE_H
#define OPENCFW_UART_STAGE1_STATE_H
#include <stdint.h>

struct gx8002_uart_stage1_state {
    uint8_t flags[4];        /* 0x20002004: [0] stage-1 step, [1] stage-2 mode */
    uint32_t boot_info[2];   /* 0x20002008: boot device (0 = UART), UART select */
    uint32_t host_word;      /* 0x20002010: word sent by the host (baud) */
    uint32_t uart_base;      /* 0x20002014: active UART, set by bringup */
};
_Static_assert(sizeof(struct gx8002_uart_stage1_state) == 0x14, "stage-1 state ABI");

extern volatile struct gx8002_uart_stage1_state gx8002_uart_stage1_state;
/* DMA controller base used by announce_transfer/postamble (0x20002274). */
extern volatile uint32_t gx8002_uart_stage1_dma_base;
#endif
