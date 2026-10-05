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
 volatile uint32_t WTS0,WTS_rest[6];
 volatile uint32_t WTC0,WTC_rest[6];
 volatile uint32_t EN0,EN_rest[6];
 volatile uint32_t ENS0,ENS_rest[6];
 volatile uint32_t ENC0,ENC_rest[6];
 uint8_t irq_reserved[0x530-0x4c8];
 volatile uint32_t MCUN0INT0EN,MCUN0INT0STAT,MCUN0INT0CLR,MCUN0INT0SET;
 volatile uint32_t MCUN0INT1EN,MCUN0INT1STAT,MCUN0INT1CLR,MCUN0INT1SET;
 volatile uint32_t MCUN0INT2EN,MCUN0INT2STAT,MCUN0INT2CLR,MCUN0INT2SET;
 volatile uint32_t MCUN0INT3EN,MCUN0INT3STAT,MCUN0INT3CLR,MCUN0INT3SET;
 volatile uint32_t MCUN0INT4EN,MCUN0INT4STAT,MCUN0INT4CLR,MCUN0INT4SET;
 volatile uint32_t MCUN0INT5EN,MCUN0INT5STAT,MCUN0INT5CLR,MCUN0INT5SET;
 volatile uint32_t MCUN0INT6EN,MCUN0INT6STAT,MCUN0INT6CLR,MCUN0INT6SET;
 volatile uint32_t MCUN1INT0EN,MCUN1INT0STAT,MCUN1INT0CLR,MCUN1INT0SET;
 volatile uint32_t MCUN1INT1EN,MCUN1INT1STAT,MCUN1INT1CLR,MCUN1INT1SET;
 volatile uint32_t MCUN1INT2EN,MCUN1INT2STAT,MCUN1INT2CLR,MCUN1INT2SET;
 volatile uint32_t MCUN1INT3EN,MCUN1INT3STAT,MCUN1INT3CLR,MCUN1INT3SET;
 volatile uint32_t MCUN1INT4EN,MCUN1INT4STAT,MCUN1INT4CLR,MCUN1INT4SET;
 volatile uint32_t MCUN1INT5EN,MCUN1INT5STAT,MCUN1INT5CLR,MCUN1INT5SET;
 volatile uint32_t MCUN1INT6EN,MCUN1INT6STAT,MCUN1INT6CLR,MCUN1INT6SET;
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
_Static_assert(offsetof(opencfw_gpio_config_registers_t,EN0)==0x474,"stock EN0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,WTS0)==0x43c,"stock WTS0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,WTC0)==0x458,"stock WTC0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,ENS0)==0x490,"stock ENS0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,ENC0)==0x4ac,"stock ENC0");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,MCUN0INT0EN)==0x530,"stock channel0 EN");
_Static_assert(offsetof(opencfw_gpio_config_registers_t,MCUN1INT0EN)==0x5a0,"stock channel1 EN");
#endif
