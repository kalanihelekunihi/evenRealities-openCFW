/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 GPIO-state implementation adapted from AmbiqSuite SDK
 * am_hal_gpio_state_read(). The reviewed upstream revision and binary evidence
 * are recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_GPIO_INPUT_WORDS
#define OPEN_CFW_GPIO_INPUT_WORDS \
    ((volatile unsigned int *)0x40010404U)
#endif

#ifndef OPEN_CFW_GPIO_OUTPUT_WORDS
#define OPEN_CFW_GPIO_OUTPUT_WORDS \
    ((volatile unsigned int *)0x40010420U)
#endif

#ifndef OPEN_CFW_GPIO_ENABLE_WORDS
#define OPEN_CFW_GPIO_ENABLE_WORDS \
    ((volatile unsigned int *)0x40010474U)
#endif

#ifndef OPEN_CFW_GPIO_OUTPUT_CLEAR_WORDS
#define OPEN_CFW_GPIO_OUTPUT_CLEAR_WORDS \
    ((volatile unsigned int *)0x40010458U)
#endif

#ifndef OPEN_CFW_GPIO_OUTPUT_SET_WORDS
#define OPEN_CFW_GPIO_OUTPUT_SET_WORDS \
    ((volatile unsigned int *)0x4001043CU)
#endif

#ifndef OPEN_CFW_GPIO_ENABLE_CLEAR_WORDS
#define OPEN_CFW_GPIO_ENABLE_CLEAR_WORDS \
    ((volatile unsigned int *)0x400104ACU)
#endif

#ifndef OPEN_CFW_GPIO_ENABLE_SET_WORDS
#define OPEN_CFW_GPIO_ENABLE_SET_WORDS \
    ((volatile unsigned int *)0x40010490U)
#endif

#ifndef OPEN_CFW_GPIO_WRITE_CRITICAL_ENTER
static inline unsigned int open_cfw_gpio_write_critical_enter(void)
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
#define OPEN_CFW_GPIO_WRITE_CRITICAL_ENTER() \
    open_cfw_gpio_write_critical_enter()
#endif

#ifndef OPEN_CFW_GPIO_WRITE_CRITICAL_EXIT
static inline void open_cfw_gpio_write_critical_exit(
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
#define OPEN_CFW_GPIO_WRITE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_gpio_write_critical_exit(interrupt_mask)
#endif

#define OPEN_CFW_GPIO_STATUS_SUCCESS 0U
#define OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT 6U

#define OPEN_CFW_GPIO_INPUT_READ 0U
#define OPEN_CFW_GPIO_OUTPUT_READ 1U
#define OPEN_CFW_GPIO_ENABLE_READ 2U

#define OPEN_CFW_GPIO_OUTPUT_CLEAR 0U
#define OPEN_CFW_GPIO_OUTPUT_SET 1U
#define OPEN_CFW_GPIO_OUTPUT_TOGGLE 2U
#define OPEN_CFW_GPIO_TRISTATE_DISABLE 3U
#define OPEN_CFW_GPIO_TRISTATE_ENABLE 4U
#define OPEN_CFW_GPIO_TRISTATE_TOGGLE 5U

/*
 * ABI-compatible source replacement for stock
 * 0x00480F8A...0x00480FD5. The stock function truncates the read selector to
 * eight bits and the GPIO word index to three bits; retain both behaviors.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_state_read(
    unsigned int gpio_number,
    unsigned int read_type,
    unsigned int *read_state
)
{
    volatile unsigned int *target;

    switch ((unsigned char)read_type) {
    case OPEN_CFW_GPIO_INPUT_READ:
        target = OPEN_CFW_GPIO_INPUT_WORDS;
        break;
    case OPEN_CFW_GPIO_OUTPUT_READ:
        target = OPEN_CFW_GPIO_OUTPUT_WORDS;
        break;
    case OPEN_CFW_GPIO_ENABLE_READ:
        target = OPEN_CFW_GPIO_ENABLE_WORDS;
        break;
    default:
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    *read_state =
        (target[(gpio_number & 0xFFU) >> 5] >>
         (gpio_number & 0x1FU)) &
        1U;
    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00480FD6...0x004810AF. Ambiq's state-write API always returns success,
 * including for an unrecognized selector.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_state_write(
    unsigned int gpio_number,
    unsigned int write_type
)
{
    unsigned int word_index = (gpio_number & 0xFFU) >> 5;
    unsigned int bit = 1U << (gpio_number & 0x1FU);
    unsigned int interrupt_mask;

    switch ((unsigned char)write_type) {
    case OPEN_CFW_GPIO_OUTPUT_CLEAR:
        OPEN_CFW_GPIO_OUTPUT_CLEAR_WORDS[word_index] = bit;
        break;
    case OPEN_CFW_GPIO_OUTPUT_SET:
        OPEN_CFW_GPIO_OUTPUT_SET_WORDS[word_index] = bit;
        break;
    case OPEN_CFW_GPIO_OUTPUT_TOGGLE:
        interrupt_mask = OPEN_CFW_GPIO_WRITE_CRITICAL_ENTER();
        OPEN_CFW_GPIO_OUTPUT_WORDS[word_index] ^= bit;
        OPEN_CFW_GPIO_WRITE_CRITICAL_EXIT(interrupt_mask);
        break;
    case OPEN_CFW_GPIO_TRISTATE_DISABLE:
        OPEN_CFW_GPIO_ENABLE_CLEAR_WORDS[word_index] = bit;
        break;
    case OPEN_CFW_GPIO_TRISTATE_ENABLE:
        OPEN_CFW_GPIO_ENABLE_SET_WORDS[word_index] = bit;
        break;
    case OPEN_CFW_GPIO_TRISTATE_TOGGLE:
        interrupt_mask = OPEN_CFW_GPIO_WRITE_CRITICAL_ENTER();
        OPEN_CFW_GPIO_ENABLE_WORDS[word_index] ^= bit;
        OPEN_CFW_GPIO_WRITE_CRITICAL_EXIT(interrupt_mask);
        break;
    default:
        break;
    }

    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}
