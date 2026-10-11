/* SPDX-License-Identifier: MIT
 * Image-A XIP native 0x102060fc, 0x10206164, 0x10206170,
 * 0x10206190. Stock C-SKY branches and fixed address literals are retained.
 * These are candidate source bodies; peripheral runtime equality is open.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t module);

static volatile uint8_t *spi_bytes(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)address;
}

static uint32_t spi_load32(volatile uint8_t *base, uint32_t offset)
{
    return *(volatile uint32_t *)(void *)(base + offset);
}

static void spi_store32(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

int32_t gx8002_xip_spi_register_master_102060fc(void *raw_master)
{
    volatile uint8_t *const head = spi_bytes(UINT32_C(0x20027ad0));
    volatile uint8_t *const master = raw_master;
    if (master == (void *)0) return -19;
    const uint32_t priority = spi_load32(master, 4u);
    const int32_t id = (int32_t)spi_load32(master, 0u);
    if (priority == 0u || id < 0) return -22;

    volatile uint8_t *const link = master + 28u;
    volatile uint8_t *const previous = spi_bytes(spi_load32(head, 4u));
    spi_store32(link, 0u, (uint32_t)(uintptr_t)head);
    spi_store32(head, 4u, (uint32_t)(uintptr_t)link);
    spi_store32(link, 4u, (uint32_t)(uintptr_t)previous);
    spi_store32(previous, 0u, (uint32_t)(uintptr_t)link);

    volatile uint8_t *cursor = spi_bytes(spi_load32(head, 8u));
    while (cursor != head + 8u) {
        if (id == (int32_t)spi_load32(cursor - 24u, 0u) &&
            priority > *(volatile uint8_t *)(void *)(cursor - 12u)) {
            spi_store32(cursor - 20u, 0u, (uint32_t)(uintptr_t)master);
            break;
        }
        cursor = spi_bytes(spi_load32(cursor, 0u));
    }
    return 0;
}

void gx8002_xip_spi_cleanup_10206164(uint32_t *device)
{
    volatile uint8_t *const controller = spi_bytes(device[0]);
    volatile uint8_t *const state = spi_bytes(spi_load32(controller, 0x18u));
    volatile uint8_t *const registers = spi_bytes(spi_load32(state, 4u));
    spi_store32(registers, 8u, 0u);
}

uint32_t gx8002_xip_spi_isr_10206170(uint32_t irq, void *raw_controller)
{
    (void)irq;
    volatile uint8_t *controller = raw_controller;
    volatile uint8_t *registers = spi_bytes(spi_load32(controller, 4u));
    const uint32_t status = spi_load32(registers, 0x30u);
    if ((status & 2u) != 0u)
        (void)*((volatile const uint32_t *)(uintptr_t)UINT32_C(0x38));
    if ((status & 8u) != 0u)
        (void)*((volatile const uint32_t *)(uintptr_t)UINT32_C(0x3c));
    return 0u;
}

int32_t gx8002_xip_spi_setup_10206190(void *raw_device)
{
    volatile uint8_t *const device = raw_device;
    *(volatile uint16_t *)(void *)(device + 10u) = 0u;
    if (device[9u] == 0u) device[9u] = 8u;
    uint32_t descriptor = spi_load32(device, 12u);
    if (descriptor == 0u) {
        descriptor = UINT32_C(0x20027ae0);
        if (spi_load32(spi_bytes(descriptor), 0u) != 0u) return -12;
    }
    uint32_t rate = spi_load32(device, 4u);
    if (rate == 0u) {
        rate = UINT32_C(10000000);
        spi_store32(device, 4u, rate);
    }
    const uint32_t source = gx8002_resident_clock_frequency_25210(14u);
    uint32_t divider = (source / rate) & ~UINT32_C(1);
    volatile uint8_t *const target = spi_bytes(descriptor);
    spi_store32(target, 0u, (uint32_t)(uintptr_t)device);
    const uint32_t mode =
        UINT32_C(0x80000000) |
        ((uint32_t)(*(volatile uint16_t *)(void *)(device + 10u) & 3u) << 8u) |
        (((uint32_t)device[16u] & 3u) << 22u);
    spi_store32(target, 4u, mode);
    if (source != divider * rate) divider += 2u;
    spi_store32(target, 8u, divider);
    spi_store32(target, 12u, 2u);
    spi_store32(device, 12u, descriptor);
    return 0;
}
