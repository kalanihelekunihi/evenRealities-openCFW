/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance hardware shutdown service. */

typedef __UINT8_TYPE__ open_cfw_hwsh_u8;
typedef __UINT32_TYPE__ open_cfw_hwsh_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_delay_41d1c0(void);
extern void open_cfw_bootloader_hw_register_clear_422d4c(void);
extern void open_cfw_bootloader_retained_hw_shutdown_423342(void);
extern void open_cfw_bootloader_hw_config_release_secondary_422fa2(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_shutdown_422fde(void)
{
    __asm__ volatile(
        "push.w {r4, r5, r6, r7, r8, lr}\n"
        "movs r4, r0\n"
        "mov r8, r4\n"
        "ldr r5, [r4, #0x28]\n"
        "ldr.w r6, [pc, #0x778]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "ldr r0, [r0, #0x30]\n"
        "ubfx r7, r0, #14, #1\n"
        "ands r7, r7, #1\n"
        "movs r0, r7\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x4000\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x800\n"
        "str r1, [r0]\n"
        "1:\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x200\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "ldr r0, [r0, #0x18]\n"
        "ubfx r0, r0, #3, #1\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "ldr.w r0, [pc, #0x81c]\n"
        "ldr.w r1, [r8, #0x30]\n"
        "udiv r0, r0, r1\n"
        "adds r0, r0, #1\n"
        "bl open_cfw_bootloader_retained_delay_41d1c0\n"
        "2:\n"
        "ldrb.w r0, [r8, #0x11b]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_register_clear_422d4c\n"
        "3:\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_retained_hw_shutdown_423342\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_config_release_secondary_422fa2\n"
        "uxtb r7, r7\n"
        "cmp r7, #0\n"
        "beq 4f\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x4000\n"
        "str r1, [r0]\n"
        "4:\n"
        "adds.w r6, r6, r5, lsl #12\n"
        "adds.w r0, r6, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x200\n"
        "str r1, [r0]\n"
        "pop.w {r4, r5, r6, r7, r8, pc}\n");
}
#else
typedef struct open_cfw_hwsh_instance { open_cfw_hwsh_u8 bytes[0x11c]; } open_cfw_hwsh_instance;
extern open_cfw_hwsh_u32 open_cfw_hwsh_host_registers[4][0x40 / 4];
extern void open_cfw_hwsh_host_delay(open_cfw_hwsh_u32 ticks);
extern void open_cfw_hwsh_host_register_clear(open_cfw_hwsh_instance *instance);
extern void open_cfw_hwsh_host_shutdown(open_cfw_hwsh_instance *instance);
extern void open_cfw_hwsh_host_release(open_cfw_hwsh_instance *instance);

static open_cfw_hwsh_u32 open_cfw_hwsh_read32(const open_cfw_hwsh_u8 *p)
{
    return (open_cfw_hwsh_u32)p[0] | ((open_cfw_hwsh_u32)p[1] << 8) |
           ((open_cfw_hwsh_u32)p[2] << 16) | ((open_cfw_hwsh_u32)p[3] << 24);
}

void open_cfw_bootloader_hw_shutdown_422fde(open_cfw_hwsh_instance *instance)
{
    open_cfw_hwsh_u32 index = open_cfw_hwsh_read32(instance->bytes + 0x28);
    open_cfw_hwsh_u32 *bank = open_cfw_hwsh_host_registers[index & 3U];
    open_cfw_hwsh_u32 had_enable = (bank[0x30 / 4] >> 14) & 1U;
    if (had_enable != 0U) bank[0x30 / 4] &= ~(0x4000U | 0x800U);
    bank[0x30 / 4] &= ~0x200U;
    if (((bank[0x18 / 4] >> 3) & 1U) != 0U) {
        open_cfw_hwsh_u32 divisor = open_cfw_hwsh_read32(instance->bytes + 0x30);
        open_cfw_hwsh_host_delay((divisor == 0U ? 0U : 10000000U / divisor) + 1U);
    }
    if (instance->bytes[0x11b] != 0U) open_cfw_hwsh_host_register_clear(instance);
    open_cfw_hwsh_host_shutdown(instance);
    open_cfw_hwsh_host_release(instance);
    if (had_enable != 0U) bank[0x30 / 4] |= 0x4000U;
    bank[0x30 / 4] |= 0x200U;
}
#endif
