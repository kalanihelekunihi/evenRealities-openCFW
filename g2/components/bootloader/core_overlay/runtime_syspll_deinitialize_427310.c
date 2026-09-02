/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0
 * am_hal_syspll_deinitialize(), authenticated at bootloader address
 * 0x00427310.  The exported name retains the row-six client ABI used by the
 * already source-owned callers at 0x00422198 and 0x00422266.
 */

typedef __UINT32_TYPE__ open_cfw_syspll_deinitialize_u32;

typedef struct open_cfw_syspll_deinitialize_state {
    open_cfw_syspll_deinitialize_u32 prefix;
    open_cfw_syspll_deinitialize_u32 module;
} open_cfw_syspll_deinitialize_state;

#define OPEN_CFW_SYSPLL_DEINITIALIZE_HANDLE_MASK 0x01ffffffU
#define OPEN_CFW_SYSPLL_DEINITIALIZE_HANDLE_MAGIC 0x01504c30U
#define OPEN_CFW_SYSPLL_DEINITIALIZE_INIT_BIT 0x01000000U
#define OPEN_CFW_SYSPLL_DEINITIALIZE_ENABLE_BIT 0x02000000U

#if defined(OPEN_CFW_SYSPLL_DEINITIALIZE_HOST_TEST)
extern open_cfw_syspll_deinitialize_u32
open_cfw_host_syspll_deinitialize_stop(
    open_cfw_syspll_deinitialize_state *state);
extern open_cfw_syspll_deinitialize_u32
open_cfw_host_pwrctrl_syspll_enabled(_Bool *enabled);
extern open_cfw_syspll_deinitialize_u32
open_cfw_host_pwrctrl_syspll_disable(void);
#define OPEN_CFW_SYSPLL_STOP(state) \
    open_cfw_host_syspll_deinitialize_stop(state)
#define OPEN_CFW_SYSPLL_POWER_ENABLED(enabled) \
    open_cfw_host_pwrctrl_syspll_enabled(enabled)
#define OPEN_CFW_SYSPLL_POWER_DISABLE() \
    open_cfw_host_pwrctrl_syspll_disable()
#else
extern open_cfw_syspll_deinitialize_u32
open_cfw_bootloader_row6_stop_4273dc(
    open_cfw_syspll_deinitialize_state *state);
extern open_cfw_syspll_deinitialize_u32
open_cfw_bootloader_pwrctrl_syspll_enabled_41cae8(_Bool *enabled);
extern open_cfw_syspll_deinitialize_u32
open_cfw_bootloader_pwrctrl_syspll_disable_41caa2(void);
#define OPEN_CFW_SYSPLL_STOP(state) \
    open_cfw_bootloader_row6_stop_4273dc(state)
#define OPEN_CFW_SYSPLL_POWER_ENABLED(enabled) \
    open_cfw_bootloader_pwrctrl_syspll_enabled_41cae8(enabled)
#define OPEN_CFW_SYSPLL_POWER_DISABLE() \
    open_cfw_bootloader_pwrctrl_syspll_disable_41caa2()
#endif

__attribute__((used, noinline))
open_cfw_syspll_deinitialize_u32 open_cfw_bootloader_row6_destroy_427310(
    open_cfw_syspll_deinitialize_state *state)
{
    open_cfw_syspll_deinitialize_u32 status = 0U;
    _Bool power_enabled = 0;

    if (state == (open_cfw_syspll_deinitialize_state *)0 ||
            (state->prefix & OPEN_CFW_SYSPLL_DEINITIALIZE_HANDLE_MASK) !=
                OPEN_CFW_SYSPLL_DEINITIALIZE_HANDLE_MAGIC) {
        return 2U;
    }

    if ((state->prefix & OPEN_CFW_SYSPLL_DEINITIALIZE_ENABLE_BIT) != 0U) {
        status = OPEN_CFW_SYSPLL_STOP(state);
    }

    (void)OPEN_CFW_SYSPLL_POWER_ENABLED(&power_enabled);
    if (power_enabled) {
        (void)OPEN_CFW_SYSPLL_POWER_DISABLE();
    }

    state->prefix &= ~OPEN_CFW_SYSPLL_DEINITIALIZE_INIT_BIT;
    return status;
}
