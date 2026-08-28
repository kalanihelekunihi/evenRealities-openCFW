/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance descriptor initializer. */

typedef __UINT8_TYPE__ open_cfw_hwdi_u8;
typedef __UINT32_TYPE__ open_cfw_hwdi_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_descriptor_init_4275ea(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_descriptor_init_422dc6(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "movs r4, r3\n"
        "movs r5, r0\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r0]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr.w r3, [pc, #0xa58]\n"
        "cmp r0, r3\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 5f\n"
        "2:\n"
        "movs r0, #0\n"
        "strb.w r0, [r5, #0xdc]\n"
        "movs r0, #0\n"
        "strb.w r0, [r5, #0xdd]\n"
        "cmp r1, #0\n"
        "beq 3f\n"
        "cmp r2, #0\n"
        "beq 3f\n"
        "movs r0, #1\n"
        "strb.w r0, [r5, #0xdc]\n"
        "movs r3, r2\n"
        "movs r2, #1\n"
        "adds.w r0, r5, #0x34\n"
        "bl open_cfw_bootloader_retained_descriptor_init_4275ea\n"
        "3:\n"
        "cmp r4, #0\n"
        "beq 4f\n"
        "ldr r3, [sp, #0x10]\n"
        "cmp r3, #0\n"
        "beq 4f\n"
        "movs r0, #1\n"
        "strb.w r0, [r5, #0xdd]\n"
        "movs r2, #1\n"
        "movs r1, r4\n"
        "adds.w r0, r5, #0x4c\n"
        "bl open_cfw_bootloader_retained_descriptor_init_4275ea\n"
        "4:\n"
        "movs r0, #0\n"
        "5:\n"
        "pop {r1, r4, r5, pc}\n");
}
#else
typedef struct { open_cfw_hwdi_u8 bytes[0x11c]; } open_cfw_hwdi_instance;
extern void open_cfw_hwdi_host_descriptor_init(
    open_cfw_hwdi_u8 *descriptor,
    open_cfw_hwdi_u32 buffer,
    open_cfw_hwdi_u32 enabled,
    open_cfw_hwdi_u32 value);

static open_cfw_hwdi_u32 open_cfw_hwdi_read32(const open_cfw_hwdi_u8 *p)
{
    return (open_cfw_hwdi_u32)p[0] |
           ((open_cfw_hwdi_u32)p[1] << 8) |
           ((open_cfw_hwdi_u32)p[2] << 16) |
           ((open_cfw_hwdi_u32)p[3] << 24);
}

open_cfw_hwdi_u32 open_cfw_bootloader_hw_descriptor_init_422dc6(
    open_cfw_hwdi_instance *instance,
    open_cfw_hwdi_u32 first_buffer,
    open_cfw_hwdi_u32 first_value,
    open_cfw_hwdi_u32 second_buffer,
    open_cfw_hwdi_u32 second_value)
{
    if (instance == (open_cfw_hwdi_instance *)0 ||
        (open_cfw_hwdi_read32(instance->bytes) & ~0xfe000000U) !=
            0x01ea9e06U) {
        return 2U;
    }
    instance->bytes[0xdc] = 0U;
    instance->bytes[0xdd] = 0U;
    if (first_buffer != 0U && first_value != 0U) {
        instance->bytes[0xdc] = 1U;
        open_cfw_hwdi_host_descriptor_init(
            instance->bytes + 0x34, first_buffer, 1U, first_value);
    }
    if (second_buffer != 0U && second_value != 0U) {
        instance->bytes[0xdd] = 1U;
        open_cfw_hwdi_host_descriptor_init(
            instance->bytes + 0x4c, second_buffer, 1U, second_value);
    }
    return 0U;
}
#endif
