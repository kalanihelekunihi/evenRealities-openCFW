/* SPDX-License-Identifier: MIT
 * Reconstructed locked Apollo510 bootloader leaves. MMIO is exercised only
 * as synthetic RAM in the accompanying comparison, not physical hardware.
 */
#include <stdint.h>
extern void opencfw_hal_mspi_cq_init(uint32_t, uint32_t, uint32_t);
extern uint32_t opencfw_hal_mspi_cq_disable(uint32_t);
extern void opencfw_hal_mspi_cq_term(uint32_t);
extern void opencfw_hal_delay_us(uint32_t);
uint32_t opencfw_hal_mspi_disable(uint32_t);
static uint32_t valid(const uint32_t *handle) {
    return handle && ((handle[0] & 0x01ffffffu) == 0x01bebebeu);
}
static volatile uint32_t *reg(const uint32_t *handle, uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)
        (0x40060000u + (handle[1] << 12) + offset);
}
uint32_t opencfw_hal_mspi_configure(uint32_t address, const uint32_t *config) {
    volatile uint32_t *handle = (volatile uint32_t *)(uintptr_t)address;
    /* Stock reads module before its null check. Preserve that raw access;
     * this is not a bounds-checked API for arbitrary caller pointers. */
    uint32_t module = handle[1];
    if (!valid((const uint32_t *)handle)) return 2;
    if (handle[0] & 0x02000000u) return 7;
    volatile uint32_t *base = (volatile uint32_t *)(uintptr_t)
        (0x40060000u + (module << 12));
    base[0x90 / 4] &= ~1u;
    base[0x9c / 4] = base[0x80 / 4] = 0;
    uint32_t *state = (uint32_t *)(uintptr_t)
        (0x2001caa0u + module * 0x8d0u);
    state[6] = config[1];
    state[5] = config[0];
    if (handle[6] != 0u) {
        ((volatile uint8_t *)handle)[0x8c8] =
            handle[6] + (handle[5] << 2) < 0x20080000u;
        uint32_t slots = ((handle[5] - 8u) << 2) / 0x48u;
        state[0x216] = slots > 256u ? 256u : slots;
    }
    ((uint8_t *)state)[9] = ((const uint8_t *)config)[8];
    ((uint8_t *)state)[8] = 1;
    ((uint8_t *)state)[10] = 0x1a;
    return 0;
}
uint32_t opencfw_hal_mspi_enable(uint32_t address) {
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2;
    if (((uint8_t *)handle)[8] == 0u) return 7;
    if (handle[6] != 0u) {
        handle[7] = handle[8] = 0;
        opencfw_hal_mspi_cq_init(handle[1], handle[5], handle[6]);
        *reg(handle, 0x2b4u) = 0x00400080u;
        handle[0x215] = 0;
        ((uint8_t *)handle)[0x83c] = 0;
        handle[0x211] = handle[0x20e] = handle[0x210] = 0;
        ((uint8_t *)handle)[0x82c] = 0;
        handle[0x20c] = 0;
        ((uint8_t *)handle)[0x82d] = 1;
        handle[0x217] = 0;
    }
    handle[0] |= 0x02000000u;
    return 0;
}
uint32_t opencfw_hal_mspi_disable(uint32_t address) {
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2;
    if (!(handle[0] & 0x02000000u)) return 0;
    if (handle[0x210] != 0u || handle[8] != 0u) return 3;
    if (handle[6] != 0u) {
        uint32_t status = opencfw_hal_mspi_cq_disable(address);
        if (status != 0u) return status;
        opencfw_hal_mspi_cq_term(address);
    }
    handle[0] &= ~0x02000000u;
    if (*reg(handle, 0x90u) & 1u)
        opencfw_hal_delay_us(handle[0x233]);
    return 0;
}
uint32_t opencfw_hal_mspi_interrupt_enable(uint32_t address, uint32_t mask) {
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2;
    *reg(handle, 0x200u) |= mask;
    return 0;
}
uint32_t opencfw_hal_mspi_interrupt_clear(uint32_t address, uint32_t mask) {
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2;
    *reg(handle, 0x208u) = mask;
    (void)*reg(handle, 0x204u); /* Stock performs the status read. */
    return 0;
}
uint32_t opencfw_hal_mspi_deinitialize(uint32_t address) {
    uint32_t *handle = (uint32_t *)(uintptr_t)address;
    if (!valid(handle)) return 2;
    if (handle[0] & 0x02000000u)
        (void)opencfw_hal_mspi_disable(address);
    handle[0] &= ~0x01000000u;
    handle[1] = 0;
    return 0;
}
void opencfw_bl_interrupt_enable(uint32_t number) {
    int32_t irq = (int16_t)number;
    if (irq >= 0)
        *(volatile uint32_t *)(uintptr_t)
            (0xe000e100u + ((uint32_t)irq >> 5) * 4u) =
            1u << (number & 31u);
}
void opencfw_bl_interrupt_priority(uint32_t number, uint32_t priority) {
    int32_t irq = (int16_t)number;
    uintptr_t address = irq < 0 ?
        0xe000ed14u + ((uint32_t)irq & 15u) :
        0xe000e400u + (uint32_t)irq;
    *(volatile uint8_t *)address = (uint8_t)(priority << 4);
}
