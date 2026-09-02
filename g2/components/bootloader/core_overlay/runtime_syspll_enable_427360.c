/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0 am_hal_syspll_enable(),
 * authenticated at bootloader address 0x00427360.  The exported name retains
 * the row-six client ABI used by the source-owned caller at 0x0042217E.
 */

typedef __UINT32_TYPE__ open_cfw_syspll_enable_u32;

typedef struct open_cfw_syspll_enable_state {
    open_cfw_syspll_enable_u32 prefix;
    open_cfw_syspll_enable_u32 module;
} open_cfw_syspll_enable_state;

#define OPEN_CFW_SYSPLL_ENABLE_HANDLE_MASK 0x01ffffffU
#define OPEN_CFW_SYSPLL_ENABLE_HANDLE_MAGIC 0x01504c30U
#define OPEN_CFW_SYSPLL_ENABLE_STATE_BIT 0x02000000U
#define OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_OVER (1U << 16)
#define OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_PDNB (1U << 17)
#define OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_RSTB (1U << 18)
#define OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_ACTIVE (1U << 19)
#define OPEN_CFW_SYSPLL_ENABLE_PLL_PDB (1U << 29)

#if defined(OPEN_CFW_SYSPLL_ENABLE_HOST_TEST)
extern open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_vrctrl_read(void);
extern open_cfw_syspll_enable_u32 open_cfw_host_syspll_enable_pllctl0_read(void);
extern void open_cfw_host_syspll_enable_pllctl0_write(
    open_cfw_syspll_enable_u32 value);
#define OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() \
    open_cfw_host_syspll_enable_vrctrl_read()
#define OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_READ() \
    open_cfw_host_syspll_enable_pllctl0_read()
#define OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_WRITE(value) \
    open_cfw_host_syspll_enable_pllctl0_write(value)
#else
#define OPEN_CFW_SYSPLL_ENABLE_VRCTRL \
    (*(volatile open_cfw_syspll_enable_u32 *)0x40020060U)
#define OPEN_CFW_SYSPLL_ENABLE_PLLCTL0 \
    (*(volatile open_cfw_syspll_enable_u32 *)0x400204d8U)
#define OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() \
    (OPEN_CFW_SYSPLL_ENABLE_VRCTRL)
#define OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_READ() \
    (OPEN_CFW_SYSPLL_ENABLE_PLLCTL0)
#define OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_WRITE(value) \
    (OPEN_CFW_SYSPLL_ENABLE_PLLCTL0 = (value))
#endif

__attribute__((used, noinline))
open_cfw_syspll_enable_u32 open_cfw_bootloader_row6_start_427360(
    open_cfw_syspll_enable_state *state)
{
    open_cfw_syspll_enable_u32 control;

    if (state == (open_cfw_syspll_enable_state *)0 ||
            (state->prefix & OPEN_CFW_SYSPLL_ENABLE_HANDLE_MASK) !=
                OPEN_CFW_SYSPLL_ENABLE_HANDLE_MAGIC) {
        return 2U;
    }

    if ((state->prefix & OPEN_CFW_SYSPLL_ENABLE_STATE_BIT) != 0U) {
        return 0U;
    }

    if ((OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() &
            OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_ACTIVE) == 0U ||
        (OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() &
            OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_RSTB) == 0U ||
        (OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() &
            OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_PDNB) == 0U ||
        (OPEN_CFW_SYSPLL_ENABLE_VRCTRL_READ() &
            OPEN_CFW_SYSPLL_ENABLE_SIMOBUCK_OVER) == 0U) {
        return 7U;
    }

    control = OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_ENABLE_PLLCTL0_WRITE(
        control | OPEN_CFW_SYSPLL_ENABLE_PLL_PDB);
    state->prefix |= OPEN_CFW_SYSPLL_ENABLE_STATE_BIT;
    return 0U;
}
