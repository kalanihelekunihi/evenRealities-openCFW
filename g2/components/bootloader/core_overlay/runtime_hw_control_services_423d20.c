/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 global hardware-control services. */

typedef __UINT8_TYPE__ open_cfw_hwcs_u8;
typedef __UINT32_TYPE__ open_cfw_hwcs_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_hw_register_call_41d21c(void);
extern void open_cfw_bootloader_retained_delay_41d1c0(void);
extern void open_cfw_bootloader_debug_shutdown_422468(void);
extern void open_cfw_bootloader_retained_primask_enter_41b8ec(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_global_service_423d20(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_hw_control_initialize_423d58\n"
        "ldr r0, [pc, #0x70]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x10\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "str r1, [r0]\n"
        "movs r3, #0\n"
        "movs r2, #0\n"
        "ldr r1, [pc, #0x5c]\n"
        "mov.w r0, #0x3e8\n"
        "bl open_cfw_bootloader_retained_hw_register_call_41d21c\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "bl open_cfw_bootloader_debug_shutdown_422468\n"
        "cmp r0, #3\n"
        "bne 1f\n"
        "movs r0, #0\n"
        "1:\n"
        "pop {r1, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_initialize_423d58(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "bl open_cfw_bootloader_hw_control_test_zero_423dc4\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "bl open_cfw_bootloader_hw_control_query_423d7a\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "1:\n"
        "movs r0, #4\n"
        "b 3f\n"
        "2:\n"
        "mov.w r0, #0x1f4\n"
        "bl open_cfw_bootloader_retained_delay_41d1c0\n"
        "movs r0, #0\n"
        "3:\n"
        "pop {r1, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_query_423d7a(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r3, #0\n"
        "movs.w r2, #0x800000\n"
        "ldr r1, [pc, #0x18]\n"
        "mov.w r0, #0x3e8\n"
        "bl open_cfw_bootloader_retained_hw_register_call_41d21c\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #1\n"
        "b 2f\n"
        "1:\n"
        "movs r0, #0\n"
        "2:\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_test_423da0(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r1, r0\n"
        "lsls r1, r1, #2\n"
        "adds.w r1, r1, #-0x20000000\n"
        "movs r3, #1\n"
        "movs r2, #3\n"
        "mov.w r0, #0x3e8\n"
        "bl open_cfw_bootloader_retained_hw_register_call_41d21c\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #1\n"
        "b 2f\n"
        "1:\n"
        "movs r0, #0\n"
        "2:\n"
        "uxtb r0, r0\n"
        "pop {r1, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_test_zero_423dc4(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_hw_control_test_423da0\n"
        "pop {r1, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_control_critical_423dd0(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, lr}\n"
        "bl open_cfw_bootloader_retained_primask_enter_41b8ec\n"
        "str r0, [sp]\n"
        "ldr r1, [pc, #0x34]\n"
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
        "b 4f\n"
        "2:\n"
        "movs r0, #0\n"
        "ldr r1, [pc, #0x18]\n"
        "strb r0, [r1]\n"
        "bl open_cfw_bootloader_debug_shutdown_422468\n"
        "movs r4, r0\n"
        "cmp r4, #3\n"
        "bne 4f\n"
        "movs r4, #0\n"
        "4:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "pop {r1, r2, r4, pc}\n");
}
#else
extern open_cfw_hwcs_u32 open_cfw_hwcs_host_register_call(
    open_cfw_hwcs_u32, open_cfw_hwcs_u32, open_cfw_hwcs_u32,
    open_cfw_hwcs_u32);
extern open_cfw_hwcs_u32 open_cfw_hwcs_host_debug_shutdown(void);
extern void open_cfw_hwcs_host_delay(open_cfw_hwcs_u32);
extern open_cfw_hwcs_u32 open_cfw_hwcs_host_primask_enter(void);
extern void open_cfw_hwcs_host_primask_restore(open_cfw_hwcs_u32);
extern open_cfw_hwcs_u32 open_cfw_hwcs_host_control_register;
extern open_cfw_hwcs_u8 open_cfw_hwcs_host_countdown;
extern open_cfw_hwcs_u8 open_cfw_hwcs_host_latch;

open_cfw_hwcs_u32 open_cfw_bootloader_hw_control_query_423d7a(void)
{
    return open_cfw_hwcs_host_register_call(
        1000U, 0xe0000e80U, 0x00800000U, 0U) == 0U;
}

open_cfw_hwcs_u32 open_cfw_bootloader_hw_control_test_423da0(
    open_cfw_hwcs_u32 index)
{
    return open_cfw_hwcs_host_register_call(
        1000U, 0xe0000000U + index * 4U, 3U, 1U) == 0U;
}

open_cfw_hwcs_u32 open_cfw_bootloader_hw_control_test_zero_423dc4(void)
{
    return open_cfw_bootloader_hw_control_test_423da0(0U);
}

open_cfw_hwcs_u32 open_cfw_bootloader_hw_control_initialize_423d58(void)
{
    if (open_cfw_bootloader_hw_control_test_zero_423dc4() == 0U ||
        open_cfw_bootloader_hw_control_query_423d7a() == 0U) return 4U;
    open_cfw_hwcs_host_delay(500U);
    return 0U;
}

open_cfw_hwcs_u32 open_cfw_bootloader_hw_global_service_423d20(void)
{
    open_cfw_hwcs_u32 result;
    (void)open_cfw_bootloader_hw_control_initialize_423d58();
    open_cfw_hwcs_host_control_register &= ~0x10U;
    open_cfw_hwcs_host_control_register &= ~1U;
    result = open_cfw_hwcs_host_register_call(1000U, 0xe0000e80U, 0U, 0U);
    if (result == 0U) {
        result = open_cfw_hwcs_host_debug_shutdown();
        if (result == 3U) result = 0U;
    }
    return result;
}

open_cfw_hwcs_u32 open_cfw_bootloader_hw_control_critical_423dd0(void)
{
    open_cfw_hwcs_u32 token = open_cfw_hwcs_host_primask_enter();
    open_cfw_hwcs_u32 result;
    if (open_cfw_hwcs_host_countdown != 0U) --open_cfw_hwcs_host_countdown;
    if (open_cfw_hwcs_host_countdown != 0U) {
        result = 3U;
    } else {
        open_cfw_hwcs_host_latch = 0U;
        result = open_cfw_hwcs_host_debug_shutdown();
        if (result == 3U) result = 0U;
    }
    open_cfw_hwcs_host_primask_restore(token);
    return result;
}
#endif
