/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0 am_hal_syspll_lock_wait(),
 * authenticated at bootloader address 0x00427522.
 */

typedef __UINT32_TYPE__ open_cfw_syspll_lock_wait_u32;

typedef struct open_cfw_syspll_lock_wait_state {
    open_cfw_syspll_lock_wait_u32 prefix;
    open_cfw_syspll_lock_wait_u32 module;
} open_cfw_syspll_lock_wait_state;

#define OPEN_CFW_SYSPLL_LOCK_WAIT_HANDLE_MASK 0x01ffffffU
#define OPEN_CFW_SYSPLL_LOCK_WAIT_HANDLE_MAGIC 0x01504c30U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_INVALID_HANDLE 2U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_INVALID_OPERATION 7U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_CLOCK_SOURCE_MIN_MHZ 12U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_LOW_CYCLES 1000U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_HIGH_CYCLES 1875U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_VCOSELECT_BIT (1U << 9)
#define OPEN_CFW_SYSPLL_LOCK_WAIT_ENABLE_BIT (1U << 29)
#define OPEN_CFW_SYSPLL_LOCK_WAIT_REFDIV_MASK 0x3fU
#define OPEN_CFW_SYSPLL_LOCK_WAIT_LOCK_MASK 1U
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLSTAT_ADDRESS 0x400204e4U

#if defined(OPEN_CFW_SYSPLL_LOCK_WAIT_HOST_TEST)
extern open_cfw_syspll_lock_wait_u32
open_cfw_host_syspll_lock_wait_pllctl0_read(void);
extern open_cfw_syspll_lock_wait_u32
open_cfw_host_syspll_lock_wait_plldiv1_read(void);
extern open_cfw_syspll_lock_wait_u32
open_cfw_host_syspll_lock_wait_status_check(
    open_cfw_syspll_lock_wait_u32 timeout_us,
    open_cfw_syspll_lock_wait_u32 address,
    open_cfw_syspll_lock_wait_u32 mask,
    open_cfw_syspll_lock_wait_u32 expected,
    open_cfw_syspll_lock_wait_u32 equality);
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0_READ() \
    open_cfw_host_syspll_lock_wait_pllctl0_read()
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLDIV1_READ() \
    open_cfw_host_syspll_lock_wait_plldiv1_read()
#define OPEN_CFW_SYSPLL_LOCK_WAIT_STATUS_CHECK(timeout, address, mask, expected, equality) \
    open_cfw_host_syspll_lock_wait_status_check( \
        (timeout), (address), (mask), (expected), (equality))
#else
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0 \
    (*(volatile open_cfw_syspll_lock_wait_u32 *)0x400204d8U)
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLDIV1 \
    (*(volatile open_cfw_syspll_lock_wait_u32 *)0x400204e0U)
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0_READ() \
    (OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0)
#define OPEN_CFW_SYSPLL_LOCK_WAIT_PLLDIV1_READ() \
    (OPEN_CFW_SYSPLL_LOCK_WAIT_PLLDIV1)
extern open_cfw_syspll_lock_wait_u32
open_cfw_bootloader_delay_us_status_check_41d246(
    open_cfw_syspll_lock_wait_u32 timeout_us,
    open_cfw_syspll_lock_wait_u32 address,
    open_cfw_syspll_lock_wait_u32 mask,
    open_cfw_syspll_lock_wait_u32 expected,
    open_cfw_syspll_lock_wait_u32 equality);
#define OPEN_CFW_SYSPLL_LOCK_WAIT_STATUS_CHECK(timeout, address, mask, expected, equality) \
    open_cfw_bootloader_delay_us_status_check_41d246( \
        (timeout), (address), (mask), (expected), (equality))
#endif

__attribute__((used, noinline))
open_cfw_syspll_lock_wait_u32 open_cfw_bootloader_row6_lock_wait_427522(
    open_cfw_syspll_lock_wait_state *state)
{
    open_cfw_syspll_lock_wait_u32 pllctl0;
    open_cfw_syspll_lock_wait_u32 vco_select;
    open_cfw_syspll_lock_wait_u32 reference_divider;
    open_cfw_syspll_lock_wait_u32 maximum_cycles;
    open_cfw_syspll_lock_wait_u32 timeout_us;

    if (state == (open_cfw_syspll_lock_wait_state *)0 ||
            (state->prefix & OPEN_CFW_SYSPLL_LOCK_WAIT_HANDLE_MASK) !=
                OPEN_CFW_SYSPLL_LOCK_WAIT_HANDLE_MAGIC) {
        return OPEN_CFW_SYSPLL_LOCK_WAIT_INVALID_HANDLE;
    }

    /* Preserve the official volatile read ordering. */
    pllctl0 = OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0_READ();
    vco_select =
        (pllctl0 & OPEN_CFW_SYSPLL_LOCK_WAIT_VCOSELECT_BIT) >> 9;
    reference_divider = OPEN_CFW_SYSPLL_LOCK_WAIT_PLLDIV1_READ() &
        OPEN_CFW_SYSPLL_LOCK_WAIT_REFDIV_MASK;
    pllctl0 = OPEN_CFW_SYSPLL_LOCK_WAIT_PLLCTL0_READ();
    if ((pllctl0 & OPEN_CFW_SYSPLL_LOCK_WAIT_ENABLE_BIT) == 0U) {
        return OPEN_CFW_SYSPLL_LOCK_WAIT_INVALID_OPERATION;
    }

    maximum_cycles = vco_select == 1U ?
        OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_HIGH_CYCLES :
        OPEN_CFW_SYSPLL_LOCK_WAIT_VCO_LOW_CYCLES;
    timeout_us = maximum_cycles * reference_divider;
    timeout_us = (timeout_us +
        (OPEN_CFW_SYSPLL_LOCK_WAIT_CLOCK_SOURCE_MIN_MHZ - 1U)) /
        OPEN_CFW_SYSPLL_LOCK_WAIT_CLOCK_SOURCE_MIN_MHZ;

    return OPEN_CFW_SYSPLL_LOCK_WAIT_STATUS_CHECK(
        timeout_us,
        OPEN_CFW_SYSPLL_LOCK_WAIT_PLLSTAT_ADDRESS,
        OPEN_CFW_SYSPLL_LOCK_WAIT_LOCK_MASK,
        OPEN_CFW_SYSPLL_LOCK_WAIT_LOCK_MASK,
        1U);
}
