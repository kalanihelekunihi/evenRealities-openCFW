/* SPDX-License-Identifier: MIT
 * Main MSPI command queue adapters at 0x4bfc5a, 0x4bfd62 and 0x4bfc86.
 * Layout follows the authenticated Main image and the bootloader HAL source.
 */
#include <stdint.h>

#define MAIN_MSPI_STATE_BASE UINT32_C(0x200523d8)
#define MSPI_STATE_STRIDE UINT32_C(0x8d0)
#define QUEUE_HANDLE_OFFSET UINT32_C(0x828)

typedef struct {
    uint32_t queue_size_half_units;
    uint32_t queue_buffer_address;
    uint8_t option;
    uint8_t padding[3];
} main_cmdq_config_t;

_Static_assert(sizeof(main_cmdq_config_t) == 12, "Main CMDQ config ABI");

extern uint32_t g2_main_cq_init_538d58(uint32_t, const void *, uint32_t *);
extern uint32_t g2_main_cq_disable_538e8c(uint32_t *);
extern uint32_t g2_main_cq_term_53909a(uint32_t *, uint32_t);

void g2_main_mspi_cq_init_4bfc5a(uint32_t module, uint32_t queue_size_input,
                                  uint32_t queue_buffer_address)
{
    main_cmdq_config_t config = {
        .queue_size_half_units = queue_size_input >> 1,
        .queue_buffer_address = queue_buffer_address,
        .option = 1u,
        .padding = {0u, 0u, 0u},
    };
    const uintptr_t slot = MAIN_MSPI_STATE_BASE + module * MSPI_STATE_STRIDE +
                           QUEUE_HANDLE_OFFSET;
    (void)g2_main_cq_init_538d58((module + 8u) & 0xffu, &config,
                                 (uint32_t *)slot);
}

uint32_t g2_main_mspi_cq_disable_4bfd62(uint32_t state_address)
{
    const uintptr_t queue = *(const volatile uint32_t *)(uintptr_t)
        (state_address + QUEUE_HANDLE_OFFSET);
    return g2_main_cq_disable_538e8c((uint32_t *)queue);
}

void g2_main_mspi_cq_term_4bfc86(uint32_t state_address)
{
    const uint32_t module = *(const volatile uint32_t *)(uintptr_t)
        (state_address + 4u);
    const uintptr_t slot = MAIN_MSPI_STATE_BASE + module * MSPI_STATE_STRIDE +
                           QUEUE_HANDLE_OFFSET;
    const uintptr_t queue = *(const volatile uint32_t *)slot;
    if (queue != 0u) {
        (void)g2_main_cq_term_53909a((uint32_t *)queue, 1u);
        *(volatile uint32_t *)slot = 0u;
    }
}
