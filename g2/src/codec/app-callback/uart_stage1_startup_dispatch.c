/* SPDX-License-Identifier: MIT
 * Unseeded stage-1 startup dispatcher at 0x100001bc, recovered directly
 * from native instructions. The lower initializers at 0x100001fc,
 * 0x10001dd8, 0x10001378 and 0x100002c8 remain distinct bodies.
 */
#include <stdint.h>
#include "uart_stage1_state.h"

extern void gx8002_uart_stage1_initialize_hardware(void);
extern void gx8002_uart_stage1_initialize_data(void);
extern void gx8002_uart_stage1_initialize_runtime(void);
extern void gx8002_uart_stage1_clear_bss(void);
extern void gx8002_uart_stage1_handshake(void);
extern uint32_t gx8002_uart_stage1_get_char(void);
extern void gx8002_uart_stage1_start_application(void);

uint32_t gx8002_uart_stage1_get_stored_id(void)
{
    return gx8002_uart_stage1_state.boot_info[0];
}

void gx8002_uart_stage1_startup_dispatch(void)
{
    gx8002_uart_stage1_initialize_hardware();
    gx8002_uart_stage1_initialize_data();
    gx8002_uart_stage1_initialize_runtime();
    gx8002_uart_stage1_clear_bss();
    if (gx8002_uart_stage1_get_stored_id() != 0) return;
    volatile uint8_t *const stage_flags = gx8002_uart_stage1_state.flags;
    stage_flags[0] = 2;
    gx8002_uart_stage1_handshake();
    while ((gx8002_uart_stage1_get_char() & 0xffu) != 'S') { }
    stage_flags[1] = 2;
    gx8002_uart_stage1_start_application();
}
