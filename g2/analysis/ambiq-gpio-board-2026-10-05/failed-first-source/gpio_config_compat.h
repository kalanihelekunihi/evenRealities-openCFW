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
 volatile uint32_t RD0,RD_rest[6];
 volatile uint32_t WT0,WT_rest[6];
 volatile uint32_t EN0,EN_rest[6];
 volatile uint32_t WTS0,WTS_rest[6];
 volatile uint32_t WTC0,WTC_rest[6];
 volatile uint32_t ENS0,ENS_rest[6];
 volatile uint32_t ENC0,ENC_rest[6];
} opencfw_gpio_config_registers_t;
#define GPIO ((opencfw_gpio_config_registers_t *)(uintptr_t)0x40010000u)
#define AM_CRITICAL_BEGIN uint32_t saved_primask=am_hal_interrupt_master_disable();
#define AM_CRITICAL_END __asm__ volatile("msr primask, %0" :: "r"(saved_primask) : "memory");
_Static_assert(sizeof(am_hal_gpio_pincfg_t)==4,"ARM by-value raw configuration word");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,PADKEY)==0x400,"stock unlock key");
#define AM_HAL_MASK32(n)        ((uint32_t)1 << ((n) & 0x1F))

#define AM_HAL_GPIO_RDn(pin)    ((volatile uint32_t *)&GPIO->RD0  + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_WTn(pin)    ((volatile uint32_t *)&GPIO->WT0  + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_WTCn(pin)   ((volatile uint32_t *)&GPIO->WTC0 + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_WTSn(pin)   ((volatile uint32_t *)&GPIO->WTS0 + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_ENn(pin)    ((volatile uint32_t *)&GPIO->EN0  + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_ENCn(pin)   ((volatile uint32_t *)&GPIO->ENC0 + (((pin) >> 5) & 0x7))
#define AM_HAL_GPIO_ENSn(pin)   ((volatile uint32_t *)&GPIO->ENS0 + (((pin) >> 5) & 0x7))

#define am_hal_gpio_output_clear(n)             (*AM_HAL_GPIO_WTCn((n)) = AM_HAL_MASK32(n))
#define am_hal_gpio_output_set(n)               (*AM_HAL_GPIO_WTSn((n)) = AM_HAL_MASK32(n))
#define am_hal_gpio_output_toggle(n)                                            \
    if ( 1 )                                                                    \
    {                                                                           \
        AM_CRITICAL_BEGIN                                                       \
        (*AM_HAL_GPIO_WTn((n)) ^= AM_HAL_MASK32(n));                            \
        AM_CRITICAL_END                                                         \
    }

#define am_hal_gpio_output_tristate_output_dis(n)  (*AM_HAL_GPIO_ENCn((n)) = AM_HAL_MASK32(n))
#define am_hal_gpio_output_tristate_output_en(n)   (*AM_HAL_GPIO_ENSn((n)) = AM_HAL_MASK32(n))
#define am_hal_gpio_output_tristate_output_tog(n)                                   \
    if ( 1 )                                                                    \
    {                                                                           \
        AM_CRITICAL_BEGIN                                                       \
        (*AM_HAL_GPIO_ENn((n)) ^=  AM_HAL_MASK32(n));                           \
        AM_CRITICAL_END                                                         \
    }
_Static_assert(offsetof(opencfw_gpio_config_registers_t,RD0)==0x404,"stock RD0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,WT0)==0x420,"stock WT0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,EN0)==0x43c,"stock EN0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,WTS0)==0x458,"stock WTS0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,WTC0)==0x474,"stock WTC0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,ENS0)==0x490,"stock ENS0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,ENC0)==0x4ac,"stock ENC0");
#endif
