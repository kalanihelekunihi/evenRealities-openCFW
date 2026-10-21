/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10203bc0..0x10203c35 and 0x102068a0..0x102068f9.
 * DMA descriptor offsets, MMIO writes, IRQ registration, and 13 board pin
 * pairs are from stock instructions/decoded data. Padmux and DMA ISR are
 * genuine lower bodies retained as typed imports.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_dma_isr_10203adc(void);
extern int32_t gx8002_xip_padmux_initialize_10206630(const uint8_t *, int32_t);
extern int32_t gx8002_xip_padmux_check_102065b8(uint32_t, uint32_t);
extern uint32_t gx8002_xip_gpio_set_direction_10205f24(uint32_t, uint32_t);
extern void gx8002_xip_board_pin_setup_1020681c(void);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

const uint8_t gx8002_xip_board_pin_defaults_1020ad30[26] = {
    0,1, 1,1, 2,0, 3,1, 4,1, 5,1, 6,1,
    7,1, 8,1, 9,1, 10,1, 11,1, 12,1
};

void gx8002_xip_dma_initialize_10203bc0(void)
{
    volatile uint8_t *const descriptor =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e93c);
    *(volatile uint32_t *)(void *)(descriptor + 0u) = UINT32_C(0xa1000000);
    *(volatile uint32_t *)(void *)(descriptor + 4u) = 2u;
    *(volatile uint32_t *)(void *)(descriptor + 0x368u) =
        ((uint32_t)(uintptr_t)descriptor + 23u) & ~UINT32_C(15);
    descriptor[0x370u] = 0u;
    *(volatile uint32_t *)(void *)(descriptor + 0x36cu) =
        ((uint32_t)(uintptr_t)descriptor + 455u) & ~UINT32_C(15);
    descriptor[0x371u] = 0u;
    gx8002_resident_platform_gate_25080(25u, 1u);
    volatile uint8_t *const registers = (volatile uint8_t *)(uintptr_t)
        *(volatile uint32_t *)(void *)descriptor;
    *(volatile uint32_t *)(void *)(registers + 0x398u) = 0u;
    for (uint32_t offset = 0x338u; offset <= 0x358u; offset += 8u)
        *(volatile uint32_t *)(void *)(registers + offset) = UINT32_MAX;
    *(volatile uint32_t *)(void *)(registers + 0x398u) = 1u;
    gx8002_resident_platform_gate_25080(25u, 0u);
    gx8002_resident_request_irq_2553c(
        10u, (uint32_t)(uintptr_t)gx8002_xip_dma_isr_10203adc, 0u);
}

void gx8002_xip_board_pin_initialize_102068a0(void)
{
    (void)gx8002_xip_padmux_initialize_10206630(
        gx8002_xip_board_pin_defaults_1020ad30, 13u);
    for (uint32_t index = 0; index < 13u; ++index) {
        uint32_t pin = gx8002_xip_board_pin_defaults_1020ad30[index * 2u];
        uint32_t function = gx8002_xip_board_pin_defaults_1020ad30[index * 2u + 1u];
        if (gx8002_xip_padmux_check_102065b8(pin, function) != 0)
            (void)gx8002_xip_tws_publish_10206c24("pin %d set error!\n", pin);
        if ((pin == 2u && function == 0u) ||
            (pin != 2u && function == 1u))
            (void)gx8002_xip_gpio_set_direction_10205f24(pin, 0u);
    }
    gx8002_xip_board_pin_setup_1020681c();
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b4c) = 1u;
}
