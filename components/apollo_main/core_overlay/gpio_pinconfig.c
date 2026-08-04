/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 GPIO pin-configuration implementation adapted from
 * AmbiqSuite SDK am_hal_gpio_pinconfig(). The reviewed upstream revision and
 * exact G2 binary evidence are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_GPIO_CONFIG_WORDS
#define OPEN_CFW_GPIO_CONFIG_WORDS \
    ((volatile unsigned int *)0x40010000U)
#endif

#ifndef OPEN_CFW_GPIO_PADKEY
#define OPEN_CFW_GPIO_PADKEY \
    (*(volatile unsigned int *)0x40010400U)
#endif

#ifndef OPEN_CFW_GPIO_CRITICAL_ENTER
static inline unsigned int open_cfw_gpio_critical_enter(void)
{
    unsigned int interrupt_mask;

    __asm__ volatile(
        "mrs %0, primask\n"
        "cpsid i"
        : "=r"(interrupt_mask)
        :
        : "memory"
    );
    return interrupt_mask;
}
#define OPEN_CFW_GPIO_CRITICAL_ENTER() \
    open_cfw_gpio_critical_enter()
#endif

#ifndef OPEN_CFW_GPIO_CRITICAL_EXIT
static inline void open_cfw_gpio_critical_exit(
    unsigned int interrupt_mask
)
{
    __asm__ volatile(
        "msr primask, %0"
        :
        : "r"(interrupt_mask)
        : "memory"
    );
}
#define OPEN_CFW_GPIO_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_gpio_critical_exit(interrupt_mask)
#endif

#define OPEN_CFW_GPIO_TOTAL 224U
#define OPEN_CFW_GPIO_PADKEY_VALUE 0x73U

#define OPEN_CFW_GPIO_STATUS_SUCCESS 0U
#define OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE 5U
#define OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_GPIO_STATUS_INVALID_OPERATION 7U

static const unsigned int open_cfw_gpio_extended_drive[7] = {
    0x00000000U,
    0x00003FE0U,
    0x000003FFU,
    0x1FFBFE00U,
    0x0007C000U,
    0x00000000U,
    0x00000000U,
};

static const unsigned int open_cfw_gpio_drive_capable[7] = {
    0x8FC007E6U,
    0xE3F3FFFFU,
    0x81FFFFFFU,
    0xFFFFFFFFU,
    0xF00FC07FU,
    0x00000001U,
    0x00000189U,
};

/*
 * ABI-compatible source replacement for stock
 * 0x00480EEE...0x00480F0B.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_pinconfig_get(
    unsigned int gpio_number,
    unsigned int *configuration
)
{
    if (gpio_number >= OPEN_CFW_GPIO_TOTAL) {
        return OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE;
    }
    if (configuration == (unsigned int *)0) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    *configuration = OPEN_CFW_GPIO_CONFIG_WORDS[gpio_number];
    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00480F0C...0x00480F89. The configuration is the 32-bit GP.cfg word from
 * Ambiq's am_hal_gpio_pincfg_t.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_pinconfig(
    unsigned int gpio_number,
    unsigned int configuration
)
{
    unsigned int word_index;
    unsigned int bit;
    unsigned int interrupt_mask;

    if (gpio_number >= OPEN_CFW_GPIO_TOTAL) {
        return OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE;
    }

    word_index = gpio_number >> 5;
    bit = 1U << (gpio_number & 0x1FU);
    if ((open_cfw_gpio_extended_drive[word_index] & bit) == 0U) {
        unsigned int drive_strength = (configuration >> 10) & 3U;

        if (drive_strength > 1U &&
            (open_cfw_gpio_drive_capable[word_index] & bit) == 0U) {
            return OPEN_CFW_GPIO_STATUS_INVALID_OPERATION;
        }
    } else {
        unsigned int pull = (configuration >> 13) & 7U;

        if (pull != 0U && pull != 6U && pull != 1U) {
            return OPEN_CFW_GPIO_STATUS_INVALID_OPERATION;
        }
    }

    interrupt_mask = OPEN_CFW_GPIO_CRITICAL_ENTER();
    OPEN_CFW_GPIO_PADKEY = OPEN_CFW_GPIO_PADKEY_VALUE;
    OPEN_CFW_GPIO_CONFIG_WORDS[gpio_number] = configuration;
    OPEN_CFW_GPIO_PADKEY = 0;
    OPEN_CFW_GPIO_CRITICAL_EXIT(interrupt_mask);
    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}
