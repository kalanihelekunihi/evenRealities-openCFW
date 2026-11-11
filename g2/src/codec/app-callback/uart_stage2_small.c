/* SPDX-License-Identifier: MIT
 * Small authenticated UART stage-2 bodies in the reset descendant graph.
 */
#include <stdint.h>

/* Stock 0x10002A3C (gx_analog_config_update_enable) */
void gx8002_uart_stage2_runtime_boot_2a3c(void)
{
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    analog[0x40 / 4] = 0x59u;
    analog[0x44 / 4] = 0x59u;
    analog[0x48 / 4] = 0x59u;
    analog[0x4c / 4] = 0x59u;
}

uint32_t gx8002_uart_stage2_address_mask_29c0(uint32_t address)
{
    if (address < UINT32_C(0x20000000)) address &= UINT32_C(0x07ffffff);
    return address;
}

/* Stock 0x10004408 (gx_analog_set_ldo_ana_voltage) */
uint32_t gx8002_uart_stage2_set_ldo_analog_voltage_4408(uint32_t voltage)
{
    if (voltage == UINT32_MAX) return voltage;
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    analog[0x54 / 4] = (uint8_t)(voltage | (analog[0x54 / 4] & 0xf0u));
    return 0;
}

extern void gx8002_uart_stage2_cache_init_3174(void);
extern void gx8002_uart_stage2_dcache_disable_31b4(void);
extern void gx8002_uart_stage2_interrupt_tail_3194(void);

void gx8002_uart_stage2_interrupt_setup_29a0(void)
{
    gx8002_uart_stage2_cache_init_3174();
    gx8002_uart_stage2_dcache_disable_31b4();
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f014) = UINT32_C(0x20000023);
    gx8002_uart_stage2_interrupt_tail_3194();
}

uint32_t gx8002_uart_stage2_chip_revision_4f6c(void)
{
    const uint32_t revision =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000034);
    if (revision & 1u) return 2;
    if (revision & 4u) return 3;
    if (revision & 8u) return 5;
    if (revision & 2u) return 4;
    return *(const volatile uint32_t *)(uintptr_t)UINT32_C(0xa001002c) & 1u;
}

void gx8002_uart_stage2_reset_state_29d4(void)
{
    volatile uint32_t *const pmu =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    volatile uint32_t *const config =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009084);
    const uint32_t kind = pmu[0x68 / 4] & 15u;
    if (kind == 1u) {
        config[1] = (pmu[0x68 / 4] >> 4) & 15u;
        config[0] = 7u;
    } else if (kind == 0u) {
        config[0] = 0u;
        config[1] = (pmu[0x68 / 4] >> 4) & 15u;
    } else if (kind == 2u) {
        config[1] = pmu[0x68 / 4] & ~UINT32_C(0xff);
        config[0] = kind;
    }
}

extern uint32_t gx8002_uart_stage2_clock_revision_4fd0(void);
extern uint32_t gx8002_uart_stage2_clock_alternate_4fe8(void);

uint32_t gx8002_uart_stage2_default_baud_2a1c(void)
{
    if (gx8002_uart_stage2_clock_revision_4fd0() == 1u ||
        gx8002_uart_stage2_clock_alternate_4fe8() == 1u)
        return *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x20002010);
    return 0;
}

extern uint32_t gx8002_uart_stage2_uart_config_2e28(uint32_t port,
                                                      uint32_t baud);

void gx8002_uart_stage2_set_baud_2a50(uint32_t port, uint32_t baud)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20009840) = port;
    (void)gx8002_uart_stage2_uart_config_2e28(port, baud);
}

uint32_t gx8002_uart_stage2_ready_4fb0(void)
{
    const uint32_t revision = gx8002_uart_stage2_chip_revision_4f6c();
    if (revision - 2u >= 4u) return 0;
    volatile uint32_t *const pmu =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010000);
    const uint32_t ready = pmu[0x58 / 4] & 1u;
    (void)pmu[0x5c / 4];
    return ready;
}

/* Stock 0x10004428: analog request 8 (register 0x38) with level bits 3:0
 * and enable bit 4. Native builds the byte in an unwritten stack word, so
 * bits 7:5 and bytes 1..3 were stale; they are 0 here. */
extern uint32_t gx8002_uart_stage2_analog_request_4db8(uint32_t kind,
                                                          const uint8_t *request);
uint32_t gx8002_uart_stage2_set_ldo_request_4428(uint32_t value)
{
    if (value == UINT32_MAX)
        return value;
    const uint32_t request = (value & 15u) | (1u << 4);
    (void)gx8002_uart_stage2_analog_request_4db8(8u, (const uint8_t *)&request);
    return 0;
}
