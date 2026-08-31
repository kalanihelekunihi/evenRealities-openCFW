/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance hardware initializer. */

typedef __UINT8_TYPE__ open_cfw_hwinit_u8;
typedef __UINT16_TYPE__ open_cfw_hwinit_u16;
typedef __UINT32_TYPE__ open_cfw_hwinit_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_route_4222f0(void);
extern void open_cfw_bootloader_hw_clock_divider_422e28(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_initializer_42308e(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movs r7, r1\n"
        "cmp r4, #0\n"
        "beq 1f\n"
        "ldr r0, [r4]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r1, [pc, #0x340]\n"
        "cmp r0, r1\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 20f\n"
        "2:\n"
        "ldr r5, [r4, #0x28]\n"
        "ldr.w r6, [pc, #0x394]\n"
        "movs r0, #0\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "str r0, [r1, #0x30]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #8\n"
        "str r1, [r0]\n"
        "ldrb r0, [r7, #0xc]\n"
        "cmp r0, #2\n"
        "bge 3f\n"
        "ldrb r0, [r7, #0xc]\n"
        "cmp r0, #1\n"
        "bne 4f\n"
        "ldr.w r0, [pc, #0x364]\n"
        "ldr r0, [r0]\n"
        "and r0, r0, #0xff\n"
        "cmp r0, #0x21\n"
        "bne 4f\n"
        "3:\n"
        "movs r0, #6\n"
        "b 20f\n"
        "4:\n"
        "ldrb r0, [r7, #0xc]\n"
        "cmp r0, #0\n"
        "bne 5f\n"
        "movs r0, #4\n"
        "b 6f\n"
        "5:\n"
        "movs r0, #6\n"
        "6:\n"
        "strb.w r0, [r4, #0x118]\n"
        "ldr r0, [r7]\n"
        "ldr r1, [pc, #0x33c]\n"
        "cmp r0, r1\n"
        "blo 9f\n"
        "ldr r0, [pc, #0x33c]\n"
        "ldr r0, [r0]\n"
        "and r0, r0, #0xff\n"
        "cmp r0, #0x22\n"
        "blo 7f\n"
        "ldr r0, [pc, #0x334]\n"
        "ldr r1, [r0]\n"
        "movs.w r2, #0x400000\n"
        "lsls r2, r5\n"
        "orrs r1, r2\n"
        "str r1, [r0]\n"
        "7:\n"
        "ldrb.w r0, [r4, #0x118]\n"
        "cmp r0, #6\n"
        "bne 8f\n"
        "movs r0, #6\n"
        "b 81f\n"
        "8:\n"
        "movs r0, #5\n"
        "81:\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x30\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #4, #3\n"
        "str r2, [r1]\n"
        "b 12f\n"
        "9:\n"
        "ldr r0, [pc, #0x304]\n"
        "ldr r0, [r0]\n"
        "and r0, r0, #0xff\n"
        "cmp r0, #0x22\n"
        "blo 10f\n"
        "ldr r0, [pc, #0x2fc]\n"
        "ldr r1, [r0]\n"
        "movs.w r2, #0x400000\n"
        "lsls r2, r5\n"
        "bics r1, r2\n"
        "str r1, [r0]\n"
        "10:\n"
        "ldrb.w r0, [r4, #0x118]\n"
        "cmp r0, #6\n"
        "bne 11f\n"
        "movs r0, #6\n"
        "b 111f\n"
        "11:\n"
        "movs r0, #1\n"
        "111:\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x30\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #4, #3\n"
        "str r2, [r1]\n"
        "12:\n"
        "adds.w r1, r5, #0xb\n"
        "uxtb r1, r1\n"
        "ldrb.w r0, [r4, #0x118]\n"
        "bl open_cfw_bootloader_mode_route_4222f0\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x200\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x100\n"
        "str r1, [r0]\n"
        "adds.w r2, r4, #0x30\n"
        "ldr r1, [r7]\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_clock_divider_422e28\n"
        "cmp r0, #0\n"
        "bne.w 20f\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x4000\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x8000\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "ldr r1, [r0, #0x30]\n"
        "ldrh r0, [r7, #8]\n"
        "orrs r1, r0\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "str r1, [r0, #0x30]\n"
        "movs r1, #0\n"
        "movs r0, #0\n"
        "ldrb r2, [r7, #5]\n"
        "cmp r2, #0\n"
        "beq 13f\n"
        "cmp r2, #2\n"
        "beq 15f\n"
        "blo 14f\n"
        "b 16f\n"
        "13:\n"
        "movs r1, #1\n"
        "movs r0, #0\n"
        "b 16f\n"
        "14:\n"
        "movs r1, #1\n"
        "movs r0, #1\n"
        "b 16f\n"
        "15:\n"
        "movs r1, #0\n"
        "movs r0, #0\n"
        "16:\n"
        "adds.w r2, r6, r5, lsl #12\n"
        "adds r2, #0x2c\n"
        "ldr r3, [r2]\n"
        "lsrs r3, r3, #1\n"
        "lsls r3, r3, #1\n"
        "str r3, [r2]\n"
        "adds.w r2, r6, r5, lsl #12\n"
        "adds r2, #0x2c\n"
        "ldr r3, [r2]\n"
        "bfi r3, r1, #1, #1\n"
        "str r3, [r2]\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x2c\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #2, #1\n"
        "str r2, [r1]\n"
        "ldrb r0, [r7, #6]\n"
        "ands r0, r0, #1\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x2c\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #3, #1\n"
        "str r2, [r1]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x2c\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x10\n"
        "str r1, [r0]\n"
        "ldrb r0, [r7, #4]\n"
        "ands r0, r0, #3\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x2c\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #5, #2\n"
        "str r2, [r1]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x2c\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x80\n"
        "str r1, [r0]\n"
        "ldrb r0, [r7, #0xa]\n"
        "ands r0, r0, #7\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x34\n"
        "ldr r2, [r1]\n"
        "lsrs r2, r2, #3\n"
        "lsls r2, r2, #3\n"
        "orrs r0, r2\n"
        "str r0, [r1]\n"
        "ldrb r0, [r7, #0xb]\n"
        "ands r0, r0, #7\n"
        "adds.w r1, r6, r5, lsl #12\n"
        "adds r1, #0x34\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #3, #3\n"
        "str r2, [r1]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #1\n"
        "str r1, [r0]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x200\n"
        "str r1, [r0]\n"
        "adds.w r6, r6, r5, lsl #12\n"
        "adds.w r0, r6, #0x30\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x100\n"
        "str r1, [r0]\n"
        "movs r0, #0\n"
        "20:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}
#else
typedef struct open_cfw_hwinit_instance { open_cfw_hwinit_u8 bytes[0x11c]; } open_cfw_hwinit_instance;
typedef struct open_cfw_hwinit_config { open_cfw_hwinit_u8 bytes[0x0d]; } open_cfw_hwinit_config;

extern open_cfw_hwinit_u32 open_cfw_hwinit_host_registers[4][0x40 / 4];
extern open_cfw_hwinit_u32 open_cfw_hwinit_host_chip_revision;
extern open_cfw_hwinit_u32 open_cfw_hwinit_host_global_control;
extern void open_cfw_hwinit_host_mode_route(open_cfw_hwinit_u32 mode, open_cfw_hwinit_u32 route);
extern open_cfw_hwinit_u32 open_cfw_hwinit_host_clock_divider(
    open_cfw_hwinit_u32 index, open_cfw_hwinit_u32 requested, open_cfw_hwinit_u32 *actual);

static open_cfw_hwinit_u32 open_cfw_hwinit_read32(const open_cfw_hwinit_u8 *p)
{
    return (open_cfw_hwinit_u32)p[0] | ((open_cfw_hwinit_u32)p[1] << 8) |
           ((open_cfw_hwinit_u32)p[2] << 16) | ((open_cfw_hwinit_u32)p[3] << 24);
}

static open_cfw_hwinit_u16 open_cfw_hwinit_read16(const open_cfw_hwinit_u8 *p)
{
    return (open_cfw_hwinit_u16)((open_cfw_hwinit_u16)p[0] |
                                 ((open_cfw_hwinit_u16)p[1] << 8));
}

open_cfw_hwinit_u32 open_cfw_bootloader_hw_initializer_42308e(
    open_cfw_hwinit_instance *instance, const open_cfw_hwinit_config *config)
{
    open_cfw_hwinit_u32 index;
    open_cfw_hwinit_u32 *bank;
    open_cfw_hwinit_u32 mode;
    open_cfw_hwinit_u32 requested;
    open_cfw_hwinit_u32 status;
    open_cfw_hwinit_u32 route_bit1 = 0U;
    open_cfw_hwinit_u32 route_bit2 = 0U;

    if (instance == (open_cfw_hwinit_instance *)0 ||
        (open_cfw_hwinit_read32(instance->bytes) & ~0xfe000000U) != 0x01ea9e06U) {
        return 2U;
    }
    index = open_cfw_hwinit_read32(instance->bytes + 0x28);
    bank = open_cfw_hwinit_host_registers[index];
    bank[0x30 / 4] = 8U;

    mode = config->bytes[0x0c];
    if (mode >= 2U ||
        (mode == 1U && (open_cfw_hwinit_host_chip_revision & 0xffU) == 0x21U)) {
        return 6U;
    }
    instance->bytes[0x118] = (open_cfw_hwinit_u8)(mode == 0U ? 4U : 6U);

    requested = open_cfw_hwinit_read32(config->bytes);
    if (requested >= 0x0016e361U) {
        if ((open_cfw_hwinit_host_chip_revision & 0xffU) >= 0x22U) {
            open_cfw_hwinit_host_global_control |= 0x00400000U << index;
        }
        mode = instance->bytes[0x118] == 6U ? 6U : 5U;
    } else {
        if ((open_cfw_hwinit_host_chip_revision & 0xffU) >= 0x22U) {
            open_cfw_hwinit_host_global_control &= ~(0x00400000U << index);
        }
        mode = instance->bytes[0x118] == 6U ? 6U : 1U;
    }
    bank[0x30 / 4] = (bank[0x30 / 4] & ~(7U << 4)) | (mode << 4);
    open_cfw_hwinit_host_mode_route(instance->bytes[0x118], (index + 11U) & 0xffU);

    bank[0x30 / 4] &= ~(1U | 0x200U | 0x100U);
    status = open_cfw_hwinit_host_clock_divider(
        index, requested, (open_cfw_hwinit_u32 *)(void *)(instance->bytes + 0x30));
    if (status != 0U) return status;

    bank[0x30 / 4] &= ~(0x4000U | 0x8000U);
    bank[0x30 / 4] |= open_cfw_hwinit_read16(config->bytes + 8);
    if (config->bytes[5] == 0U) {
        route_bit1 = 1U;
    } else if (config->bytes[5] == 1U) {
        route_bit1 = 1U;
        route_bit2 = 1U;
    }
    bank[0x2c / 4] =
        (bank[0x2c / 4] & ~0xffU) |
        (route_bit1 << 1) | (route_bit2 << 2) |
        (((open_cfw_hwinit_u32)config->bytes[6] & 1U) << 3) | 0x10U |
        (((open_cfw_hwinit_u32)config->bytes[4] & 3U) << 5);
    bank[0x34 / 4] =
        (bank[0x34 / 4] & ~0x3fU) |
        ((open_cfw_hwinit_u32)config->bytes[0x0a] & 7U) |
        (((open_cfw_hwinit_u32)config->bytes[0x0b] & 7U) << 3);
    bank[0x30 / 4] |= 1U | 0x200U | 0x100U;
    return 0U;
}
#endif
