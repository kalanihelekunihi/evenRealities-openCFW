/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 global MSPI FIFO-read service. */

typedef __UINT8_TYPE__ open_cfw_mfr_u8;
typedef __UINT32_TYPE__ open_cfw_mfr_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_status_check_41d246(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_fifo_read_423e8a(void)
{
    __asm__ volatile(
        "push.w {r2, r3, r4, r5, r6, r7, r8, r9, r10, lr}\n"
        "movs r6, r0\n"
        "movs r5, r1\n"
        "movs r4, r2\n"
        "mov r9, r3\n"
        "cmp r6, #4\n"
        "blo 1f\n"
        "movs r0, #5\n"
        "b 8f\n"
        "1:\n"
        "mov r8, r4\n"
        "lsrs.w r8, r8, #2\n"
        "mvns r0, #3\n"
        "mla r4, r0, r8, r4\n"
        "movs r7, #0\n"
        "b 3f\n"
        "2:\n"
        "adds.w r10, r10, r6, lsl #12\n"
        "ldr.w r0, [r10, #0x14]\n"
        "str.w r0, [r5, r7, lsl #2]\n"
        "adds r7, r7, #1\n"
        "3:\n"
        "cmp r7, r8\n"
        "bhs 4f\n"
        /* Fixed literal load from 0x00423EC2 to 0x0042499C. */
        "ldr.w r10, [pc, #0xad8]\n"
        "movs r0, #0\n"
        "str r0, [sp]\n"
        "movs r3, #0\n"
        "movs r2, #0x3f\n"
        "adds.w r0, r10, r6, lsl #12\n"
        "adds.w r1, r0, #0x1c\n"
        "mov r0, r9\n"
        "bl open_cfw_bootloader_retained_status_check_41d246\n"
        "cmp r0, #0\n"
        "beq 2b\n"
        "b 8f\n"
        "4:\n"
        "cmp r4, #0\n"
        "beq 7f\n"
        /* Fixed literal load from 0x00423EE6 to 0x0042499C. */
        "ldr.w r8, [pc, #0xab4]\n"
        "movs r0, #0\n"
        "str r0, [sp]\n"
        "movs r3, #0\n"
        "movs r2, #0x3f\n"
        "adds.w r0, r8, r6, lsl #12\n"
        "adds.w r1, r0, #0x1c\n"
        "mov r0, r9\n"
        "bl open_cfw_bootloader_retained_status_check_41d246\n"
        "cmp r0, #0\n"
        "bne 8f\n"
        "adds.w r8, r8, r6, lsl #12\n"
        "ldr.w r0, [r8, #0x14]\n"
        "str r0, [sp]\n"
        "add.w r0, r5, r7, lsl #2\n"
        "movs r1, #0\n"
        "b 6f\n"
        "5:\n"
        "mov r2, sp\n"
        "ldrb r2, [r2, r1]\n"
        "strb r2, [r0, r1]\n"
        "adds r1, r1, #1\n"
        "6:\n"
        "cmp r1, r4\n"
        "blo 5b\n"
        "7:\n"
        "movs r0, #0\n"
        "8:\n"
        "pop.w {r1, r2, r4, r5, r6, r7, r8, r9, r10, pc}\n");
}
#else
typedef struct open_cfw_mfr_ports {
    void *context;
    open_cfw_mfr_u32 (*read_word)(void *context, open_cfw_mfr_u32 address);
    open_cfw_mfr_u32 (*status_check)(
        void *context, open_cfw_mfr_u32 timeout, open_cfw_mfr_u32 address,
        open_cfw_mfr_u32 mask, open_cfw_mfr_u32 value,
        open_cfw_mfr_u8 is_equal);
} open_cfw_mfr_ports;

static void open_cfw_mfr_store_word(open_cfw_mfr_u8 *output,
                                    open_cfw_mfr_u32 value)
{
    output[0] = (open_cfw_mfr_u8)value;
    output[1] = (open_cfw_mfr_u8)(value >> 8);
    output[2] = (open_cfw_mfr_u8)(value >> 16);
    output[3] = (open_cfw_mfr_u8)(value >> 24);
}

open_cfw_mfr_u32 open_cfw_bootloader_mspi_fifo_read_423e8a(
    open_cfw_mfr_u32 module, open_cfw_mfr_u8 *output,
    open_cfw_mfr_u32 byte_count, open_cfw_mfr_u32 timeout,
    const open_cfw_mfr_ports *ports)
{
    open_cfw_mfr_u32 index;
    open_cfw_mfr_u32 word_count;
    open_cfw_mfr_u32 remainder;
    open_cfw_mfr_u32 base;
    open_cfw_mfr_u32 status;

    if (module >= 4U) return 5U;
    word_count = byte_count >> 2;
    remainder = byte_count - 4U * word_count;
    base = 0x40060000U + module * 0x1000U;
    for (index = 0U; index < word_count; ++index) {
        status = ports->status_check(
            ports->context, timeout, base + 0x1CU, 0x3FU, 0U, 0U);
        if (status != 0U) return status;
        open_cfw_mfr_store_word(
            output + 4U * index,
            ports->read_word(ports->context, base + 0x14U));
    }
    if (remainder != 0U) {
        open_cfw_mfr_u32 value;
        status = ports->status_check(
            ports->context, timeout, base + 0x1CU, 0x3FU, 0U, 0U);
        if (status != 0U) return status;
        value = ports->read_word(ports->context, base + 0x14U);
        for (index = 0U; index < remainder; ++index)
            output[4U * word_count + index] =
                (open_cfw_mfr_u8)(value >> (8U * index));
    }
    return 0U;
}
#endif
