/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0 am_hal_syspll_disable(),
 * authenticated at bootloader address 0x004273DC.  The exported name retains
 * the row-six client ABI used by the source-owned lifecycle callers.
 */

typedef __UINT32_TYPE__ open_cfw_syspll_disable_u32;

typedef struct open_cfw_syspll_disable_state {
    open_cfw_syspll_disable_u32 prefix;
    open_cfw_syspll_disable_u32 module;
} open_cfw_syspll_disable_state;

#define OPEN_CFW_SYSPLL_DISABLE_HANDLE_MASK 0x01ffffffU
#define OPEN_CFW_SYSPLL_DISABLE_HANDLE_MAGIC 0x01504c30U
#define OPEN_CFW_SYSPLL_DISABLE_STATE_BIT 0x02000000U
#define OPEN_CFW_SYSPLL_DISABLE_PLL_PDB (1U << 29)

#if defined(OPEN_CFW_SYSPLL_DISABLE_HOST_TEST)
extern open_cfw_syspll_disable_u32
open_cfw_host_syspll_disable_pllctl0_read(void);
extern void open_cfw_host_syspll_disable_pllctl0_write(
    open_cfw_syspll_disable_u32 value);
#define OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_READ() \
    open_cfw_host_syspll_disable_pllctl0_read()
#define OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_WRITE(value) \
    open_cfw_host_syspll_disable_pllctl0_write(value)
#else
#define OPEN_CFW_SYSPLL_DISABLE_PLLCTL0 \
    (*(volatile open_cfw_syspll_disable_u32 *)0x400204d8U)
#define OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_READ() \
    (OPEN_CFW_SYSPLL_DISABLE_PLLCTL0)
#define OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_WRITE(value) \
    (OPEN_CFW_SYSPLL_DISABLE_PLLCTL0 = (value))
#endif

__attribute__((used, noinline))
open_cfw_syspll_disable_u32 open_cfw_bootloader_row6_stop_4273dc(
    open_cfw_syspll_disable_state *state)
{
    open_cfw_syspll_disable_u32 control;

    if (state == (open_cfw_syspll_disable_state *)0 ||
            (state->prefix & OPEN_CFW_SYSPLL_DISABLE_HANDLE_MASK) !=
                OPEN_CFW_SYSPLL_DISABLE_HANDLE_MAGIC) {
        return 2U;
    }

    control = OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_DISABLE_PLLCTL0_WRITE(
        control & ~OPEN_CFW_SYSPLL_DISABLE_PLL_PDB);
    state->prefix &= ~OPEN_CFW_SYSPLL_DISABLE_STATE_BIT;
    return 0U;
}
