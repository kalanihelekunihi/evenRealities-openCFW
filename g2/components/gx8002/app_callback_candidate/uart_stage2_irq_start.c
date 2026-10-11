/* SPDX-License-Identifier: MIT
 * Stage-2 UART IRQ setup 0x10003024. Native r1/r2 at entry carry
 * buffer and transfer byte count from 0x10002f34; the mode block follows
 * direct stores at 0x10003042..86. Hardware setup 0x10004340 and
 * callback 0x10002f98 remain separately owned source obligations.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_irq_allocate_41b8(void);
extern uint32_t gx8002_uart_stage2_mask_index_2fb4(uint32_t value,
                                                     const uint32_t *fallback,
                                                     uint32_t explicit_value);
extern void gx8002_uart_stage2_irq_set_callback_432c(uint32_t slot,
                                                       uintptr_t callback,
                                                       uintptr_t context);
extern void gx8002_uart_stage2_irq_handler_2f98(
    volatile uint32_t *descriptor);
extern int32_t gx8002_uart_stage2_irq_hardware_setup_4340(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode);

uint32_t gx8002_uart_stage2_uart_irq_setup_3024(
    volatile uint32_t *descriptor, uint32_t buffer, uint32_t transfer_bytes)
{
    const uint32_t uart_base = descriptor[1];
    const int32_t slot = gx8002_uart_stage2_irq_allocate_41b8();
    if (slot < 0) return UINT32_MAX;
    descriptor[0x68 / 4] = (uint32_t)slot;
    const uint32_t mask = descriptor[0x34 / 4];
    uint32_t mode[12] = {
        0,
        gx8002_uart_stage2_mask_index_2fb4(mask,
                                      (const uint32_t *)&descriptor[0x38 / 4], 0),
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        2,
    };
    if (descriptor[0] == 0) mode[3] = 6;
    else if (descriptor[0] == 1) mode[3] = 4;
    else return UINT32_MAX;
    mode[6] = gx8002_uart_stage2_mask_index_2fb4(mask,
                                      (const uint32_t *)&descriptor[0x38 / 4], 0);
    gx8002_uart_stage2_irq_set_callback_432c((uint32_t)slot,
        (uintptr_t)&gx8002_uart_stage2_irq_handler_2f98,
        (uintptr_t)descriptor);
    (void)gx8002_uart_stage2_irq_hardware_setup_4340(buffer, uart_base,
                    transfer_bytes, (uint32_t)slot, mode);
    return 0;
}
