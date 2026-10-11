/* SPDX-License-Identifier: MIT
 * Named nondefault external IRQ vector wrappers from stock table 0x410040.
 * All callback bodies are source symbols; MMIO/device timing is untested.
 */
#include <stdint.h>
#include <stdbool.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define BYTE(address) (*(volatile uint8_t *)(uintptr_t)(address))
extern uint32_t opencfw_boot_uart_irq_row(uint32_t row);
extern uint32_t am_hal_mspi_interrupt_status_get(void *, uint32_t *, bool);
extern uint32_t am_hal_mspi_interrupt_clear(void *, uint32_t);
extern uint32_t am_hal_mspi_interrupt_service(void *, uint32_t);
extern uint32_t opencfw_boot_gpio_irq_status(uint32_t, uint32_t, uint32_t *);
extern uint32_t opencfw_boot_gpio_irq_clear(uint32_t, uint32_t);
extern uint32_t opencfw_boot_gpio_irq_service(uint32_t, uint32_t);
extern const int16_t opencfw_boot_gpio_irqnums[4];
extern void boost_service(void);

void opencfw_boot_uart_irq1(void)
{
    if (BYTE(UINT32_C(0x20000454) + 0x34u) == 1u)
        (void)opencfw_boot_uart_irq_row(1u);
}
void opencfw_boot_uart_irq2(void)
{
    if (BYTE(UINT32_C(0x20000454) + 0x50u) == 1u)
        (void)opencfw_boot_uart_irq_row(2u);
}
void opencfw_boot_uart_irq3(void)
{
    if (BYTE(UINT32_C(0x20000454) + 0x6cu) == 1u)
        (void)opencfw_boot_uart_irq_row(3u);
}
void opencfw_boot_mspi_irq(void)
{
    void *const handle = (void *)(uintptr_t)WORD(UINT32_C(0x200270dc));
    uint32_t status = 0u;
    (void)am_hal_mspi_interrupt_status_get(handle, &status, false);
    (void)am_hal_mspi_interrupt_clear(handle, status);
    (void)am_hal_mspi_interrupt_service(handle, status);
}
void opencfw_boot_spot_timer_irq(void)
{
    boost_service();
}
static void gpio_irq(uint32_t row)
{
    const volatile int16_t *const irqnums = opencfw_boot_gpio_irqnums;
    uint32_t status = 0u;
    (void)opencfw_boot_gpio_irq_status((uint32_t)(int32_t)irqnums[row], 0u,
                                       &status);
    (void)opencfw_boot_gpio_irq_clear((uint32_t)(int32_t)irqnums[row], status);
    (void)opencfw_boot_gpio_irq_service((uint32_t)(int32_t)irqnums[row], status);
}
void opencfw_boot_gpio_irq0(void) { gpio_irq(0u); }
void opencfw_boot_gpio_irq1(void) { gpio_irq(1u); }
void opencfw_boot_gpio_irq2(void) { gpio_irq(2u); }
