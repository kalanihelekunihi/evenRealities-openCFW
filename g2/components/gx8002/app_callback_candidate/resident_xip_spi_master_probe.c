/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10206480..0x1020656f. Source owns the SPI master
 * setup, controller register probing, MMIO gate and callback relocations.
 * Four downstream SPI bodies remain actual typed imported functions.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern void gx8002_xip_spi_cleanup_10206164(uint32_t *device);
extern int32_t gx8002_xip_spi_setup_10206190(void *device);
extern int32_t gx8002_xip_spi_quick_transfer_10206204(
    uint32_t *device, void *transfer);
extern int32_t gx8002_xip_spi_register_master_102060fc(void *master);
extern uint32_t gx8002_xip_spi_isr_10206170(uint32_t irq, void *controller);

static volatile uint32_t *spi_registers(void)
{
    volatile const uint32_t *const base =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027b18);
    return (volatile uint32_t *)(uintptr_t)*base;
}

static uint32_t probe_capacity(uint32_t register_offset)
{
    volatile uint32_t *const register_word =
        (volatile uint32_t *)(void *)((volatile uint8_t *)spi_registers() +
                                      register_offset);
    uint32_t candidate = 2u;
    for (uint32_t count = 0; count < 256u; ++count) {
        *register_word = candidate;
        if (*register_word != candidate) {
            if (candidate == 257u) candidate = 0u;
            break;
        }
        ++candidate;
    }
    *register_word = 0u;
    return candidate;
}

void gx8002_xip_spi_master_probe_10206480(void)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20027ae0);
    *(volatile uint32_t *)(void *)(state + 0x38u) = UINT32_C(0xa3000000);
    *(volatile uint32_t *)(void *)(state + 0x34u) = UINT32_C(0x20027af0);
    *(volatile uint32_t *)(void *)(state + 0x28u) = UINT32_C(0x20027b14);
    *(volatile uint32_t *)(void *)(state + 0x10u) = 0u;
    *(volatile uint32_t *)(void *)(state + 0x14u) = 1u;
    *(volatile uint32_t *)(void *)(state + 0x20u) =
        (uint32_t)(uintptr_t)gx8002_xip_spi_cleanup_10206164;
    *(volatile uint32_t *)(void *)(state + 0x18u) =
        (uint32_t)(uintptr_t)gx8002_xip_spi_setup_10206190;
    *(volatile uint32_t *)(void *)(state + 0x1cu) =
        (uint32_t)(uintptr_t)gx8002_xip_spi_quick_transfer_10206204;
    gx8002_resident_platform_gate_25080(14u, 1u);
    volatile uint32_t *const registers = spi_registers();
    registers[8u / 4u] = 0u;
    registers[0x2cu / 4u] = 0x4eu;
    if (*(volatile uint32_t *)(void *)(state + 0x3cu) == 0u)
        *(volatile uint32_t *)(void *)(state + 0x3cu) = probe_capacity(0x18u);
    if (*(volatile uint32_t *)(void *)(state + 0x40u) == 0u)
        *(volatile uint32_t *)(void *)(state + 0x40u) = probe_capacity(0x1cu);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa030008c) = 3u;
    registers[8u / 4u] = 1u;
    while ((registers[0x28u / 4u] & 8u) != 0u) { }
    while ((registers[0x28u / 4u] & 1u) != 0u) { }
    gx8002_resident_platform_gate_25080(14u, 0u);
    *(volatile uint32_t *)(void *)(state + 0x44u) = 0u;
    *(volatile uint32_t *)(void *)(state + 0x48u) = 0u;
    (void)gx8002_xip_spi_register_master_102060fc(
        (void *)(uintptr_t)UINT32_C(0x20027af0));
    gx8002_resident_request_irq_2553c(
        16u, (uint32_t)(uintptr_t)gx8002_xip_spi_isr_10206170,
        UINT32_C(0x20027b14));
}
