/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 GPIO interrupt implementation adapted from AmbiqSuite SDK
 * interrupt index, control, status, clear, registration, and service
 * routines. Evidence is recorded in EVIDENCE.md.
 */

#ifndef OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD
#define OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(channel, index) \
    (*(volatile unsigned int *)( \
        0x40010530U + ((channel) * 0x70U) + ((index) * 0x10U) \
    ))
#endif

#ifndef OPEN_CFW_GPIO_INTERRUPT_STATUS_WORD
#define OPEN_CFW_GPIO_INTERRUPT_STATUS_WORD(channel, index) \
    (*(volatile unsigned int *)( \
        0x40010534U + ((channel) * 0x70U) + ((index) * 0x10U) \
    ))
#endif

#ifndef OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD
#define OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD(channel, index) \
    (*(volatile unsigned int *)( \
        0x40010538U + ((channel) * 0x70U) + ((index) * 0x10U) \
    ))
#endif

#ifndef OPEN_CFW_GPIO_INTERRUPT_POST_CLEAR_READ
#define OPEN_CFW_GPIO_INTERRUPT_POST_CLEAR_READ() \
    ((void)OPEN_CFW_GPIO_INTERRUPT_STATUS_WORD( \
        OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1, \
        OPEN_CFW_GPIO_INTERRUPT_WORDS - 1U \
    ))
#endif

#ifndef OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER
static inline unsigned int open_cfw_gpio_interrupt_critical_enter(void)
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
#define OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER() \
    open_cfw_gpio_interrupt_critical_enter()
#endif

#ifndef OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT
static inline void open_cfw_gpio_interrupt_critical_exit(
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
#define OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_gpio_interrupt_critical_exit(interrupt_mask)
#endif

#define OPEN_CFW_GPIO_TOTAL 224U
#define OPEN_CFW_GPIO_INTERRUPT_WORDS 7U

#define OPEN_CFW_GPIO_STATUS_SUCCESS 0U
#define OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE 5U
#define OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT 6U
#define OPEN_CFW_GPIO_STATUS_INVALID_OPERATION 7U

#define OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0 0U
#define OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1 1U
#define OPEN_CFW_GPIO_INTERRUPT_CHANNEL_BOTH 2U

#define OPEN_CFW_GPIO_INTERRUPT_INDIVIDUAL_DISABLE 0U
#define OPEN_CFW_GPIO_INTERRUPT_INDIVIDUAL_ENABLE 1U
#define OPEN_CFW_GPIO_INTERRUPT_MASK_DISABLE 2U
#define OPEN_CFW_GPIO_INTERRUPT_MASK_ENABLE 3U

#define OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST 56U
#define OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST 62U
#define OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST 125U
#define OPEN_CFW_GPIO_IRQ_CHANNEL_1_LAST 131U

typedef void (*open_cfw_gpio_handler_t)(void *);

#ifndef OPEN_CFW_GPIO_HANDLER_ENTRY
#define OPEN_CFW_GPIO_HANDLER_ENTRY(index, bit) \
    (*(open_cfw_gpio_handler_t volatile *)( \
        0x20068228U + ((index) * 128U) + ((bit) * 4U) \
    ))
#endif

#ifndef OPEN_CFW_GPIO_HANDLER_ARGUMENT
#define OPEN_CFW_GPIO_HANDLER_ARGUMENT(index, bit) \
    (*(void * volatile *)( \
        0x20068928U + ((index) * 128U) + ((bit) * 4U) \
    ))
#endif

/*
 * ABI-compatible source replacement for stock
 * 0x00480ED8...0x00480EED. The stock helper performs no range or null checks.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_index(
    unsigned int gpio_number,
    unsigned int *register_index,
    unsigned int *bit_mask
)
{
    *register_index = gpio_number >> 5;
    *bit_mask = 1U << (gpio_number & 0x1FU);
    return 0;
}

/*
 * ABI-compatible source replacement for stock
 * 0x004810B0...0x004812F5. Both enum arguments are truncated to eight bits,
 * matching the reviewed G2 compiler output.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_control(
    unsigned int channel,
    unsigned int control,
    void *gpio_mask_or_number
)
{
    volatile unsigned int *gpio_mask;
    unsigned int channel_value = (unsigned char)channel;
    unsigned int control_value = (unsigned char)control;
    unsigned int register_channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0;
    unsigned int register_index = 0;
    unsigned int bit_mask = 0;
    unsigned int interrupt_mask;
    unsigned int word;

    if (gpio_mask_or_number == (void *)0) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }
    if (control_value > OPEN_CFW_GPIO_INTERRUPT_MASK_ENABLE) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    gpio_mask = (volatile unsigned int *)gpio_mask_or_number;
    if (control_value <= OPEN_CFW_GPIO_INTERRUPT_INDIVIDUAL_ENABLE) {
        unsigned int gpio_number = gpio_mask[0];

        if (gpio_number >= OPEN_CFW_GPIO_TOTAL) {
            return OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE;
        }
        if (open_cfw_gpio_interrupt_index(
                gpio_number,
                &register_index,
                &bit_mask
            ) != OPEN_CFW_GPIO_STATUS_SUCCESS) {
            return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
        }
        if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
            register_channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1;
        }
    }

    interrupt_mask = OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER();
    switch (control_value) {
    case OPEN_CFW_GPIO_INTERRUPT_INDIVIDUAL_DISABLE:
        OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
            register_channel,
            register_index
        ) &= ~bit_mask;
        if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_BOTH) {
            OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1,
                register_index
            ) &= ~bit_mask;
        }
        break;
    case OPEN_CFW_GPIO_INTERRUPT_INDIVIDUAL_ENABLE:
        OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
            register_channel,
            register_index
        ) |= bit_mask;
        if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_BOTH) {
            OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1,
                register_index
            ) |= bit_mask;
        }
        break;
    case OPEN_CFW_GPIO_INTERRUPT_MASK_DISABLE:
        if (channel_value != OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
            for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
                OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                    OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0,
                    word
                ) &= ~gpio_mask[word];
            }
        }
        if (channel_value != OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0) {
            for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
                OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                    OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1,
                    word
                ) &= ~gpio_mask[word];
            }
        }
        break;
    case OPEN_CFW_GPIO_INTERRUPT_MASK_ENABLE:
        if (channel_value != OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
            for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
                OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                    OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0,
                    word
                ) |= gpio_mask[word];
            }
        }
        if (channel_value != OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0) {
            for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
                OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                    OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1,
                    word
                ) |= gpio_mask[word];
            }
        }
        break;
    default:
        break;
    }
    OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask);

    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x004812F6...0x00481467. The reviewed stock function does not validate the
 * destination pointer; callers must provide seven writable words.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_status_get(
    unsigned int channel,
    unsigned int enabled_only,
    unsigned int *gpio_mask
)
{
    volatile unsigned int enable_mask[OPEN_CFW_GPIO_INTERRUPT_WORDS];
    unsigned int channel_value = (unsigned char)channel;
    unsigned int interrupt_mask;
    unsigned int result = OPEN_CFW_GPIO_STATUS_SUCCESS;
    unsigned int word;

    for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
        enable_mask[word] = 0xFFFFFFFFU;
    }

    interrupt_mask = OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER();
    if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0 ||
        channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
        if ((unsigned char)enabled_only != 0U) {
            for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
                enable_mask[word] =
                    OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(
                        channel_value,
                        word
                    );
            }
        }
        for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
            gpio_mask[word] =
                OPEN_CFW_GPIO_INTERRUPT_STATUS_WORD(channel_value, word) &
                enable_mask[word];
        }
    } else {
        result = OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }
    OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask);

    return result;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00481468...0x00481573.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_clear(
    unsigned int channel,
    volatile unsigned int *gpio_mask
)
{
    unsigned int channel_value = (unsigned char)channel;
    unsigned int interrupt_mask;
    unsigned int word;

    if (gpio_mask == (volatile unsigned int *)0) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_BOTH) {
        interrupt_mask = OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER();
        for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
            OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD(
                OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0,
                word
            ) = gpio_mask[word];
        }
        for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
            OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD(
                OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1,
                word
            ) = gpio_mask[word];
        }
        OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask);
    } else if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0 ||
               channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
        interrupt_mask = OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER();
        for (word = 0; word < OPEN_CFW_GPIO_INTERRUPT_WORDS; ++word) {
            OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD(channel_value, word) =
                gpio_mask[word];
        }
        OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask);
    }

    OPEN_CFW_GPIO_INTERRUPT_POST_CLEAR_READ();
    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00481574...0x004815F1.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_irq_status_get(
    unsigned int gpio_irq,
    unsigned int enabled_only,
    unsigned int *interrupt_status
)
{
    unsigned int channel;
    unsigned int register_index;
    unsigned int interrupt_mask;

    if (interrupt_status == (unsigned int *)0 ||
        gpio_irq < OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST ||
        (gpio_irq > OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST &&
         gpio_irq < OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST) ||
        gpio_irq > OPEN_CFW_GPIO_IRQ_CHANNEL_1_LAST) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    if (gpio_irq <= OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST) {
        channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0;
        register_index =
            gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST;
    } else {
        channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1;
        register_index =
            gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST;
    }

    interrupt_mask = OPEN_CFW_GPIO_INTERRUPT_CRITICAL_ENTER();
    if ((unsigned char)enabled_only != 0U) {
        *interrupt_status =
            OPEN_CFW_GPIO_INTERRUPT_ENABLE_WORD(channel, register_index);
    } else {
        *interrupt_status = 0xFFFFFFFFU;
    }
    *interrupt_status &=
        OPEN_CFW_GPIO_INTERRUPT_STATUS_WORD(channel, register_index);
    OPEN_CFW_GPIO_INTERRUPT_CRITICAL_EXIT(interrupt_mask);

    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x004815F2...0x0048162B.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_irq_clear(
    unsigned int gpio_irq,
    unsigned int interrupt_status
)
{
    unsigned int channel;
    unsigned int register_index;

    if (gpio_irq < OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST ||
        (gpio_irq > OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST &&
         gpio_irq < OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST) ||
        gpio_irq > OPEN_CFW_GPIO_IRQ_CHANNEL_1_LAST) {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    if (gpio_irq <= OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST) {
        channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0;
        register_index =
            gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST;
    } else {
        channel = OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1;
        register_index =
            gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST;
    }
    OPEN_CFW_GPIO_INTERRUPT_CLEAR_WORD(channel, register_index) =
        interrupt_status;

    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x0048162C...0x004816C5. The reviewed stock routine intentionally performs
 * no GPIO-number range validation.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_register(
    unsigned int channel,
    unsigned int gpio_number,
    open_cfw_gpio_handler_t handler,
    void *argument
)
{
    unsigned int channel_value = (unsigned char)channel;
    unsigned int channel_0_index = gpio_number >> 5;
    unsigned int channel_1_index = channel_0_index + 7U;
    unsigned int bit = gpio_number & 0x1FU;

    if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_0) {
        OPEN_CFW_GPIO_HANDLER_ENTRY(channel_0_index, bit) = handler;
        OPEN_CFW_GPIO_HANDLER_ARGUMENT(channel_0_index, bit) = argument;
    } else if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_1) {
        OPEN_CFW_GPIO_HANDLER_ENTRY(channel_1_index, bit) = handler;
        OPEN_CFW_GPIO_HANDLER_ARGUMENT(channel_1_index, bit) = argument;
    } else if (channel_value == OPEN_CFW_GPIO_INTERRUPT_CHANNEL_BOTH) {
        OPEN_CFW_GPIO_HANDLER_ENTRY(channel_0_index, bit) = handler;
        OPEN_CFW_GPIO_HANDLER_ARGUMENT(channel_0_index, bit) = argument;
        OPEN_CFW_GPIO_HANDLER_ENTRY(channel_1_index, bit) = handler;
        OPEN_CFW_GPIO_HANDLER_ARGUMENT(channel_1_index, bit) = argument;
    } else {
        return OPEN_CFW_GPIO_STATUS_INVALID_ARGUMENT;
    }

    return OPEN_CFW_GPIO_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x004816C6...0x00481739.
 */
__attribute__((used, noinline))
unsigned int open_cfw_gpio_interrupt_service(
    unsigned int gpio_irq,
    unsigned int interrupt_status
)
{
    unsigned int handler_index;
    unsigned int result = OPEN_CFW_GPIO_STATUS_SUCCESS;

    if (!((gpio_irq >= OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST &&
           gpio_irq <= OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST) ||
          (gpio_irq >= OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST &&
           gpio_irq <= OPEN_CFW_GPIO_IRQ_CHANNEL_1_LAST))) {
        return OPEN_CFW_GPIO_STATUS_OUT_OF_RANGE;
    }

    if (gpio_irq <= OPEN_CFW_GPIO_IRQ_CHANNEL_0_LAST) {
        handler_index = gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_0_FIRST;
    } else {
        handler_index =
            gpio_irq - OPEN_CFW_GPIO_IRQ_CHANNEL_1_FIRST + 7U;
    }

    while (interrupt_status != 0U) {
        unsigned int lowest_bit = interrupt_status & (0U - interrupt_status);
        unsigned int bit = 31U - (unsigned int)__builtin_clz(lowest_bit);
        open_cfw_gpio_handler_t handler;
        void *argument;

        interrupt_status &= ~(1U << bit);
        handler = OPEN_CFW_GPIO_HANDLER_ENTRY(handler_index, bit);
        argument = OPEN_CFW_GPIO_HANDLER_ARGUMENT(handler_index, bit);
        if (handler != (open_cfw_gpio_handler_t)0) {
            handler(argument);
        } else {
            result = OPEN_CFW_GPIO_STATUS_INVALID_OPERATION;
        }
    }

    return result;
}
