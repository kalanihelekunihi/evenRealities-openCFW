/* SPDX-License-Identifier: MIT
 * Native XIP startup children: 0x10203c40, 0x102037e0, 0x102060d0,
 * 0x102060e8, 0x10206680, 0x102066a0, 0x102066b0, 0x102066bc.
 * C-SKY native instructions fix the MMIO/SRAM addresses, call order and
 * callback forwarding. UART initialization remains its actual lower body.
 */
#include <stdint.h>

extern void gx8002_resident_icache_enable_2571c(void);
extern void gx8002_resident_dcache_disable_255e4(void);
extern void gx8002_resident_dcache_enable_255c4(void);
extern uint32_t gx8002_xip_uart_initialize_10203530(uint32_t, uint32_t);
extern uint32_t gx8002_xip_console_port_2002731c;
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);
extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t);
extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

void gx8002_xip_cache_initialize_10203c40(void)
{
    gx8002_resident_icache_enable_2571c();
    gx8002_resident_dcache_disable_255e4();
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f014) = 0x23u;
    gx8002_resident_dcache_enable_255c4();
}

uint32_t gx8002_xip_console_initialize_102037e0(uint32_t port, uint32_t baud)
{
    gx8002_xip_console_port_2002731c = port;
    return gx8002_xip_uart_initialize_10203530(port, baud);
}

void gx8002_xip_gpio_initialize_102060d0(void)
{
    gx8002_resident_platform_gate_25080(4u, 1u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0001034) = 0u;
}

void gx8002_xip_device_list_initialize_102060e8(void)
{
    volatile uint32_t *const lists =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027ad0);
    lists[0] = UINT32_C(0x20027ad0);
    lists[1] = UINT32_C(0x20027ad0);
    lists[2] = UINT32_C(0x20027ad8);
    lists[3] = UINT32_C(0x20027ad8);
}

typedef uint32_t (*gx8002_rtc_callback)(uint32_t, uint32_t);

uint32_t gx8002_xip_rtc_isr_10206680(uint32_t irq)
{
    volatile uint32_t *const callback =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027b40);
    uint32_t raw = callback[0];
    if (raw == 0u) return 0u;
    return ((gx8002_rtc_callback)(uintptr_t)(raw & ~UINT32_C(1)))(
        irq, callback[1]);
}

void gx8002_xip_rtc_start_tick_102066a0(void)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    rtc[0x0cu / 4u] |= 4u;
}

void gx8002_xip_rtc_set_tick_102066b0(uint32_t tick)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    rtc[8u / 4u] = tick;
}

void gx8002_xip_rtc_initialize_102066bc(void)
{
    volatile uint32_t *const rtc =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0003000);
    gx8002_resident_platform_gate_25080(0u, 1u);
    rtc[0x0cu / 4u] |= 0x10u;
    uint32_t frequency = gx8002_resident_clock_frequency_25210(0u);
    if (frequency < 0x10000u) {
        rtc[0x20u / 4u] = frequency;
        gx8002_resident_request_irq_2553c(
            4u, (uint32_t)(uintptr_t)gx8002_xip_rtc_isr_10206680, 0u);
        gx8002_xip_rtc_start_tick_102066a0();
    } else {
        (void)gx8002_xip_tws_publish_10206c24("RTC prescaler error!\n");
    }
}
