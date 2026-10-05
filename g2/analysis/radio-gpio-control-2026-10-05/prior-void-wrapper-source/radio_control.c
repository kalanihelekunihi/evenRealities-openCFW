/* SPDX-License-Identifier: MIT */
#include "gpio_config.h"
#include "gpio_interrupt_control.h"
/* Exact void wrappers from52dd58/52dd6a, called by radio boot/shutdown.
 * Local pin value is borrowed synchronously by HAL; returned status ignored.
 */
void opencfw_radio_irq_enable_exact(void)
{
    uint32_t pin=117u;
    (void)am_hal_gpio_interrupt_control(AM_HAL_GPIO_INT_CHANNEL_0,
                                      AM_HAL_GPIO_INT_CTRL_INDV_ENABLE,&pin);
}
void opencfw_radio_irq_disable_exact(void)
{
    uint32_t pin=117u;
    (void)am_hal_gpio_interrupt_control(AM_HAL_GPIO_INT_CHANNEL_0,
                                      AM_HAL_GPIO_INT_CTRL_INDV_DISABLE,&pin);
}
/* Reconstructed52eece; byte-truncated truth value, not strict boolean1. */
void opencfw_radio_pin136_gate_raw(uint32_t enabled)
{
    (void)am_hal_gpio_state_write(136u,(uint8_t)enabled ?
                                 AM_HAL_GPIO_OUTPUT_SET:AM_HAL_GPIO_OUTPUT_CLEAR);
}
void opencfw_radio_gpio_shutdown_phase(void)
{
    opencfw_radio_irq_disable_exact();
    opencfw_radio_pin136_gate_raw(0);
    opencfw_radio_gpio_idle_pins();
}
