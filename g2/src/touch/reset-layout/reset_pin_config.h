/* SPDX-License-Identifier: MIT
 * Infineon CapSense v6 fifth-generation LP pin record ABI.
 */
#ifndef TOUCH_RESET_PIN_CONFIG_H
#define TOUCH_RESET_PIN_CONFIG_H
#include <stdint.h>
#include <stddef.h>
struct touch_pin_config { volatile uint32_t *port; uint8_t pin,pad; };
_Static_assert(sizeof(struct touch_pin_config)==8u,"LP pin ABI");
_Static_assert(offsetof(struct touch_pin_config,pad)==5u,"LP pad ABI");
extern const struct touch_pin_config touch_generated_pin_config[5];
#endif
