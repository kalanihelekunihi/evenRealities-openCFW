/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 RTC calendar/time read adaptation from AmbiqSuite SDK
 * 5.1.0. The reviewed stock wrapper, HAL dependencies, register effects, and
 * host behavioral evidence are recorded in EVIDENCE.md.
 */

typedef struct open_cfw_rtc_get_time {
    unsigned int read_error;
    unsigned int weekday;
    unsigned int century_bit;
    unsigned int year;
    unsigned int month;
    unsigned int day;
    unsigned int hour;
    unsigned int minute;
    unsigned int second;
    unsigned int hundredths;
} open_cfw_rtc_get_time;

#define OPEN_CFW_RTC_GET_CLKGEN_OCTRL_ADDRESS 0x4000400CU
#define OPEN_CFW_RTC_GET_CONTROL_ADDRESS 0x40004800U
#define OPEN_CFW_RTC_GET_COUNTER_LOW_ADDRESS 0x40004820U
#define OPEN_CFW_RTC_GET_COUNTER_UP_ADDRESS 0x40004824U

#define OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS 0x400083C0U
#define OPEN_CFW_RTC_GET_TIMER_COUNTER_ADDRESS 0x400083C4U
#define OPEN_CFW_RTC_GET_TIMER_COMPARE0_ADDRESS 0x400083C8U
#define OPEN_CFW_RTC_GET_TIMER_COMPARE1_ADDRESS 0x400083CCU
#define OPEN_CFW_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS 0x40008010U

#define OPEN_CFW_RTC_GET_CLKGEN_LFRC_MASK 0x00000080U
#define OPEN_CFW_RTC_GET_TIMER_ENABLE_MASK 0x00000001U
#define OPEN_CFW_RTC_GET_TIMER_CLEAR_MASK 0x00000002U
#define OPEN_CFW_RTC_GET_TIMER14_GLOBAL_MASK 0x00004000U
#define OPEN_CFW_RTC_GET_TIMER_EDGE_FUNCTION 0x00000010U
#define OPEN_CFW_RTC_GET_TIMER_LFRC_CLOCK 0x00000600U
#define OPEN_CFW_RTC_GET_TIMER_XT_CLOCK 0x00000A00U

#ifndef OPEN_CFW_RTC_GET_READ
#define OPEN_CFW_RTC_GET_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_RTC_GET_WRITE
#define OPEN_CFW_RTC_GET_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_RTC_GET_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_RTC_GET_IRQ_DISABLE() open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_RTC_GET_IRQ_RESTORE
static __attribute__((always_inline)) inline void
open_cfw_rtc_get_irq_restore_target(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r"(primask)
        : "memory"
    );
}
#define OPEN_CFW_RTC_GET_IRQ_RESTORE(primask) \
    open_cfw_rtc_get_irq_restore_target(primask)
#endif

#ifndef OPEN_CFW_RTC_GET_DELAY_US
void open_cfw_delay_us(unsigned int microseconds);
#define OPEN_CFW_RTC_GET_DELAY_US(microseconds) \
    open_cfw_delay_us(microseconds)
#endif

static __attribute__((always_inline)) inline unsigned int
open_cfw_rtc_get_bcd_to_decimal(unsigned int value)
{
    unsigned int byte = value & 0xFFU;

    return ((byte >> 4U) * 10U) + (byte & 0xFU);
}

static __attribute__((always_inline)) inline void
open_cfw_rtc_get_poll_clock_edge(void)
{
    unsigned int control;
    unsigned int counter;
    unsigned int clock;

    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control & ~OPEN_CFW_RTC_GET_TIMER_ENABLE_MASK
    );

    clock = OPEN_CFW_RTC_GET_READ(OPEN_CFW_RTC_GET_CLKGEN_OCTRL_ADDRESS);
    control = OPEN_CFW_RTC_GET_TIMER_EDGE_FUNCTION
        | ((clock & OPEN_CFW_RTC_GET_CLKGEN_LFRC_MASK) != 0U
            ? OPEN_CFW_RTC_GET_TIMER_LFRC_CLOCK
            : OPEN_CFW_RTC_GET_TIMER_XT_CLOCK);
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_COMPARE0_ADDRESS,
        0xFFFFFFFFU
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_COMPARE1_ADDRESS,
        0xFFFFFFFFU
    );

    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS,
        control | OPEN_CFW_RTC_GET_TIMER14_GLOBAL_MASK
    );

    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control | OPEN_CFW_RTC_GET_TIMER_CLEAR_MASK
    );
    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control & ~OPEN_CFW_RTC_GET_TIMER_CLEAR_MASK
    );
    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control | OPEN_CFW_RTC_GET_TIMER_ENABLE_MASK
    );

    counter = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_COUNTER_ADDRESS
    );
    while (counter == OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_COUNTER_ADDRESS
    )) {
    }

    control = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
    );
    OPEN_CFW_RTC_GET_WRITE(
        OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS,
        control & ~OPEN_CFW_RTC_GET_TIMER_ENABLE_MASK
    );
    OPEN_CFW_RTC_GET_DELAY_US(10U);
}

/*
 * ABI-compatible source replacement for the void stock wrapper at
 * 0x0047EF10...0x0047EF17.
 */
__attribute__((used, noinline))
void open_cfw_rtc_time_get(open_cfw_rtc_get_time *time)
{
    unsigned int counter_low;
    unsigned int counter_up;
    unsigned int primask;

    primask = OPEN_CFW_RTC_GET_IRQ_DISABLE();
    open_cfw_rtc_get_poll_clock_edge();
    counter_low = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_COUNTER_LOW_ADDRESS
    );
    counter_up = OPEN_CFW_RTC_GET_READ(
        OPEN_CFW_RTC_GET_COUNTER_UP_ADDRESS
    );
    OPEN_CFW_RTC_GET_IRQ_RESTORE(primask);

    time->read_error = counter_up >> 31U;
    if (time->read_error != 0U) {
        return;
    }

    time->hour = open_cfw_rtc_get_bcd_to_decimal(
        (counter_low >> 24U) & 0x3FU
    );
    time->minute = open_cfw_rtc_get_bcd_to_decimal(
        (counter_low >> 16U) & 0x7FU
    );
    time->second = open_cfw_rtc_get_bcd_to_decimal(
        (counter_low >> 8U) & 0x7FU
    );
    time->hundredths = open_cfw_rtc_get_bcd_to_decimal(
        counter_low & 0xFFU
    );
    time->century_bit = (counter_up >> 28U) & 1U;
    time->weekday = open_cfw_rtc_get_bcd_to_decimal(
        (counter_up >> 24U) & 7U
    );
    time->year = open_cfw_rtc_get_bcd_to_decimal(
        (counter_up >> 16U) & 0xFFU
    );
    time->month = open_cfw_rtc_get_bcd_to_decimal(
        (counter_up >> 8U) & 0x1FU
    );
    time->day = open_cfw_rtc_get_bcd_to_decimal(counter_up & 0x3FU);
}

#undef OPEN_CFW_RTC_GET_DELAY_US
#undef OPEN_CFW_RTC_GET_IRQ_RESTORE
#undef OPEN_CFW_RTC_GET_IRQ_DISABLE
#undef OPEN_CFW_RTC_GET_WRITE
#undef OPEN_CFW_RTC_GET_READ
#undef OPEN_CFW_RTC_GET_TIMER_XT_CLOCK
#undef OPEN_CFW_RTC_GET_TIMER_LFRC_CLOCK
#undef OPEN_CFW_RTC_GET_TIMER_EDGE_FUNCTION
#undef OPEN_CFW_RTC_GET_TIMER14_GLOBAL_MASK
#undef OPEN_CFW_RTC_GET_TIMER_CLEAR_MASK
#undef OPEN_CFW_RTC_GET_TIMER_ENABLE_MASK
#undef OPEN_CFW_RTC_GET_CLKGEN_LFRC_MASK
#undef OPEN_CFW_RTC_GET_TIMER_GLOBAL_ENABLE_ADDRESS
#undef OPEN_CFW_RTC_GET_TIMER_COMPARE1_ADDRESS
#undef OPEN_CFW_RTC_GET_TIMER_COMPARE0_ADDRESS
#undef OPEN_CFW_RTC_GET_TIMER_COUNTER_ADDRESS
#undef OPEN_CFW_RTC_GET_TIMER_CONTROL_ADDRESS
#undef OPEN_CFW_RTC_GET_COUNTER_UP_ADDRESS
#undef OPEN_CFW_RTC_GET_COUNTER_LOW_ADDRESS
#undef OPEN_CFW_RTC_GET_CONTROL_ADDRESS
#undef OPEN_CFW_RTC_GET_CLKGEN_OCTRL_ADDRESS
