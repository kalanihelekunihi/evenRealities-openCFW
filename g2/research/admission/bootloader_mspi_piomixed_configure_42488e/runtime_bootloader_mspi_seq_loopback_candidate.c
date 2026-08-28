/* SPDX-License-Identifier: BSD-3-Clause */
#include <stdint.h>

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_seq_loopback_424978(void)
{
    __asm__ volatile(
        "ldr.w r1, [r0, #0x830]\n"
        "adds r1, r1, #1\n"
        "str r1, [r0, #0x20]\n"
        "movs r1, #0\n"
        "str r1, [r0, #0x1c]\n"
        "movs r1, #1\n"
        "strb.w r1, [r0, #0x834]\n"
        "movs r1, #0x40\n"
        "ldr r0, [r0, #4]\n"
        "ldr.w r2, [pc, #0x814]\n"
        "adds.w r2, r2, r0, lsl #12\n"
        "str.w r1, [r2, #0x2b4]\n"
        "bx lr\n");
}
#else
typedef struct open_cfw_mspi_seq_loopback_state {
    uint32_t module;
    uint32_t transaction_interrupt;
    uint32_t last_completed_index;
    uint32_t last_programmed_index;
    uint8_t transfer_complete;
} open_cfw_mspi_seq_loopback_state;

typedef void (*open_cfw_mspi_seq_loopback_write_fn)(void *context,
                                                    uint32_t address,
                                                    uint32_t value);

void open_cfw_bootloader_mspi_seq_loopback_424978(
    open_cfw_mspi_seq_loopback_state *state, void *context,
    open_cfw_mspi_seq_loopback_write_fn write_reg)
{
    state->last_completed_index = state->last_programmed_index + 1U;
    state->transaction_interrupt = 0U;
    state->transfer_complete = 1U;
    write_reg(context, 0x400602B4U + state->module * 0x1000U, 0x40U);
}
#endif
