/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_AMBIQ_GPIO_COMPAT_H
#define OPENCFW_AMBIQ_GPIO_COMPAT_H
#include "ambiq_gpio.h"
#include "../ambiq_mspi/ambiq_interrupt_mask.h"
#include <stddef.h>
_Static_assert(sizeof(void *)==4,"GPIO stock callback ABI is ARM32");
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_STATUS_OUT_OF_RANGE 5u
#define AM_HAL_STATUS_INVALID_ARG 6u
#define AM_HAL_STATUS_INVALID_OPERATION 7u
#define GPIO0_001F_IRQn 56u
#define GPIO0_C0DF_IRQn 62u
#define GPIO1_001F_IRQn 125u
#define GPIO1_C0DF_IRQn 131u
#define GPIO_INTX_DELTA 0x10u
#define GPIO_NXINT_DELTA 0x70u
#define GPIO_IRQ2N(irq) (((irq)>GPIO0_C0DF_IRQn)?1u:0u)
#define GPIO_IRQ2IDX(irq) (((irq)>=GPIO1_001F_IRQn)?((irq)-GPIO1_001F_IRQn):((irq)-GPIO0_001F_IRQn))
#define GPIO_NUM2IDX(pin) ((pin)/32u)
#define AM_REGVAL(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define AM_ASM_CLZ(value) __builtin_clz(value)
/* Sparse GPIO register view; does not initialize hardware. */
typedef struct {uint8_t opaque[0x530];volatile uint32_t MCUN0INT0EN,MCUN0INT0STAT,MCUN0INT0CLR;} opencfw_gpio_registers_t;
#define GPIO ((opencfw_gpio_registers_t *)(uintptr_t)0x40010000u)
_Static_assert(offsetof(opencfw_gpio_registers_t,MCUN0INT0STAT)==0x534,"stock IRQ status");
#define gpio_ppfnHandlers ((am_hal_gpio_handler_t (*)[32])(uintptr_t)0x20068228u)
#define gpio_pppvIrqArgs ((void * (*)[32])(uintptr_t)0x20068928u)
#define AM_CRITICAL_BEGIN uint32_t saved_primask=am_hal_interrupt_master_disable();
#define AM_CRITICAL_END __asm__ volatile("msr primask, %0" :: "r"(saved_primask) : "memory");
#endif
