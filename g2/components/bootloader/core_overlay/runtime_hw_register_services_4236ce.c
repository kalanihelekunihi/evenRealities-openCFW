/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 per-instance register services. */

typedef __UINT8_TYPE__ open_cfw_hwrs_u8;
typedef __UINT32_TYPE__ open_cfw_hwrs_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_register_or_4236ce(void)
{
    __asm__ volatile(
        "movs r2, r0\n"
        "ldr r2, [r2, #0x28]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r3, [pc, #0x150]\n"
        "cmp r0, r3\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 3f\n"
        "2:\n"
        "ldr r0, [pc, #0x7c]\n"
        "adds.w r3, r0, r2, lsl #12\n"
        "ldr r3, [r3, #0x38]\n"
        "orrs r1, r3\n"
        "adds.w r0, r0, r2, lsl #12\n"
        "str r1, [r0, #0x38]\n"
        "movs r0, #0\n"
        "3:\n"
        "bx lr\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_register_write_423700(void)
{
    __asm__ volatile(
        "movs r2, r0\n"
        "ldr r2, [r2, #0x28]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r3, [pc, #0x120]\n"
        "cmp r0, r3\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 3f\n"
        "2:\n"
        "ldr r0, [pc, #0x48]\n"
        "adds.w r3, r0, r2, lsl #12\n"
        "str r1, [r3, #0x44]\n"
        "adds.w r0, r0, r2, lsl #12\n"
        "ldr r0, [r0, #0x40]\n"
        "movs r0, #0\n"
        "3:\n"
        "bx lr\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_register_query_42372a(void)
{
    __asm__ volatile(
        "push {r4}\n"
        "movs r3, r0\n"
        "ldr r3, [r3, #0x28]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r4, [pc, #0xf4]\n"
        "cmp r0, r4\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 5f\n"
        "2:\n"
        "uxtb r2, r2\n"
        "cmp r2, #0\n"
        "beq 3f\n"
        "ldr r0, [pc, #0x18]\n"
        "adds.w r0, r0, r3, lsl #12\n"
        "ldr r0, [r0, #0x40]\n"
        "b 4f\n"
        "3:\n"
        "ldr r0, [pc, #0xc]\n"
        "adds.w r0, r0, r3, lsl #12\n"
        "ldr r0, [r0, #0x3c]\n"
        "4:\n"
        "str r0, [r1]\n"
        "movs r0, #0\n"
        "5:\n"
        "pop {r4}\n"
        "bx lr\n");
}
#else
typedef struct open_cfw_hwrs_instance {
    open_cfw_hwrs_u8 bytes[0x11c];
} open_cfw_hwrs_instance;

extern open_cfw_hwrs_u32 open_cfw_hwrs_host_registers[4][18];

static open_cfw_hwrs_u32 open_cfw_hwrs_read32(const open_cfw_hwrs_u8 *p)
{
    return (open_cfw_hwrs_u32)p[0] |
           ((open_cfw_hwrs_u32)p[1] << 8) |
           ((open_cfw_hwrs_u32)p[2] << 16) |
           ((open_cfw_hwrs_u32)p[3] << 24);
}

static open_cfw_hwrs_u32 open_cfw_hwrs_validate(
    const open_cfw_hwrs_instance *instance)
{
    return instance != (const open_cfw_hwrs_instance *)0 &&
           (open_cfw_hwrs_read32(instance->bytes) & ~0xfe000000U) ==
               0x01ea9e06U;
}

open_cfw_hwrs_u32 open_cfw_bootloader_hw_register_or_4236ce(
    open_cfw_hwrs_instance *instance, open_cfw_hwrs_u32 mask)
{
    open_cfw_hwrs_u32 index;
    if (!open_cfw_hwrs_validate(instance)) return 2U;
    index = open_cfw_hwrs_read32(instance->bytes + 0x28);
    open_cfw_hwrs_host_registers[index][0x38U / 4U] |= mask;
    return 0U;
}

open_cfw_hwrs_u32 open_cfw_bootloader_hw_register_write_423700(
    open_cfw_hwrs_instance *instance, open_cfw_hwrs_u32 value)
{
    open_cfw_hwrs_u32 index;
    if (!open_cfw_hwrs_validate(instance)) return 2U;
    index = open_cfw_hwrs_read32(instance->bytes + 0x28);
    open_cfw_hwrs_host_registers[index][0x44U / 4U] = value;
    (void)open_cfw_hwrs_host_registers[index][0x40U / 4U];
    return 0U;
}

open_cfw_hwrs_u32 open_cfw_bootloader_hw_register_query_42372a(
    open_cfw_hwrs_instance *instance, open_cfw_hwrs_u32 *output,
    open_cfw_hwrs_u32 selector)
{
    open_cfw_hwrs_u32 index;
    if (!open_cfw_hwrs_validate(instance)) return 2U;
    index = open_cfw_hwrs_read32(instance->bytes + 0x28);
    *output = open_cfw_hwrs_host_registers[index]
        [((open_cfw_hwrs_u8)selector != 0U) ? (0x40U / 4U) : (0x3cU / 4U)];
    return 0U;
}
#endif
