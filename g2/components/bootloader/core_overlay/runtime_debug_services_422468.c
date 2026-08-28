/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * G2 bootloader debug-domain shutdown services.  The public behavioral oracle
 * is AmbiqSuite SDK 5.1.0 am_hal_debug.c, copyright (c) 2025 Ambiq Micro, Inc.
 */

typedef __UINT8_TYPE__ open_cfw_debug_u8;
typedef __UINT32_TYPE__ open_cfw_debug_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_debug_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_debug_u32 open_cfw_bootloader_pwrctrl_enable_41bf84(open_cfw_debug_u32);
extern open_cfw_debug_u32 open_cfw_bootloader_pwrctrl_disable_41c17a(open_cfw_debug_u32);
extern open_cfw_debug_u32 open_cfw_bootloader_pwrctrl_enabled_41c2d8(open_cfw_debug_u32, open_cfw_debug_u8 *);
extern open_cfw_debug_u32 open_cfw_bootloader_delay_status_change_41d21c(open_cfw_debug_u32, volatile open_cfw_debug_u32 *, open_cfw_debug_u32, open_cfw_debug_u32);
extern open_cfw_debug_u32 open_cfw_bootloader_debug_power_target_4224b2(open_cfw_debug_u32);
extern open_cfw_debug_u32 open_cfw_bootloader_debug_trace_disable_target_42252e(void);
#define OPEN_CFW_DEBUG_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_debug_u32 open_cfw_debug_host_critical_save(void);
void open_cfw_debug_host_critical_restore(open_cfw_debug_u32);
open_cfw_debug_u32 open_cfw_debug_host_pwrctrl_enable(open_cfw_debug_u32);
open_cfw_debug_u32 open_cfw_debug_host_pwrctrl_disable(open_cfw_debug_u32);
open_cfw_debug_u32 open_cfw_debug_host_pwrctrl_enabled(open_cfw_debug_u32, open_cfw_debug_u8 *);
open_cfw_debug_u32 open_cfw_debug_host_delay_status_change(open_cfw_debug_u32, volatile open_cfw_debug_u32 *, open_cfw_debug_u32, open_cfw_debug_u32);
extern open_cfw_debug_u8 open_cfw_debug_host_enable_count;
extern open_cfw_debug_u8 open_cfw_debug_host_power_count;
extern open_cfw_debug_u8 open_cfw_debug_host_trace_count;
extern open_cfw_debug_u8 open_cfw_debug_host_power_entry_state;
extern volatile open_cfw_debug_u32 open_cfw_debug_host_dbgctrl;
extern volatile open_cfw_debug_u32 open_cfw_debug_host_demcr;
#define OPEN_CFW_DEBUG_ATTR __attribute__((used, noinline))
#endif

open_cfw_debug_u32 open_cfw_bootloader_debug_power_4224b2(open_cfw_debug_u32 power_up);
open_cfw_debug_u32 open_cfw_bootloader_debug_trace_disable_42252e(void);

OPEN_CFW_DEBUG_ATTR
open_cfw_debug_u32 open_cfw_bootloader_debug_disable_422468(void)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr r1, [pc, #0x104]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldrb r0, [r1]\n"
        "subs r0, r0, #1\n"
        "strb r0, [r1]\n"
        "1:\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r0, #3\n"
        "b 3f\n"
        "2:\n"
        "ldr r0, [pc, #0xf0]\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0xe\n"
        "str r1, [r0]\n"
        "3:\n"
        "bl open_cfw_bootloader_debug_trace_disable_target_42252e\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_debug_power_target_4224b2\n"
        "movs r4, r0\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_debug_u32 mask = open_cfw_debug_host_critical_save();
    open_cfw_debug_u32 result = 0U;
    if (open_cfw_debug_host_enable_count != 0U) --open_cfw_debug_host_enable_count;
    if (open_cfw_debug_host_enable_count != 0U) result = 3U;
    else open_cfw_debug_host_dbgctrl &= ~0x0FU;
    (void)result;
    (void)open_cfw_bootloader_debug_trace_disable_42252e();
    result = open_cfw_bootloader_debug_power_4224b2(0U);
    open_cfw_debug_host_critical_restore(mask);
    return result;
#endif
}

OPEN_CFW_DEBUG_ATTR
open_cfw_debug_u32 open_cfw_bootloader_debug_power_4224b2(open_cfw_debug_u32 power_up)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, lr}\n"
        "movs r5, r0\n"
        "movs r4, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "uxtb r5, r5\n"
        "cmp r5, #0\n"
        "beq 4f\n"
        "ldr r0, [pc, #0xb8]\n"
        "ldrb r1, [r0]\n"
        "adds r1, r1, #1\n"
        "strb r1, [r0]\n"
        "ldr r5, [pc, #0xb4]\n"
        "ldrb r0, [r5]\n"
        "cmp r0, #0\n"
        "bne 7f\n"
        "movs r0, #1\n"
        "strb r0, [r5]\n"
        "mov r1, sp\n"
        "movs r0, #0x1c\n"
        "bl open_cfw_bootloader_pwrctrl_enabled_41c2d8\n"
        "ldrb.w r0, [sp]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "ldrb r0, [r5]\n"
        "orrs r0, r0, #2\n"
        "strb r0, [r5]\n"
        "b 7f\n"
        "2:\n"
        "movs r0, #0x1c\n"
        "bl open_cfw_bootloader_pwrctrl_enable_41bf84\n"
        "b 7f\n"
        "4:\n"
        "ldr r1, [pc, #0x84]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldrb r0, [r1]\n"
        "subs r0, r0, #1\n"
        "strb r0, [r1]\n"
        "5:\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 6f\n"
        "movs r4, #3\n"
        "b 7f\n"
        "6:\n"
        "ldr r5, [pc, #0x70]\n"
        "ldrb r0, [r5]\n"
        "cmp r0, #1\n"
        "bne 8f\n"
        "movs r0, #0x1c\n"
        "bl open_cfw_bootloader_pwrctrl_disable_41c17a\n"
        "8:\n"
        "movs r0, #0\n"
        "strb r0, [r5]\n"
        "7:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "pop {r1, r2, r3, r4, r5, pc}\n");
#else
    open_cfw_debug_u32 mask = open_cfw_debug_host_critical_save();
    open_cfw_debug_u32 result = 0U;
    if ((open_cfw_debug_u8)power_up != 0U) {
        ++open_cfw_debug_host_power_count;
        if (open_cfw_debug_host_power_entry_state == 0U) {
            open_cfw_debug_u8 enabled = 0U;
            open_cfw_debug_host_power_entry_state = 1U;
            (void)open_cfw_debug_host_pwrctrl_enabled(28U, &enabled);
            if (enabled != 0U) open_cfw_debug_host_power_entry_state |= 2U;
            else (void)open_cfw_debug_host_pwrctrl_enable(28U);
        }
    } else {
        if (open_cfw_debug_host_power_count != 0U) --open_cfw_debug_host_power_count;
        if (open_cfw_debug_host_power_count != 0U) result = 3U;
        else {
            if (open_cfw_debug_host_power_entry_state == 1U) (void)open_cfw_debug_host_pwrctrl_disable(28U);
            open_cfw_debug_host_power_entry_state = 0U;
        }
    }
    open_cfw_debug_host_critical_restore(mask);
    return result;
#endif
}

OPEN_CFW_DEBUG_ATTR
open_cfw_debug_u32 open_cfw_bootloader_debug_trace_disable_42252e(void)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr r1, [pc, #0x4c]\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldrb r0, [r1]\n"
        "subs r0, r0, #1\n"
        "strb r0, [r1]\n"
        "1:\n"
        "ldrb r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "movs r4, #3\n"
        "b 3f\n"
        "2:\n"
        "ldr r0, [pc, #0x38]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x1000000\n"
        "str r1, [r0]\n"
        "movs r3, #0\n"
        "movs.w r2, #0x1000000\n"
        "ldr r1, [pc, #0x28]\n"
        "movs r0, #10\n"
        "bl open_cfw_bootloader_delay_status_change_41d21c\n"
        "movs r4, r0\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "pop {r1, r2, r4, pc}\n");
#else
    open_cfw_debug_u32 mask = open_cfw_debug_host_critical_save();
    open_cfw_debug_u32 result;
    if (open_cfw_debug_host_trace_count != 0U) --open_cfw_debug_host_trace_count;
    if (open_cfw_debug_host_trace_count != 0U) result = 3U;
    else {
        open_cfw_debug_host_demcr &= ~0x01000000U;
        result = open_cfw_debug_host_delay_status_change(10U, &open_cfw_debug_host_demcr, 0x01000000U, 0U);
    }
    open_cfw_debug_host_critical_restore(mask);
    return result;
#endif
}
