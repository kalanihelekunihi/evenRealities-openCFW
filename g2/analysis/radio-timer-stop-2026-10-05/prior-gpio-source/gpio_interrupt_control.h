/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_GPIO_INTERRUPT_CONTROL_H
#define OPENCFW_GPIO_INTERRUPT_CONTROL_H
#include "../ambiq_gpio/ambiq_gpio.h"
typedef uint8_t am_hal_gpio_int_ctrl_e;
enum { AM_HAL_GPIO_INT_CTRL_INDV_DISABLE, AM_HAL_GPIO_INT_CTRL_INDV_ENABLE,
       AM_HAL_GPIO_INT_CTRL_MASK_DISABLE, AM_HAL_GPIO_INT_CTRL_MASK_ENABLE,
       AM_HAL_GPIO_INT_CTRL_LAST=AM_HAL_GPIO_INT_CTRL_MASK_ENABLE };
/* Compatible seven-word view of the upstream volatile mask union. */
typedef struct { union { volatile uint32_t Msk[7]; } U; } am_hal_gpio_mask_t;
/* input: readable u32 pin for individual control, readable seven-word mask
 * for mask control. Synchronous borrowing only; no retained input pointer.
 * Stock does not reject channels outside0..2; use raw adapter for diagnostics.
 */
uint32_t am_hal_gpio_interrupt_control(am_hal_gpio_int_channel_e,am_hal_gpio_int_ctrl_e,void *);
uint32_t opencfw_gpio_interrupt_control_raw(uint32_t,uint32_t,void *);
uint32_t opencfw_radio_irq_enable_exact(void);
uint32_t opencfw_radio_irq_disable_exact(void);
void opencfw_radio_pin136_gate_raw(uint32_t);
/* Reconstructed GPIO-only contiguous shutdown slice4b49d8..4b49e6.
 * Timer stop, transport release and state clearing are outside this slice.
 */
void opencfw_radio_gpio_shutdown_phase(void);
#endif
