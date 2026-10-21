/* SPDX-License-Identifier: MIT
 * Image-B DMA setup at 0x10004d14. Storage alignment, gate transitions,
 * controller clears and IRQ registration follow the native ordering.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enable);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t line, int32_t (*handler)(int32_t, void *), uint32_t argument);
extern int32_t gx8002_image_b_dma_irq_10004c04(int32_t line, void *context);

void gx8002_image_b_dma_initialize_10004d14(void)
{
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    *(volatile uint32_t *)(void *)(state + 0u) = UINT32_C(0xa1000000);
    *(volatile uint32_t *)(void *)(state + 4u) = 2u;
    *(volatile uint32_t *)(void *)(state + 0x368u) =
        ((uint32_t)(uintptr_t)(state + 23u)) & ~UINT32_C(15);
    state[0x370u] = 0u;
    *(volatile uint32_t *)(void *)(state + 0x36cu) =
        ((uint32_t)(uintptr_t)(state + 455u)) & ~UINT32_C(15);
    state[0x371u] = 0u;
    gx8002_image_b_platform_gate_10003be8(25u, 1u);
    uint32_t base = *(volatile uint32_t *)(void *)state;
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)base;
    registers[0x398u / 4u] = 0u;
    registers[0x338u / 4u] = UINT32_MAX;
    registers[0x340u / 4u] = UINT32_MAX;
    registers[0x348u / 4u] = UINT32_MAX;
    registers[0x350u / 4u] = UINT32_MAX;
    registers[0x358u / 4u] = UINT32_MAX;
    registers[0x398u / 4u] = 1u;
    gx8002_image_b_platform_gate_10003be8(25u, 0u);
    gx8002_image_b_request_irq_10004844(
        10u, gx8002_image_b_dma_irq_10004c04, 0u);
}
