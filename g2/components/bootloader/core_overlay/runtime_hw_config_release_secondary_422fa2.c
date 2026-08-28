/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 secondary configuration release. */

typedef __UINT8_TYPE__ open_cfw_hwcrs_u8;
typedef __UINT32_TYPE__ open_cfw_hwcrs_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_retained_memset_41560c(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_config_release_secondary_422fa2(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r5, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp]\n"
        "ldrb.w r0, [r4, #0x11a]\n"
        "cmp r0, #1\n"
        "bne 2f\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0x11a]\n"
        "movs r1, #0x38\n"
        "movs r2, #0\n"
        "adds.w r6, r4, #0x64\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_retained_memset_41560c\n"
        "movs r0, #0\n"
        "str.w r0, [r4, #0x9c]\n"
        "b 3f\n"
        "2:\n"
        "movs r5, #7\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r5\n"
        "pop {r1, r2, r4, r5, r6, pc}\n");
}
#else
typedef struct { open_cfw_hwcrs_u8 bytes[0x11c]; } open_cfw_hwcrs_instance;
extern open_cfw_hwcrs_u32 open_cfw_hwcrs_host_critical_enter(void);
extern void open_cfw_hwcrs_host_critical_restore(open_cfw_hwcrs_u32 token);
extern void open_cfw_hwcrs_host_memset(open_cfw_hwcrs_u8 *destination, open_cfw_hwcrs_u32 length, open_cfw_hwcrs_u32 value);

open_cfw_hwcrs_u32 open_cfw_bootloader_hw_config_release_secondary_422fa2(
    open_cfw_hwcrs_instance *instance)
{
    open_cfw_hwcrs_u32 token = open_cfw_hwcrs_host_critical_enter();
    open_cfw_hwcrs_u32 status = 0U;
    if (instance->bytes[0x11a] == 1U) {
        instance->bytes[0x11a] = 0U;
        open_cfw_hwcrs_host_memset(instance->bytes + 0x64, 0x38U, 0U);
        instance->bytes[0x9c] = 0U;
        instance->bytes[0x9d] = 0U;
        instance->bytes[0x9e] = 0U;
        instance->bytes[0x9f] = 0U;
    } else {
        status = 7U;
    }
    open_cfw_hwcrs_host_critical_restore(token);
    return status;
}
#endif
