/* SPDX-License-Identifier: MIT
 * Unseeded 0x10001bf8 transfer descriptor constructor, reconstructed from
 * authenticated stage-1 native instructions. The RAM peripheral base word
 * and descriptor workspace are product/startup layout contracts.
 */
#include <stdint.h>
#include <stddef.h>

extern void gx8002_uart_stage1_pmu_dispatch(uint32_t selector, uint32_t enabled);

struct stage1_transfer_descriptor {
    uint32_t second_address;
    uint32_t first_address;
    uint32_t next;
    uint32_t control;
    uint32_t size;
    uint32_t reserved;
};
_Static_assert(sizeof(struct stage1_transfer_descriptor) == 24,
               "native transfer descriptor stride");

static uint32_t stage1_bus_address(uint32_t address)
{
    const uint32_t shifted = address + UINT32_C(0xf0000000);
    return shifted <= UINT32_C(0x1fffffff)
               ? address & UINT32_C(0x0fffffff) : address;
}

void gx8002_uart_stage1_announce_transfer(uint32_t first_address,
                                           uintptr_t second_address,
                                           uint32_t length,
                                           uint32_t width)
{
    gx8002_uart_stage1_pmu_dispatch(0x19u, 1u);
    const volatile uint32_t *const peripheral_word =
        (const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002274);
    volatile uint32_t *const peripheral =
        (volatile uint32_t *)(uintptr_t)*peripheral_word;
    static const uint16_t enable_offsets[] = {0x338, 0x340, 0x348, 0x350, 0x358};
    static const uint16_t clear_offsets[] = {0x2c0, 0x2c8, 0x2d0, 0x2d8, 0x2e0};
    for (unsigned i = 0; i < 5; ++i) {
        peripheral[enable_offsets[i] / 4] |= 1u;
    }
    for (unsigned i = 0; i < 5; ++i) {
        peripheral[clear_offsets[i] / 4] &= ~UINT32_C(1);
    }
    peripheral[0x398 / 4] = 1;

    const uint32_t second_bus = stage1_bus_address((uint32_t)second_address);
    const uint32_t first_bus = stage1_bus_address(first_address);
    const int32_t divisor = 4095;
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(length), "r"(divisor) : "cc");
    const uint32_t remainder = length - (uint32_t)quotient * 4095u;
    const uint32_t count = (uint32_t)quotient + (remainder != 0u);
    peripheral[0x00 / 4] = second_bus;
    peripheral[0x08 / 4] = first_bus;
    peripheral[0x18 / 4] = UINT32_C(0x1a209401);
    peripheral[0x40 / 4] = 0;
    peripheral[0x44 / 4] = (width << 7) | 2u;

    volatile struct stage1_transfer_descriptor *const descriptors =
        (volatile struct stage1_transfer_descriptor *)(uintptr_t)UINT32_C(0x20002278);
    for (uint32_t i = 0; i + 1u < count; ++i) {
        volatile struct stage1_transfer_descriptor *const descriptor = &descriptors[i];
        descriptor->second_address = second_bus;
        descriptor->first_address = first_bus + i * 4095u;
        descriptor->next = stage1_bus_address((uint32_t)(uintptr_t)&descriptors[i + 1u]);
        descriptor->control = UINT32_C(0x1a209401);
        descriptor->size = 4095u;
    }
    volatile struct stage1_transfer_descriptor *const final =
        &descriptors[count == 0u ? 0u : count - 1u];
    final->second_address = second_bus;
    final->first_address = first_bus + (count > 1u ? count - 1u : 0u) * 4095u;
    final->next = 0;
    final->control = UINT32_C(0x02209401);
    final->size = remainder != 0u ? remainder : 4095u;
    peripheral[0x10 / 4] = stage1_bus_address((uint32_t)(uintptr_t)descriptors);
}
