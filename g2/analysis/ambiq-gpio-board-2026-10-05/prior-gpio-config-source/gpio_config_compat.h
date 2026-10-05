/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_GPIO_CONFIG_COMPAT_H
#define OPENCFW_GPIO_CONFIG_COMPAT_H
#include "gpio_config.h"
#include "../ambiq_mspi/ambiq_interrupt_mask.h"
#include <stddef.h>
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_STATUS_OUT_OF_RANGE 5u
#define AM_HAL_STATUS_INVALID_ARG 6u
#define AM_HAL_STATUS_INVALID_OPERATION 7u
#define AM_HAL_PIN_TOTAL_GPIOS 224u
#define AM_HAL_GPIO_PIN_DRIVESTRENGTH_0P5X 1u
#define AM_HAL_GPIO_PIN_PULLUP_NONE 0u
#define AM_HAL_GPIO_PIN_PULLDOWN_50K 1u
#define AM_HAL_GPIO_PIN_PULLUP_50K 6u
#define GPIO_PADKEY_PADKEY_Key 0x73u
typedef struct {
 volatile uint32_t PINCFG0;
 volatile uint32_t other_pinconfigs[223];
 uint8_t reserved[0x80];
 volatile uint32_t PADKEY;
} opencfw_gpio_config_registers_t;
#define GPIO ((opencfw_gpio_config_registers_t *)(uintptr_t)0x40010000u)
#define AM_CRITICAL_BEGIN uint32_t saved_primask=am_hal_interrupt_master_disable();
#define AM_CRITICAL_END __asm__ volatile("msr primask, %0" :: "r"(saved_primask) : "memory");
_Static_assert(sizeof(am_hal_gpio_pincfg_t)==4,"ARM by-value raw configuration word");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,PADKEY)==0x400,"stock unlock key");
#endif
