/* Readable reconstruction of the locked 228-byte am_hal_cmdq_init at
 * 0x00427794.  The two absolute data bases and sparse 32-bit row layouts
 * are taken from its literal loads/stores; no public SDK structure is used. */
#include <stddef.h>
#include <stdint.h>

enum {
    CMDQ_STATE_BASE = 0x200262f0u,
    CMDQ_OPS_BASE = 0x00430880u,
    CMDQ_STATE_STRIDE = 0x2cu,
    CMDQ_OPS_STRIDE = 0x28u,
    CMDQ_INTERFACE_COUNT = 12u
};

struct cmdq_config32 {
    uint32_t queue_size_half_units;
    uint32_t queue_buffer_address;
    uint8_t option;
};

/* Byte offsets grounded in the consumer's accesses, not a claimed complete
 * HAL type. The trailing word at +0x28 is not touched by this function. */
struct cmdq_state32 {
    uint32_t flags;                 /* +0x00 */
    uint32_t queue_buffer;          /* +0x04 */
    uint32_t read_pointer;           /* +0x08 */
    uint32_t write_pointer;          /* +0x0c */
    uint32_t producer_pointer;       /* +0x10 */
    uint32_t consumer_pointer;       /* +0x14 */
    uint32_t queue_size_bytes;       /* +0x18 */
    uint32_t private_zero_1c;        /* +0x1c */
    uint32_t private_zero_20;        /* +0x20 */
    uint32_t interface_ops_address;  /* +0x24 */
    uint32_t untouched_28;           /* +0x28 */
};

struct cmdq_interface_ops32 {
    uint32_t option_register;        /* +0x00 */
    uint32_t buffer_register;        /* +0x04 */
    uint32_t reset_register_a;       /* +0x08 */
    uint32_t reset_register_b;       /* +0x0c */
    uint32_t control_register;       /* +0x10 */
    uint32_t control_mask;           /* +0x14 */
    uint32_t untouched_18;           /* +0x18 */
    uint32_t untouched_1c;           /* +0x1c */
    uint32_t untouched_20;           /* +0x20 */
    uint32_t untouched_24;           /* +0x24 */
};

_Static_assert(sizeof(struct cmdq_config32) == 12u, "stock config extent");
_Static_assert(sizeof(struct cmdq_state32) == CMDQ_STATE_STRIDE,
               "stock state row stride");
_Static_assert(offsetof(struct cmdq_state32, interface_ops_address) == 0x24u,
               "stock ops pointer offset");
_Static_assert(sizeof(struct cmdq_interface_ops32) == CMDQ_OPS_STRIDE,
               "stock interface ops row stride");
_Static_assert(sizeof(uintptr_t) == 4u, "stock uses 32-bit pointers");

static volatile struct cmdq_state32 *state_row(uint32_t interface_id)
{
    return (volatile struct cmdq_state32 *)(uintptr_t)
        (CMDQ_STATE_BASE + interface_id * CMDQ_STATE_STRIDE);
}

static volatile struct cmdq_interface_ops32 *ops_row(uint32_t interface_id)
{
    return (volatile struct cmdq_interface_ops32 *)(uintptr_t)
        (CMDQ_OPS_BASE + interface_id * CMDQ_OPS_STRIDE);
}

uint32_t opencfw_bl_cmdq_init(uint32_t interface_id,
                              const struct cmdq_config32 *config,
                              void **handle_slot)
{
    volatile struct cmdq_state32 *state;
    volatile struct cmdq_interface_ops32 *ops;
    uint32_t option;

    interface_id &= 0xffu;
    if (interface_id >= CMDQ_INTERFACE_COUNT) {
        return 5u;
    }
    if (config == NULL || config->queue_buffer_address == 0u ||
        handle_slot == NULL || config->queue_size_half_units < 2u) {
        return 6u;
    }

    state = state_row(interface_id);
    if ((state->flags & 0x01000000u) != 0u) {
        return 7u;
    }

    state->queue_size_bytes = config->queue_size_half_units << 3;
    state->queue_buffer = config->queue_buffer_address;
    state->write_pointer = config->queue_buffer_address;
    state->consumer_pointer = config->queue_buffer_address;
    state->producer_pointer = config->queue_buffer_address;
    state->read_pointer = config->queue_buffer_address +
                          (config->queue_size_half_units << 3);
    state->flags = (state->flags | 0x01000000u) & 0xfdffffffu;
    state->flags = (state->flags & 0xff000000u) | 0x00cdcdcdU;
    state->interface_ops_address = CMDQ_OPS_BASE +
                                   interface_id * CMDQ_OPS_STRIDE;
    state->private_zero_1c = 0u;
    state->private_zero_20 = 0u;

    ops = ops_row(interface_id);
    *(volatile uint32_t *)(uintptr_t)ops->reset_register_a = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->reset_register_b = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->control_register =
        *(volatile uint32_t *)(uintptr_t)ops->control_register |
        ops->control_mask;
    *(volatile uint32_t *)(uintptr_t)ops->buffer_register =
        config->queue_buffer_address;
    option = ((uint32_t)config->option & 1u) << 1;
    *(volatile uint32_t *)(uintptr_t)ops->option_register = option;
    *handle_slot = (void *)(uintptr_t)(CMDQ_STATE_BASE +
                                      interface_id * CMDQ_STATE_STRIDE);
    return 0u;
}

/* Match the stock linkage name used by mspi_cq_init.  This adapter preserves
 * the byte-wide interface argument and forwards into the independently
 * testable reconstruction above. */
uint32_t am_hal_cmdq_init(uint8_t interface_id,
                          const struct cmdq_config32 *config,
                          void **handle_slot)
{
    return opencfw_bl_cmdq_init(interface_id, config, handle_slot);
}
