/* SPDX-License-Identifier: MIT
 * Reconstructed Apollo510 private MSPI clock/command-queue adapters and the
 * bounded CMDQ operations reached by those adapters.  Peripheral addresses
 * and sparse queue rows are tied to the locked bootloader image.
 */
#include "nor_mspi_queue.h"
#include <stddef.h>

#define MSPI_CLOCK_CONTROL       UINT32_C(0x40004110)
#define MSPI_STATE_BASE          UINT32_C(0x2001caa0)
#define MSPI_STATE_STRIDE        UINT32_C(0x8d0)
#define MSPI_QUEUE_HANDLE_OFFSET UINT32_C(0x828)
#define CMDQ_STATE_BASE          UINT32_C(0x200262f0)
#define CMDQ_OPS_BASE            UINT32_C(0x00430880)
#define CMDQ_STATE_STRIDE        UINT32_C(0x2c)
#define CMDQ_OPS_STRIDE          UINT32_C(0x28)
#define CMDQ_INTERFACE_COUNT     UINT32_C(12)
#define CMDQ_MAGIC               UINT32_C(0x01cdcdcd)
#define CMDQ_VALID_MASK          UINT32_C(0x01ffffff)

extern uint32_t opencfw_bl_critical_save(void);
extern uint32_t opencfw_bl_clock_request(uint32_t clock, uint32_t user);
extern void opencfw_bl_delay_us(uint32_t raw_duration);

typedef struct {
    uint32_t queue_size_half_units;
    uint32_t queue_buffer_address;
    uint8_t option;
} cmdq_config_t;

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
} cmdq_state_t;

typedef struct {
    uint32_t option_register;
    uint32_t buffer_register;
    uint32_t reset_register_a;
    uint32_t reset_register_b;
    uint32_t control_register;
    uint32_t control_mask;
    uint32_t unused_18;
    uint32_t unused_1c;
    uint32_t unused_20;
    uint32_t unused_24;
} cmdq_ops_t;

_Static_assert(sizeof(void *) == 4, "locked bootloader uses 32-bit pointers");
_Static_assert(sizeof(cmdq_config_t) == 12, "CMDQ config ABI");
_Static_assert(sizeof(cmdq_state_t) == CMDQ_STATE_STRIDE, "CMDQ state stride");
_Static_assert(sizeof(cmdq_ops_t) == CMDQ_OPS_STRIDE, "CMDQ ops stride");
_Static_assert(offsetof(cmdq_state_t, interface_ops_address) == 0x24,
               "CMDQ ops pointer offset");

static volatile cmdq_state_t *cmdq_state(uint32_t interface_id)
{
    return (volatile cmdq_state_t *)(uintptr_t)
        (CMDQ_STATE_BASE + interface_id * CMDQ_STATE_STRIDE);
}

static volatile cmdq_ops_t *cmdq_ops(uint32_t interface_id)
{
    return (volatile cmdq_ops_t *)(uintptr_t)
        (CMDQ_OPS_BASE + interface_id * CMDQ_OPS_STRIDE);
}

static uint32_t queue_is_valid(const uint32_t *queue)
{
    return queue != NULL && (queue[0] & CMDQ_VALID_MASK) == CMDQ_MAGIC;
}

#ifndef OPENCFW_USE_EXTERNAL_MSPI_CLOCKGEN
static uint32_t shifted(uint32_t value, uint32_t amount)
{
    return amount < 32u ? value << amount : 0u;
}
#endif

static void update_indices(uint32_t *queue)
{
    const uint32_t saved_mask = opencfw_bl_critical_save();
    const uintptr_t ops = queue[9];
    const uintptr_t current_index_register =
        *(const volatile uint32_t *)(ops + 8u);
    const uint32_t current_low =
        *(const volatile uint32_t *)current_index_register & 0xffu;
    uint32_t current = current_low | (queue[8] & 0xffffff00u);

    queue[7] = current;
    if ((int32_t)(queue[8] - current) < 0)
        queue[7] = current - 0x100u;

    const uintptr_t current_queue_head_register =
        *(const volatile uint32_t *)(ops + 4u);
    queue[3] = *(const volatile uint32_t *)current_queue_head_register;
    __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
}

#ifndef OPENCFW_USE_EXTERNAL_MSPI_CLOCKGEN
void opencfw_bl_mspi_clockgen_control(uint32_t module, uint32_t enable,
                                     uint32_t configure, uint32_t source)
{
    const uint32_t saved_mask = opencfw_bl_critical_save();
    const uint32_t shift = (module * 5u) & 0xffu;
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)MSPI_CLOCK_CONTROL;

    if ((uint8_t)enable == 0u) {
        *control &= ~shifted(1u, shift);
    } else {
        if ((uint8_t)configure != 0u) {
            const uint32_t field_mask = shifted(0x1eu, shift);
            const uint32_t field_value = shifted(
                (uint32_t)(uint8_t)source << 1, shift);
            *control = (*control & ~field_mask) | field_value;
        }
        *control |= shifted(1u, shift);
        opencfw_bl_delay_us(10u);
    }

    __asm__ volatile("msr primask, %0" :: "r"(saved_mask) : "memory");
}
#endif

void opencfw_hal_mspi_cq_init(uint32_t module, uint32_t queue_size_input,
                              uint32_t queue_buffer_address)
{
    cmdq_config_t config;
    const uintptr_t handle_slot = MSPI_STATE_BASE +
        module * MSPI_STATE_STRIDE + MSPI_QUEUE_HANDLE_OFFSET;

    config.queue_size_half_units = queue_size_input >> 1;
    config.queue_buffer_address = queue_buffer_address;
    config.option = 1u;
    (void)opencfw_provider_427794((module + 8u) & 0xffu, &config,
                                  (void **)handle_slot);
}

void opencfw_bl_mspi_cq_enable(uint32_t mspi_state_address)
{
    const uint32_t module = *(const volatile uint32_t *)(uintptr_t)
        (mspi_state_address + 4u);
    const uint32_t status = opencfw_bl_clock_request(
        4u, (module + 0x10u) & 0xffu);
    if (status == 0u) {
        const uintptr_t queue = *(const volatile uint32_t *)(uintptr_t)
            (mspi_state_address + MSPI_QUEUE_HANDLE_OFFSET);
        (void)opencfw_provider_427878((uint32_t *)queue);
    }
}

uint32_t opencfw_hal_mspi_cq_disable(uint32_t mspi_state_address)
{
    const uintptr_t queue = *(const volatile uint32_t *)(uintptr_t)
        (mspi_state_address + MSPI_QUEUE_HANDLE_OFFSET);
    return opencfw_provider_4278c8((uint32_t *)queue);
}

void opencfw_hal_mspi_cq_term(uint32_t mspi_state_address)
{
    const uint32_t module = *(const volatile uint32_t *)(uintptr_t)
        (mspi_state_address + 4u);
    const uintptr_t slot = MSPI_STATE_BASE + module * MSPI_STATE_STRIDE +
                           MSPI_QUEUE_HANDLE_OFFSET;
    const uintptr_t queue = *(const volatile uint32_t *)slot;

    if (queue != 0u) {
        (void)opencfw_provider_427ad6((uint32_t *)queue, 1u);
        *(volatile uint32_t *)slot = 0u;
    }
}

uint32_t opencfw_provider_427794(uint32_t interface_id,
                                const void *config_pointer,
                                void **handle_slot)
{
    const cmdq_config_t *const config =
        (const cmdq_config_t *)config_pointer;
    volatile cmdq_state_t *state;
    volatile cmdq_ops_t *ops;
    uint32_t option;

    interface_id &= 0xffu;
    if (interface_id >= CMDQ_INTERFACE_COUNT)
        return 5u;
    if (config == NULL || config->queue_buffer_address == 0u ||
        handle_slot == NULL || config->queue_size_half_units < 2u)
        return 6u;

    state = cmdq_state(interface_id);
    if ((state->flags & 0x01000000u) != 0u)
        return 7u;

    state->queue_size_bytes = config->queue_size_half_units << 3;
    state->queue_buffer = config->queue_buffer_address;
    state->write_pointer = config->queue_buffer_address;
    state->consumer_pointer = config->queue_buffer_address;
    state->producer_pointer = config->queue_buffer_address;
    state->read_pointer = config->queue_buffer_address +
        config->queue_size_half_units * 8u;
    state->flags |= 0x01000000u;
    state->flags &= ~0x02000000u;
    state->flags = (state->flags & 0xff000000u) | CMDQ_MAGIC;
    state->interface_ops_address = CMDQ_OPS_BASE +
        interface_id * CMDQ_OPS_STRIDE;
    state->current_index = 0u;
    state->end_index = 0u;

    ops = cmdq_ops(interface_id);
    *(volatile uint32_t *)(uintptr_t)ops->reset_register_a = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->reset_register_b = 0u;
    *(volatile uint32_t *)(uintptr_t)ops->control_register |=
        ops->control_mask;
    *(volatile uint32_t *)(uintptr_t)ops->buffer_register =
        config->queue_buffer_address;
    option = ((uint32_t)config->option & 1u) << 1;
    *(volatile uint32_t *)(uintptr_t)ops->option_register = option;
    *handle_slot = (void *)(uintptr_t)(CMDQ_STATE_BASE +
        interface_id * CMDQ_STATE_STRIDE);
    return 0u;
}

uint32_t opencfw_provider_427878(uint32_t *queue)
{
    if (!queue_is_valid(queue))
        return 2u;
    if ((queue[0] & 0x02000000u) != 0u)
        return 0u;

    if (queue[2] >= UINT32_C(0x20080000))
        __asm__ volatile("dmb sy" ::: "memory");

    volatile uint32_t *const option_register =
        (volatile uint32_t *)(uintptr_t)
            *(const volatile uint32_t *)(uintptr_t)queue[9];
    *option_register |= 1u;
    queue[0] |= 0x02000000u;
    return 0u;
}

uint32_t opencfw_provider_4278c8(uint32_t *queue)
{
    if (!queue_is_valid(queue))
        return 2u;
    if ((queue[0] & 0x02000000u) == 0u)
        return 0u;

    volatile uint32_t *const option_register =
        (volatile uint32_t *)(uintptr_t)
            *(const volatile uint32_t *)(uintptr_t)queue[9];
    *option_register &= ~1u;
    queue[0] &= ~0x02000000u;
    return 0u;
}

uint32_t opencfw_provider_427ad6(uint32_t *queue, uint32_t force)
{
    if (!queue_is_valid(queue))
        return 2u;

    update_indices(queue);
    if ((uint8_t)force == 0u && queue[7] != queue[8])
        return 3u;

    queue[0] &= ~0x01000000u;
    volatile cmdq_ops_t *const ops =
        (volatile cmdq_ops_t *)(uintptr_t)queue[9];
    *(volatile uint32_t *)(uintptr_t)ops->option_register &= ~1u;
    *(volatile uint32_t *)(uintptr_t)ops->control_register &=
        ~ops->control_mask;
    return 0u;
}

/* ABI names used by the existing HAL leaves and by the public Apollo source. */
uint32_t am_hal_cmdq_enable(void *queue)
{
    return opencfw_provider_427878((uint32_t *)queue);
}

uint32_t am_hal_cmdq_disable(void *queue)
{
    return opencfw_provider_4278c8((uint32_t *)queue);
}

uint32_t am_hal_cmdq_term(void *queue, uint32_t force)
{
    return opencfw_provider_427ad6((uint32_t *)queue, force);
}
