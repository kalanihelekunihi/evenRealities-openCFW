/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader dual-clock switch at
 * 0x00426C8C. The low input byte controls CLKGEN HFADJ bit 5. A transition to
 * enabled publishes the bit before invoking the authenticated bounded status
 * check; redundant enables and every disable return success without polling.
 */

typedef __UINT8_TYPE__ open_cfw_dual_switch_u8;
typedef __UINT32_TYPE__ open_cfw_dual_switch_u32;

#define OPEN_CFW_DUAL_SWITCH_BIT 0x20U
#define OPEN_CFW_DUAL_SWITCH_POLL_MASK 0x01000000U

#if defined(OPEN_CFW_DUAL_SWITCH_HOST_TEST)
extern volatile open_cfw_dual_switch_u32 open_cfw_dual_switch_host_hfadj;
extern volatile open_cfw_dual_switch_u32 open_cfw_dual_switch_host_status;
open_cfw_dual_switch_u32 open_cfw_dual_switch_host_status_check(
    open_cfw_dual_switch_u32,
    volatile open_cfw_dual_switch_u32 *,
    open_cfw_dual_switch_u32,
    open_cfw_dual_switch_u32,
    open_cfw_dual_switch_u32);
#define OPEN_CFW_DUAL_SWITCH_HFADJ open_cfw_dual_switch_host_hfadj
#define OPEN_CFW_DUAL_SWITCH_STATUS_POINTER (&open_cfw_dual_switch_host_status)
#define OPEN_CFW_DUAL_SWITCH_STATUS_CHECK open_cfw_dual_switch_host_status_check
#else
extern open_cfw_dual_switch_u32 open_cfw_bootloader_retained_status_check_41d246(
    open_cfw_dual_switch_u32,
    volatile open_cfw_dual_switch_u32 *,
    open_cfw_dual_switch_u32,
    open_cfw_dual_switch_u32,
    open_cfw_dual_switch_u32);
#define OPEN_CFW_DUAL_SWITCH_HFADJ \
    (*(volatile open_cfw_dual_switch_u32 *)(__UINTPTR_TYPE__)0x40004044U)
#define OPEN_CFW_DUAL_SWITCH_STATUS_POINTER \
    ((volatile open_cfw_dual_switch_u32 *)(__UINTPTR_TYPE__)0x40004030U)
#define OPEN_CFW_DUAL_SWITCH_STATUS_CHECK \
    open_cfw_bootloader_retained_status_check_41d246
#endif

__attribute__((used, noinline))
open_cfw_dual_switch_u32 open_cfw_bootloader_dual_switch_426c8c(
    open_cfw_dual_switch_u32 enabled)
{
    open_cfw_dual_switch_u32 value;

    if ((open_cfw_dual_switch_u8)enabled != 0U) {
        value = OPEN_CFW_DUAL_SWITCH_HFADJ;
        if ((value & OPEN_CFW_DUAL_SWITCH_BIT) == 0U) {
            OPEN_CFW_DUAL_SWITCH_HFADJ = value | OPEN_CFW_DUAL_SWITCH_BIT;
            return OPEN_CFW_DUAL_SWITCH_STATUS_CHECK(
                100U,
                OPEN_CFW_DUAL_SWITCH_STATUS_POINTER,
                OPEN_CFW_DUAL_SWITCH_POLL_MASK,
                OPEN_CFW_DUAL_SWITCH_POLL_MASK,
                1U);
        }
    } else {
        value = OPEN_CFW_DUAL_SWITCH_HFADJ;
        OPEN_CFW_DUAL_SWITCH_HFADJ = value & ~OPEN_CFW_DUAL_SWITCH_BIT;
    }
    return 0U;
}
