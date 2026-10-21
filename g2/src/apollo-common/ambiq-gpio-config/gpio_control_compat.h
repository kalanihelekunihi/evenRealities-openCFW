/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_GPIO_CONTROL_COMPAT_H
#define OPENCFW_GPIO_CONTROL_COMPAT_H
#include "gpio_config_compat.h"
#include "gpio_interrupt_control.h"
#define AM_HAL_GPIO_MAX_PADS 224u
#define GPIO_INTX_DELTA 0x10u
#define GPIO_NXINT_DELTA 0x70u
#define AM_REGVAL(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define DIAG_SUPPRESS_VOLATILE_ORDER()
#define DIAG_DEFAULT_VOLATILE_ORDER()
#endif
