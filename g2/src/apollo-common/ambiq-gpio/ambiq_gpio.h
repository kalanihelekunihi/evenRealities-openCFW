/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AMBIQ_GPIO_H
#define OPENCFW_AMBIQ_GPIO_H
#include <stdbool.h>
#include <stdint.h>
typedef void (*am_hal_gpio_handler_t)(void *);
typedef enum {AM_HAL_GPIO_INT_CHANNEL_0=0,AM_HAL_GPIO_INT_CHANNEL_1=1,AM_HAL_GPIO_INT_CHANNEL_BOTH=2} am_hal_gpio_int_channel_e;
/* ARM32 stock subset. Status requires a mapped writable uint32 output and
 * privileged execution. Initialization and serialized access are caller duties.
 * IRQ56..62 and125..131 map seven banks per channel.
 * Registration validates channel ONLY: caller validates physical pin/bank<7,
 * callback/argument lifetime and prevents concurrent publication/dispatch.
 * Service visits mask bits in ascending order, reads live callback slots, and
 * continues after missing callbacks. Clear writes a mask without waiting. */
uint32_t am_hal_gpio_interrupt_irq_status_get(uint32_t,bool,uint32_t *);
uint32_t am_hal_gpio_interrupt_irq_clear(uint32_t,uint32_t);
uint32_t am_hal_gpio_interrupt_register(am_hal_gpio_int_channel_e,uint32_t,am_hal_gpio_handler_t,void *);
uint32_t am_hal_gpio_interrupt_service(uint32_t,uint32_t);
#endif
