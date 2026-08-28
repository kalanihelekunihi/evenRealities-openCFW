/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 secondary per-instance configuration latch. */

typedef __UINT8_TYPE__ open_cfw_hwcls_u8;
typedef __UINT32_TYPE__ open_cfw_hwcls_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_critical_enter_41b8ec(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_config_latch_secondary_422f4c(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r5, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp]\n"
        "ldrb.w r0, [r4, #0x11a]\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #1\n"
        "strb.w r0, [r4, #0x11a]\n"
        "ldrb.w r0, [r6, #0x34]\n"
        "strb.w r0, [r4, #0x98]\n"
        "ldr r0, [r6]\n"
        "str r0, [r4, #0x64]\n"
        "ldr r0, [r6, #4]\n"
        "str r0, [r4, #0x68]\n"
        "ldr r0, [r6, #8]\n"
        "str r0, [r4, #0x6c]\n"
        "ldr r0, [r6, #0xc]\n"
        "str r0, [r4, #0x70]\n"
        "ldr r0, [r6, #0x10]\n"
        "str r0, [r4, #0x74]\n"
        "ldr r0, [r6, #0x14]\n"
        "str r0, [r4, #0x78]\n"
        "ldr r0, [r6, #0x18]\n"
        "str r0, [r4, #0x7c]\n"
        "movs r0, #0\n"
        "str.w r0, [r4, #0x9c]\n"
        "b 3f\n"
        "2:\n"
        "ldr.w r5, [pc, #0x8bc]\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r5\n"
        "pop {r1, r2, r4, r5, r6, pc}\n");
}
#else
typedef struct { open_cfw_hwcls_u8 bytes[0x11c]; } open_cfw_hwcls_instance;
extern open_cfw_hwcls_u32 open_cfw_hwcls_host_critical_enter(void);
extern void open_cfw_hwcls_host_critical_restore(open_cfw_hwcls_u32 token);

static open_cfw_hwcls_u32 open_cfw_hwcls_read32(const open_cfw_hwcls_u8 *p)
{
    return (open_cfw_hwcls_u32)p[0] |
           ((open_cfw_hwcls_u32)p[1] << 8) |
           ((open_cfw_hwcls_u32)p[2] << 16) |
           ((open_cfw_hwcls_u32)p[3] << 24);
}

static void open_cfw_hwcls_write32(open_cfw_hwcls_u8 *p, open_cfw_hwcls_u32 value)
{
    p[0] = (open_cfw_hwcls_u8)value;
    p[1] = (open_cfw_hwcls_u8)(value >> 8);
    p[2] = (open_cfw_hwcls_u8)(value >> 16);
    p[3] = (open_cfw_hwcls_u8)(value >> 24);
}

open_cfw_hwcls_u32 open_cfw_bootloader_hw_config_latch_secondary_422f4c(
    open_cfw_hwcls_instance *instance,
    const open_cfw_hwcls_u8 *configuration)
{
    open_cfw_hwcls_u32 token = open_cfw_hwcls_host_critical_enter();
    open_cfw_hwcls_u32 status = 0U;
    open_cfw_hwcls_u32 index;
    if (instance->bytes[0x11a] != 0U) {
        status = 0x08000005U;
    } else {
        instance->bytes[0x11a] = 1U;
        instance->bytes[0x98] = configuration[0x34];
        for (index = 0U; index < 7U; index++) {
            open_cfw_hwcls_write32(
                instance->bytes + 0x64U + index * 4U,
                open_cfw_hwcls_read32(configuration + index * 4U));
        }
        open_cfw_hwcls_write32(instance->bytes + 0x9c, 0U);
    }
    open_cfw_hwcls_host_critical_restore(token);
    return status;
}
#endif
