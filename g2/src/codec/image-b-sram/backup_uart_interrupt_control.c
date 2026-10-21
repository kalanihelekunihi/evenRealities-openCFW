/* SPDX-License-Identifier: MIT
 * Image-B UART interrupt callback registration and removal at
 * 0x10004650/4684/46ac/46e0. The native port record is 0x80 bytes.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_irq_save_1000486c(void);
extern void gx8002_image_b_irq_restore_10004878(uint32_t previous);

static volatile uint32_t *port_record(uint32_t port)
{
    return (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
}

static void set_port_interrupt(volatile uint32_t *record,
                               uint32_t mask, uint32_t enabled)
{
    uint32_t previous = gx8002_image_b_irq_save_1000486c();
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)record[1];
    uint32_t control = registers[1];
    registers[1] = enabled ? control | mask : control & ~mask;
    gx8002_image_b_irq_restore_10004878(previous);
}

int32_t gx8002_image_b_uart_tx_irq_enable_10004650(
    uint32_t port, uint32_t callback, uint32_t context)
{
    volatile uint32_t *record = port_record(port);
    if (callback == 0u) return -1;
    record[0x44u / 4u] = 1u;
    record[0x48u / 4u] = callback;
    record[0x4cu / 4u] = context;
    set_port_interrupt(record, 2u, 1u);
    return 0;
}

int32_t gx8002_image_b_uart_tx_irq_disable_10004684(uint32_t port)
{
    volatile uint32_t *record = port_record(port);
    record[0x48u / 4u] = 0u;
    record[0x4cu / 4u] = 0u;
    set_port_interrupt(record, 2u, 0u);
    return 0;
}

int32_t gx8002_image_b_uart_rx_irq_enable_100046ac(
    uint32_t port, uint32_t callback, uint32_t context)
{
    volatile uint32_t *record = port_record(port);
    if (callback == 0u) return -1;
    record[0x40u / 4u] = 1u;
    record[0x50u / 4u] = callback;
    record[0x54u / 4u] = context;
    set_port_interrupt(record, 1u, 1u);
    return 0;
}

int32_t gx8002_image_b_uart_rx_irq_disable_100046e0(uint32_t port)
{
    volatile uint32_t *record = port_record(port);
    record[0x50u / 4u] = 0u;
    record[0x54u / 4u] = 0u;
    set_port_interrupt(record, 1u, 0u);
    return 0;
}
