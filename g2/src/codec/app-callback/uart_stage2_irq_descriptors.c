/* SPDX-License-Identifier: MIT
 * Stage-2 chained transfer descriptor writer at 0x10003f1c.
 * Each descriptor is six words (24 bytes). The native source reads
 * base words 0, 1, and 3; base word 2 is not an input contract.
 */
#include <stdint.h>

extern uint32_t gx8002_uart_stage2_address_mask_29c0(uint32_t address);

void gx8002_uart_stage2_irq_descriptors_3f1c(const uint32_t *base,
                                               volatile uint32_t *output,
                                               int32_t count,
                                               int32_t bytes,
                                               uint8_t mode)
{
    const uint32_t scales[4] = {0xfffu, 0xf001u, 0, 0};
    const uint32_t control = base[3];
    const uint32_t address_step = (uint32_t)mode *
        scales[(control & 0x3ffu) >> 9];
    const uint32_t buffer_step = (uint32_t)mode *
        scales[(control & 0xffu) >> 7];
    uint32_t address_offset = 0;
    uint32_t buffer_offset = 0;
    volatile uint32_t *last = output;
    if (count >= 2) {
        for (int32_t i = 0; i < count - 1; ++i) {
            volatile uint32_t *entry = output + (uint32_t)i * 6u;
            entry[0] = base[0] + address_offset;
            entry[1] = base[1] + buffer_offset;
            entry[2] = gx8002_uart_stage2_address_mask_29c0(
                (uint32_t)(uintptr_t)(entry + 6));
            entry[3] = control;
            entry[4] = 0xfffu;
            address_offset += address_step;
            buffer_offset += buffer_step;
        }
        last = output + (uint32_t)(count - 1) * 6u;
    }
    last[0] = base[0] + address_offset;
    last[1] = base[1] + buffer_offset;
    last[2] = 0;
    last[3] = control & UINT32_C(0xe7ffffff);
    const int32_t remainder = bytes % 0xfff;
    last[4] = remainder == 0 ? 0xfffu : (uint32_t)remainder;
}
