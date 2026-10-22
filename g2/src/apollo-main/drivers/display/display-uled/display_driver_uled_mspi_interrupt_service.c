/* SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2025 Ambiq Micro, Inc.
 * Apollo-main MSPI interrupt-service candidate for 0x4c240e, adapted from
 * pinned Ambiq HAL 5.1.0 and the independently bounded bootloader candidate.
 * Main-specific SRAM base and lower provider addresses are from the locked
 * S200 image. This is not byte-equal or hardware-validated source.
 */
#include <stdint.h>
#include <stddef.h>

typedef void (*mspi_done_t)(void *, uint32_t);
typedef struct {
    uint32_t last_idx_processed;
    uint32_t last_idx_posted;
    uint32_t last_idx_allocated;
    uint8_t tip, paused, error, pad;
} mspi_cmdq_status_t;

extern uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t, uint32_t *);
extern uint32_t display_driver_uled_mspi_dma_stop_4bfd62(uint32_t *);
extern uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t);
extern uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t *);
extern uint32_t display_driver_uled_mspi_dma_next_4bfdf4(uint32_t *);
extern uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t, uint32_t);

#define MSPI_REG_BASE UINT32_C(0x40060000)
#define MSPI_STATE_BASE UINT32_C(0x200523d8)
#define MSPI_STATE_STRIDE UINT32_C(0x8d0)

static volatile uint32_t *reg(uint32_t module, uint32_t offset)
{
    return (volatile uint32_t *)(uintptr_t)(MSPI_REG_BASE + module * 0x1000u + offset);
}

static uint32_t word(const volatile uint8_t *state, uint32_t offset)
{
    return *(const volatile uint32_t *)(const void *)(state + offset);
}

static void put_word(volatile uint8_t *state, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(state + offset) = value;
}

static void cq_callback(volatile uint8_t *state, uint32_t index, uint32_t status)
{
    const uint32_t slot = index & 0xffu;
    const uintptr_t callback = word(state, 0x28u + slot * 4u);
    if (callback != 0u) {
        ((mspi_done_t)callback)((void *)(uintptr_t)word(state, 0x428u + slot * 4u), status);
        if (state[0x82cu] != 2u)
            put_word(state, 0x28u + slot * 4u, 0u);
    }
}

/* Stock 0x4C240E (am_hal_mspi_interrupt_service) */
uint32_t am_hal_mspi_interrupt_service(void *handle, uint32_t interrupt_status)
{
    volatile uint8_t *const state = (volatile uint8_t *)handle;
    if (state == NULL || (word(state, 0u) & 0x01ffffffu) != 0x01bebebeu)
        return 2u;

    const uint32_t module = word(state, 4u);
    if (state[0x83cu] != 0u) {
        put_word(state, 0x24u, word(state, 0x24u) | interrupt_status);
        if ((word(state, 0x24u) & 0x18c0u) == 0u)
            return 0u;
        while ((*reg(module, 0x104u) & 1u) != 0u) { }
        put_word(state, 0x24u, word(state, 0x24u) | *reg(module, 0x204u));
        *reg(module, 0x208u) = UINT32_MAX;
        const uint32_t failed = (word(state, 0x24u) & 0x1880u) != 0u;
        if (failed) {
            *reg(module, 0x100u) &= ~3u;
            *reg(module, 0x30u) &= ~0x40000000u;
            *reg(module, 0x30u) |= 0x40000000u;
        }
        const uint32_t next = word(state, 0x850u) + 1u;
        put_word(state, 0x850u, next);
        put_word(state, 0x840u, word(state, 0x840u) - 1u);
        const uint32_t ring = word(state, 0x848u);
        const uintptr_t descriptor = word(state, 0x854u) + (next % ring) * 0x18u;
        const uintptr_t callback = *(const uint32_t *)(descriptor + 0x10u);
        if (callback != 0u) {
            ((mspi_done_t)callback)((void *)(uintptr_t)*(const uint32_t *)(descriptor + 0x14u), failed);
            *(uint32_t *)(descriptor + 0x10u) = 0u;
        }
        if (word(state, 0x840u) == 0u) {
            state[0x83cu] = 0u;
            *reg(module, 0x100u) = 0u;
            *reg(module, 0x200u) &= ~0x40u;
            *reg(module, 0x2b4u) = 0x80u;
            if (word(state, 0x20u) == 0u && state[0x8c9u] != 4u)
                return display_driver_uled_mspi_pin_control_4c4530(4u, (module + 0x10u) & 0xffu);
        } else {
            put_word(state, 0x24u, 0u);
            (void)display_driver_uled_mspi_dma_next_4bfdf4((uint32_t *)(void *)state);
        }
        return 0u;
    }

    if (word(state, 0x20u) != 0u) {
        put_word(state, 0x24u, word(state, 0x24u) | interrupt_status);
        const uintptr_t queue_slot = MSPI_STATE_BASE + module * MSPI_STATE_STRIDE + 0x828u;
        const uintptr_t queue = *(const volatile uint32_t *)queue_slot;
        if (queue != 0u) {
            mspi_cmdq_status_t status;
            if (display_driver_uled_mspi_queue_snapshot_53901a(queue, (uint32_t *)&status) == 0u) {
                state[0x834u] = 0u;
                while (state[0x834u] == 0u && word(state, 0x1cu) != status.last_idx_processed) {
                    const uint32_t index = word(state, 0x1cu) + 1u;
                    put_word(state, 0x1cu, index);
                    put_word(state, 0x20u, word(state, 0x20u) - 1u);
                    cq_callback(state, index, 0u);
                }
                if (state[0x834u] == 0u) {
                    if ((interrupt_status & 0x1880u) != 0u || status.error != 0u) {
                        const uint32_t index = word(state, 0x1cu) + 1u;
                        put_word(state, 0x1cu, index);
                        put_word(state, 0x20u, word(state, 0x20u) - 1u);
                        cq_callback(state, index, 1u);
                        uint32_t result = display_driver_uled_mspi_dma_stop_4bfd62((uint32_t *)(void *)state);
                        if (result != 0u) return result;
                        *reg(module, 0x100u) &= ~3u;
                        *reg(module, 0x30u) &= ~0x40000000u;
                        *reg(module, 0x30u) |= 0x40000000u;
                        *reg(module, 0x2acu) = *reg(module, 0x2acu);
                        (void)display_driver_uled_mspi_queue_release_5390fc(queue);
                        if (word(state, 0x20u) != 0u) {
                            result = display_driver_uled_mspi_dma_start_4bfd44((uint32_t *)(void *)state);
                            if (result != 0u) return result;
                        }
                    }
                    if (word(state, 0x20u) == 0u) {
                        const uint32_t result = display_driver_uled_mspi_dma_stop_4bfd62((uint32_t *)(void *)state);
                        if (result != 0u) return result;
                    }
                }
            }
        }
        if (word(state, 0x20u) == 0u) {
            *reg(module, 0x100u) &= ~3u;
            if (state[0x8c9u] != 4u)
                return display_driver_uled_mspi_pin_control_4c4530(4u, (module + 0x10u) & 0xffu);
        }
    }
    return 0u;
}
