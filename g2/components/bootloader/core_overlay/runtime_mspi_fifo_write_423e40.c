/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 global MSPI FIFO-write service. */

typedef __UINT8_TYPE__ open_cfw_mfw_u8;
typedef __UINT32_TYPE__ open_cfw_mfw_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_status_check_41d246(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_fifo_write_423e40(void)
{
    __asm__ volatile(
        "push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r7, r2\n"
        "mov r8, r3\n"
        "movs r0, #0\n"
        "cmp r4, #4\n"
        "blo 2f\n"
        "movs r0, #5\n"
        "b 3f\n"
        "2:\n"
        "movs r5, #0\n"
        "b 1f\n"
        "4:\n"
        /* Fixed literal load from 0x00423E5A to 0x0042499C. */
        "ldr.w r0, [pc, #0xb40]\n"
        "ldr.w r1, [r6, r5, lsl #2]\n"
        "adds.w r2, r0, r4, lsl #12\n"
        "str r1, [r2, #0x10]\n"
        "movs r1, #0\n"
        "str r1, [sp]\n"
        "movs r3, #0x10\n"
        "movs r2, #0x3f\n"
        "adds.w r0, r0, r4, lsl #12\n"
        "adds.w r1, r0, #0x18\n"
        "mov r0, r8\n"
        "bl open_cfw_bootloader_retained_status_check_41d246\n"
        "adds r5, r5, #1\n"
        "1:\n"
        "lsls r1, r5, #2\n"
        "cmp r1, r7\n"
        "blo 4b\n"
        "3:\n"
        "pop.w {r1, r2, r4, r5, r6, r7, r8, pc}\n");
}
#else
typedef struct open_cfw_mfw_ports {
    void *context;
    void (*write_word)(void *context, open_cfw_mfw_u32 address,
                       open_cfw_mfw_u32 value);
    open_cfw_mfw_u32 (*status_check)(
        void *context, open_cfw_mfw_u32 timeout, open_cfw_mfw_u32 address,
        open_cfw_mfw_u32 mask, open_cfw_mfw_u32 value,
        open_cfw_mfw_u8 is_equal);
} open_cfw_mfw_ports;

open_cfw_mfw_u32 open_cfw_bootloader_mspi_fifo_write_423e40(
    open_cfw_mfw_u32 module, const open_cfw_mfw_u32 *data,
    open_cfw_mfw_u32 byte_count, open_cfw_mfw_u32 timeout,
    const open_cfw_mfw_ports *ports)
{
    open_cfw_mfw_u32 index;
    open_cfw_mfw_u32 status = 0U;
    open_cfw_mfw_u32 base;

    if (module >= 4U) return 5U;
    base = 0x40060000U + module * 0x1000U;
    for (index = 0U; 4U * index < byte_count; ++index) {
        ports->write_word(ports->context, base + 0x10U, data[index]);
        status = ports->status_check(
            ports->context, timeout, base + 0x18U, 0x3FU, 0x10U, 0U);
    }
    return status;
}
#endif
