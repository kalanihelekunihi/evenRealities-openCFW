/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_RADIO_GPIO_H
#define OPENCFW_RADIO_GPIO_H
#include <stdint.h>
/* Reconstructed stock consumer, privileged ARM32 only. No pad setup or full radio boot.
 * Caller serializes publication and supplies the actual scheduler provider.
 * Counter wraps modulo2^32; callback ignores argument and posts event1.
 * No release, cancellation, or callback-lifetime guarantee is provided. */
void opencfw_radio_gpio_callback(void *);
uint32_t opencfw_radio_gpio_register(void);
void GPIO0_607F_IRQHandler(void);
/* Stock boot tail only: publication, GPIO enable, priority4, NVIC enable.
 * Does not initialize pads, tables, radio state or scheduler. Disable only
 * clears GPIO EN bit21; it does not unregister, clear pending or disable NVIC. */
void opencfw_radio_gpio_enable(void);
void opencfw_radio_gpio_disable(void);
void opencfw_radio_gpio_irq_setup(void);
/* Link-time provider boundary: stock call0x52b91e; semantics beyond event
 * submission are not implemented by this foundation. */
void opencfw_radio_scheduler_event(uint32_t handler_id,uint32_t event_mask);
#endif
