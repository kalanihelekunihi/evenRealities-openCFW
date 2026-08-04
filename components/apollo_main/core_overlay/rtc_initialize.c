/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 RTC clock initialization adapted from AmbiqSuite SDK
 * 5.1.0. The reviewed stock span, initializer-table entry, register effects,
 * and host behavioral evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS 0x4000400CU
#define OPEN_CFW_RTC_CLKGEN_OSEL_MASK 0x00000080U
#define OPEN_CFW_RTC_CONTROL_ADDRESS 0x40004800U
#define OPEN_CFW_RTC_STOP_MASK 0x00000010U

#ifndef OPEN_CFW_RTC_READ
#define OPEN_CFW_RTC_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_RTC_WRITE
#define OPEN_CFW_RTC_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

/*
 * ABI-compatible source replacement for stock
 * 0x0047EE60...0x0047EE77.
 */
__attribute__((used, noinline))
unsigned int open_cfw_rtc_initialize(void)
{
    unsigned int value;

    /*
     * The stock initializer selects XTAL once through clkgen_control() and
     * once through rtc_osc_select(). Both operations are observable volatile
     * read/modify/writes of CLKGEN.OCTRL.OSEL and are intentionally retained.
     */
    value = OPEN_CFW_RTC_READ(OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS);
    OPEN_CFW_RTC_WRITE(
        OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS,
        value & ~OPEN_CFW_RTC_CLKGEN_OSEL_MASK
    );
    value = OPEN_CFW_RTC_READ(OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS);
    OPEN_CFW_RTC_WRITE(
        OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS,
        value & ~OPEN_CFW_RTC_CLKGEN_OSEL_MASK
    );

    /*
     * Apollo510 encodes RTCCTL.RSTOP=0 as RUN. This is the complete register
     * effect of the stock rtc_osc_enable() dependency.
     */
    value = OPEN_CFW_RTC_READ(OPEN_CFW_RTC_CONTROL_ADDRESS);
    OPEN_CFW_RTC_WRITE(
        OPEN_CFW_RTC_CONTROL_ADDRESS,
        value & ~OPEN_CFW_RTC_STOP_MASK
    );

    return 0U;
}

#undef OPEN_CFW_RTC_WRITE
#undef OPEN_CFW_RTC_READ
#undef OPEN_CFW_RTC_STOP_MASK
#undef OPEN_CFW_RTC_CONTROL_ADDRESS
#undef OPEN_CFW_RTC_CLKGEN_OSEL_MASK
#undef OPEN_CFW_RTC_CLKGEN_OCTRL_ADDRESS
