/* SPDX-License-Identifier: MIT
 * Main CMDQ initializer at 0x538d58 and its source-owned 12-row resources.
 * Resource values were checked against Main 0x6c0f40 and bootloader source.
 */
#include <stddef.h>
#include <stdint.h>

#define MAIN_CMDQ_STATE_BASE UINT32_C(0x2006ef28)
#define CMDQ_STATE_STRIDE UINT32_C(0x2c)
#define CMDQ_MAGIC UINT32_C(0x01cdcdcd)

typedef struct {
    uint32_t option_register;
    uint32_t buffer_register;
    uint32_t reset_register_a;
    uint32_t reset_register_b;
    uint32_t control_register;
    uint32_t control_mask;
    uint32_t status_register;
    uint32_t option_value;
    uint32_t reset_value;
    uint32_t control_value;
} main_cmdq_resource_t;

typedef struct {
    uint32_t flags;
    uint32_t queue_buffer;
    uint32_t read_pointer;
    uint32_t write_pointer;
    uint32_t producer_pointer;
    uint32_t consumer_pointer;
    uint32_t queue_size_bytes;
    uint32_t current_index;
    uint32_t end_index;
    uint32_t interface_ops_address;
    uint32_t untouched_28;
} main_cmdq_state_t;

typedef struct {
    uint32_t queue_size_half_units;
    uint32_t queue_buffer_address;
    uint8_t option;
    uint8_t padding[3];
} main_cmdq_config_t;

_Static_assert(sizeof(main_cmdq_resource_t) == 0x28, "CMDQ resource row ABI");
_Static_assert(sizeof(main_cmdq_state_t) == 0x2c, "CMDQ state row ABI");
_Static_assert(offsetof(main_cmdq_state_t, interface_ops_address) == 0x24,
               "CMDQ ops field ABI");
_Static_assert(sizeof(main_cmdq_config_t) == 12, "CMDQ config ABI");

/* These are peripheral addresses and scalar masks. No stock image address is
 * retained in the source table; a final image linker places it anew. */
__attribute__((used, aligned(4), section(".main_cmdq_resources")))
const main_cmdq_resource_t g2_main_cmdq_resources[12] = {
    {0x40050228u,0x4005022cu,0x40050240u,0x40050244u,0x4005023cu,0x00008000u,0x40050230u,1u,4u,2u},
    {0x40051228u,0x4005122cu,0x40051240u,0x40051244u,0x4005123cu,0x00008000u,0x40051230u,1u,4u,2u},
    {0x40052228u,0x4005222cu,0x40052240u,0x40052244u,0x4005223cu,0x00008000u,0x40052230u,1u,4u,2u},
    {0x40053228u,0x4005322cu,0x40053240u,0x40053244u,0x4005323cu,0x00008000u,0x40053230u,1u,4u,2u},
    {0x40054228u,0x4005422cu,0x40054240u,0x40054244u,0x4005423cu,0x00008000u,0x40054230u,1u,4u,2u},
    {0x40055228u,0x4005522cu,0x40055240u,0x40055244u,0x4005523cu,0x00008000u,0x40055230u,1u,4u,2u},
    {0x40056228u,0x4005622cu,0x40056240u,0x40056244u,0x4005623cu,0x00008000u,0x40056230u,1u,4u,2u},
    {0x40057228u,0x4005722cu,0x40057240u,0x40057244u,0x4005723cu,0x00008000u,0x40057230u,1u,4u,2u},
    {0x400602a0u,0x400602a8u,0x400602c0u,0x400602c4u,0x400602b8u,0x00004000u,0x400602acu,1u,4u,8u},
    {0x400612a0u,0x400612a8u,0x400612c0u,0x400612c4u,0x400612b8u,0x00004000u,0x400612acu,1u,4u,8u},
    {0x400622a0u,0x400622a8u,0x400622c0u,0x400622c4u,0x400622b8u,0x00004000u,0x400622acu,1u,4u,8u},
    {0x400632a0u,0x400632a8u,0x400632c0u,0x400632c4u,0x400632b8u,0x00004000u,0x400632acu,1u,4u,8u},
};

uint32_t g2_main_cq_init_538d58(uint32_t interface_id,
                                  const void *configuration,
                                  uint32_t *handle_slot)
{
    const main_cmdq_config_t *const config = configuration;
    interface_id &= 0xffu;
    if (interface_id >= 12u)
        return 5u;
    if (config == NULL || config->queue_buffer_address == 0u ||
        handle_slot == NULL || config->queue_size_half_units < 2u)
        return 6u;

    volatile main_cmdq_state_t *const state =
        (volatile main_cmdq_state_t *)(uintptr_t)
        (MAIN_CMDQ_STATE_BASE + interface_id * CMDQ_STATE_STRIDE);
    if (state->flags & UINT32_C(0x01000000))
        return 7u;

    const main_cmdq_resource_t *const ops =
        &g2_main_cmdq_resources[interface_id];
    state->queue_size_bytes = config->queue_size_half_units << 3;
    state->queue_buffer = config->queue_buffer_address;
    state->write_pointer = config->queue_buffer_address;
    state->producer_pointer = config->queue_buffer_address;
    state->consumer_pointer = config->queue_buffer_address;
    state->read_pointer = config->queue_buffer_address +
                          (config->queue_size_half_units << 3);
    state->flags = (state->flags & UINT32_C(0xfd000000)) |
                   UINT32_C(0x01000000) | CMDQ_MAGIC;
    state->interface_ops_address = (uint32_t)(uintptr_t)ops;
    state->current_index = 0u;
    state->end_index = 0u;

    *(volatile uint32_t *)(uintptr_t)ops->reset_register_a = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->reset_register_b = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->control_register |=
        ops->control_mask;
    *(volatile uint32_t *)(uintptr_t)ops->buffer_register =
        config->queue_buffer_address;
    *(volatile uint32_t *)(uintptr_t)ops->option_register =
        ((uint32_t)config->option << 1) & 2u;
    *handle_slot = MAIN_CMDQ_STATE_BASE + interface_id * CMDQ_STATE_STRIDE;
    return 0u;
}
