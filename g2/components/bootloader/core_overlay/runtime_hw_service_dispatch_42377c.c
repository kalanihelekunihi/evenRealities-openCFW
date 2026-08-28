/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance service dispatcher. */

typedef __UINT8_TYPE__ open_cfw_hwsd_u8;
typedef __UINT32_TYPE__ open_cfw_hwsd_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_shutdown_422fde(void);
extern void open_cfw_bootloader_hw_register_clear_secondary_422d4c(void);
extern void open_cfw_bootloader_retained_hw_status_map_422d7a(void);
extern void open_cfw_bootloader_hw_register_clear_422d20(void);
extern void open_cfw_bootloader_hw_secondary_progress_423608(void);
extern void open_cfw_bootloader_hw_primary_progress_423524(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_service_dispatch_42377c(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r5, r4\n"
        "cmp r4, #0\n"
        "beq 1f\n"
        "ldr r0, [r4]\n"
        "bic r0, r0, #0xfe000000\n"
        "ldr r1, [pc, #0xa0]\n"
        "cmp r0, r1\n"
        "beq 2f\n"
        "1:\n"
        "movs r0, #2\n"
        "b 9f\n"
        "2:\n"
        "ldr r7, [r4, #0x28]\n"
        "ldrb.w r0, [r5, #0x11b]\n"
        "cmp r0, #0\n"
        "beq 8f\n"
        "ldr.w r0, [r5, #0xe8]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr.w r0, [r5, #0xe4]\n"
        "ldr r1, [pc, #0xb0]\n"
        "adds.w r1, r1, r7, lsl #12\n"
        "ldr r1, [r1, #0x50]\n"
        "lsls r1, r1, #20\n"
        "lsrs r1, r1, #20\n"
        "subs r0, r0, r1\n"
        "ldr.w r1, [r5, #0xe8]\n"
        "str r0, [r1]\n"
        "3:\n"
        "lsls r0, r6, #25\n"
        "bpl 4f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_shutdown_422fde\n"
        "4:\n"
        "lsls r0, r6, #19\n"
        "bpl 5f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_register_clear_secondary_422d4c\n"
        "5:\n"
        "lsls r0, r6, #20\n"
        "bpl 7f\n"
        "ldr.w r0, [r5, #0xf0]\n"
        "cmp r0, #0\n"
        "beq 6f\n"
        "movs r1, r6\n"
        "movs r0, r7\n"
        "bl open_cfw_bootloader_retained_hw_status_map_422d7a\n"
        "ldr.w r1, [r5, #0xf4]\n"
        "ldr.w r2, [r5, #0xf0]\n"
        "blx r2\n"
        "movs r0, #0\n"
        "str.w r0, [r5, #0xf0]\n"
        "6:\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_register_clear_422d20\n"
        "7:\n"
        "movs r0, #0\n"
        "strb.w r0, [r5, #0x11b]\n"
        "b 10f\n"
        "8:\n"
        "tst.w r6, #0x50\n"
        "beq 11f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_secondary_progress_423608\n"
        "11:\n"
        "lsls r0, r6, #26\n"
        "bpl 12f\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_primary_progress_423524\n"
        "12:\n"
        "lsls r0, r6, #31\n"
        "bpl 10f\n"
        "movs r0, #1\n"
        "strb.w r0, [r5, #0xde]\n"
        "10:\n"
        "movs r0, #1\n"
        "9:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}
#else
typedef struct open_cfw_hwsd_instance {
    open_cfw_hwsd_u8 bytes[0x11c];
} open_cfw_hwsd_instance;

extern open_cfw_hwsd_u32 open_cfw_hwsd_host_bank50(open_cfw_hwsd_u32);
extern void open_cfw_hwsd_host_shutdown(open_cfw_hwsd_instance *);
extern void open_cfw_hwsd_host_clear_secondary(open_cfw_hwsd_instance *);
extern open_cfw_hwsd_u32 open_cfw_hwsd_host_status_map(open_cfw_hwsd_u32, open_cfw_hwsd_u32);
extern void open_cfw_hwsd_host_callback(open_cfw_hwsd_u32, open_cfw_hwsd_u32);
extern void open_cfw_hwsd_host_clear_primary(open_cfw_hwsd_instance *);
extern void open_cfw_hwsd_host_secondary_progress(open_cfw_hwsd_instance *);
extern void open_cfw_hwsd_host_primary_progress(open_cfw_hwsd_instance *);

static open_cfw_hwsd_u32 open_cfw_hwsd_read32(const open_cfw_hwsd_u8 *p)
{
    return (open_cfw_hwsd_u32)p[0] | ((open_cfw_hwsd_u32)p[1] << 8) |
           ((open_cfw_hwsd_u32)p[2] << 16) | ((open_cfw_hwsd_u32)p[3] << 24);
}

static void open_cfw_hwsd_write32(open_cfw_hwsd_u8 *p, open_cfw_hwsd_u32 value)
{
    p[0] = (open_cfw_hwsd_u8)value; p[1] = (open_cfw_hwsd_u8)(value >> 8);
    p[2] = (open_cfw_hwsd_u8)(value >> 16); p[3] = (open_cfw_hwsd_u8)(value >> 24);
}

open_cfw_hwsd_u32 open_cfw_bootloader_hw_service_dispatch_42377c(
    open_cfw_hwsd_instance *instance, open_cfw_hwsd_u32 flags)
{
    open_cfw_hwsd_u32 index;
    if (instance == (open_cfw_hwsd_instance *)0 ||
        (open_cfw_hwsd_read32(instance->bytes) & ~0xfe000000U) != 0x01ea9e06U)
        return 2U;
    index = open_cfw_hwsd_read32(instance->bytes + 0x28);
    if (instance->bytes[0x11b] != 0U) {
        if (open_cfw_hwsd_read32(instance->bytes + 0xe8) != 0U)
            open_cfw_hwsd_write32(instance->bytes + 0xec,
                open_cfw_hwsd_read32(instance->bytes + 0xe4) -
                (open_cfw_hwsd_host_bank50(index) & 0xfffU));
        if ((flags & (1U << 6)) != 0U) open_cfw_hwsd_host_shutdown(instance);
        if ((flags & (1U << 12)) != 0U) open_cfw_hwsd_host_clear_secondary(instance);
        if ((flags & (1U << 11)) != 0U) {
            if (open_cfw_hwsd_read32(instance->bytes + 0xf0) != 0U) {
                open_cfw_hwsd_host_callback(
                    open_cfw_hwsd_host_status_map(index, flags),
                    open_cfw_hwsd_read32(instance->bytes + 0xf4));
                open_cfw_hwsd_write32(instance->bytes + 0xf0, 0U);
            }
            open_cfw_hwsd_host_clear_primary(instance);
        }
        instance->bytes[0x11b] = 0U;
    } else {
        if ((flags & 0x50U) != 0U) open_cfw_hwsd_host_secondary_progress(instance);
        if ((flags & (1U << 5)) != 0U) open_cfw_hwsd_host_primary_progress(instance);
        if ((flags & 1U) != 0U) instance->bytes[0xde] = 1U;
    }
    return 1U;
}
#endif
