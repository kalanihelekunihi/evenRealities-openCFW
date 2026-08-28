/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance configuration latch. */

typedef __UINT8_TYPE__ open_cfw_hwcl_u8;
typedef __UINT32_TYPE__ open_cfw_hwcl_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_critical_enter_41b8ec(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_config_latch_422ee2(void)
{
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r5, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp]\n"
        "ldrb.w r0, [r4, #0x119]\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r0, #1\n"
        "strb.w r0, [r4, #0x119]\n"
        "ldrb.w r0, [r6, #0x34]\n"
        "strb.w r0, [r4, #0xd4]\n"
        "ldr r0, [r6]\n"
        "str.w r0, [r4, #0xa0]\n"
        "ldr r0, [r6, #4]\n"
        "str.w r0, [r4, #0xa4]\n"
        "ldr r0, [r6, #8]\n"
        "str.w r0, [r4, #0xa8]\n"
        "ldr r0, [r6, #0xc]\n"
        "str.w r0, [r4, #0xac]\n"
        "ldr r0, [r6, #0x10]\n"
        "str.w r0, [r4, #0xb0]\n"
        "ldr r0, [r6, #0x14]\n"
        "str.w r0, [r4, #0xb4]\n"
        "ldr r0, [r6, #0x18]\n"
        "str.w r0, [r4, #0xb8]\n"
        "movs r0, #0\n"
        "str.w r0, [r4, #0xd8]\n"
        "movs r0, #0\n"
        "strb.w r0, [r4, #0xde]\n"
        "b 3f\n"
        "2:\n"
        "ldr.w r5, [pc, #0x910]\n"
        "3:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "movs r0, r5\n"
        "pop {r1, r2, r4, r5, r6, pc}\n");
}
#else
typedef struct { open_cfw_hwcl_u8 bytes[0x11c]; } open_cfw_hwcl_instance;
extern open_cfw_hwcl_u32 open_cfw_hwcl_host_critical_enter(void);
extern void open_cfw_hwcl_host_critical_restore(open_cfw_hwcl_u32 token);

static open_cfw_hwcl_u32 open_cfw_hwcl_read32(const open_cfw_hwcl_u8 *p)
{
    return (open_cfw_hwcl_u32)p[0] |
           ((open_cfw_hwcl_u32)p[1] << 8) |
           ((open_cfw_hwcl_u32)p[2] << 16) |
           ((open_cfw_hwcl_u32)p[3] << 24);
}

static void open_cfw_hwcl_write32(open_cfw_hwcl_u8 *p, open_cfw_hwcl_u32 value)
{
    p[0] = (open_cfw_hwcl_u8)value;
    p[1] = (open_cfw_hwcl_u8)(value >> 8);
    p[2] = (open_cfw_hwcl_u8)(value >> 16);
    p[3] = (open_cfw_hwcl_u8)(value >> 24);
}

open_cfw_hwcl_u32 open_cfw_bootloader_hw_config_latch_422ee2(
    open_cfw_hwcl_instance *instance,
    const open_cfw_hwcl_u8 *configuration)
{
    open_cfw_hwcl_u32 token = open_cfw_hwcl_host_critical_enter();
    open_cfw_hwcl_u32 status = 0U;
    open_cfw_hwcl_u32 index;
    if (instance->bytes[0x119] != 0U) {
        status = 0x08000004U;
    } else {
        instance->bytes[0x119] = 1U;
        instance->bytes[0xd4] = configuration[0x34];
        for (index = 0U; index < 7U; index++) {
            open_cfw_hwcl_write32(
                instance->bytes + 0xa0U + index * 4U,
                open_cfw_hwcl_read32(configuration + index * 4U));
        }
        open_cfw_hwcl_write32(instance->bytes + 0xd8, 0U);
        instance->bytes[0xde] = 0U;
    }
    open_cfw_hwcl_host_critical_restore(token);
    return status;
}
#endif
