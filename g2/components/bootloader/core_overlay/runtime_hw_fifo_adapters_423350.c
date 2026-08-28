/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 critical-section FIFO adapters. */

typedef __UINT8_TYPE__ open_cfw_hwfa_u8;
typedef __UINT32_TYPE__ open_cfw_hwfa_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_hw_fifo_read_4232c8(void);
extern void open_cfw_bootloader_hw_fifo_write_42330e(void);
extern void open_cfw_bootloader_retained_descriptor_consume_427602(void);
extern void open_cfw_bootloader_retained_descriptor_read_427660(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_fifo_snapshot_423350(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "sub sp, #0x28\n"
        "movs r4, r0\n"
        "movs r5, r4\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp, #4]\n"
        "mov r3, sp\n"
        "movs r2, #0x20\n"
        "add r1, sp, #8\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_hw_fifo_read_4232c8\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "bne 1f\n"
        "ldr r2, [sp]\n"
        "add r1, sp, #8\n"
        "adds.w r0, r5, #0x4c\n"
        "bl open_cfw_bootloader_retained_descriptor_consume_427602\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "ldr.w r4, [pc, #0x4d8]\n"
        "1:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "add sp, #0x2c\n"
        "pop {r4, r5, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_fifo_pump_423390(void)
{
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, r6, r7, lr}\n"
        "movs r5, r0\n"
        "movs r6, r5\n"
        "ldr r7, [r6, #0x28]\n"
        "movs r4, #0\n"
        "bl open_cfw_bootloader_retained_critical_enter_41b8ec\n"
        "str r0, [sp, #4]\n"
        "1:\n"
        "ldr.w r0, [pc, #0x3c0]\n"
        "adds.w r0, r0, r7, lsl #12\n"
        "ldr r0, [r0, #0x18]\n"
        "ubfx r0, r0, #5, #1\n"
        "cmp r0, #0\n"
        "bne 2f\n"
        "movs r2, #1\n"
        "mov r1, sp\n"
        "adds.w r0, r6, #0x34\n"
        "bl open_cfw_bootloader_retained_descriptor_read_427660\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "add r3, sp, #8\n"
        "movs r2, #1\n"
        "mov r1, sp\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_hw_fifo_write_42330e\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "beq 1b\n"
        "b 2f\n"
        "2:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "movs r0, r4\n"
        "pop {r1, r2, r3, r4, r5, r6, r7, pc}\n");
}
#else
typedef struct open_cfw_hwfa_instance {
    open_cfw_hwfa_u8 bytes[0x11c];
} open_cfw_hwfa_instance;
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_critical_enter(void);
extern void open_cfw_hwfa_host_critical_restore(open_cfw_hwfa_u32 token);
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_fifo_read(open_cfw_hwfa_instance *, open_cfw_hwfa_u8 *, open_cfw_hwfa_u32, open_cfw_hwfa_u32 *);
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_fifo_write(open_cfw_hwfa_instance *, const open_cfw_hwfa_u8 *, open_cfw_hwfa_u32, open_cfw_hwfa_u32 *);
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_consume(open_cfw_hwfa_u8 *, const open_cfw_hwfa_u8 *, open_cfw_hwfa_u32);
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_descriptor_read(open_cfw_hwfa_u8 *, open_cfw_hwfa_u8 *, open_cfw_hwfa_u32);
extern open_cfw_hwfa_u32 open_cfw_hwfa_host_status(open_cfw_hwfa_u32 index);

static open_cfw_hwfa_u32 open_cfw_hwfa_read32(const open_cfw_hwfa_u8 *p)
{
    return (open_cfw_hwfa_u32)p[0] | ((open_cfw_hwfa_u32)p[1] << 8) |
           ((open_cfw_hwfa_u32)p[2] << 16) | ((open_cfw_hwfa_u32)p[3] << 24);
}

open_cfw_hwfa_u32 open_cfw_bootloader_hw_fifo_snapshot_423350(open_cfw_hwfa_instance *instance)
{
    open_cfw_hwfa_u8 buffer[32]; open_cfw_hwfa_u32 count = 0U;
    open_cfw_hwfa_u32 token = open_cfw_hwfa_host_critical_enter();
    open_cfw_hwfa_u32 status = open_cfw_hwfa_host_fifo_read(instance, buffer, 32U, &count);
    if (status == 0U && open_cfw_hwfa_host_consume(instance->bytes + 0x4c, buffer, count) == 0U)
        status = 0x08000001U;
    open_cfw_hwfa_host_critical_restore(token);
    return status;
}

open_cfw_hwfa_u32 open_cfw_bootloader_hw_fifo_pump_423390(open_cfw_hwfa_instance *instance)
{
    open_cfw_hwfa_u8 byte; open_cfw_hwfa_u32 count, status = 0U;
    open_cfw_hwfa_u32 index = open_cfw_hwfa_read32(instance->bytes + 0x28);
    open_cfw_hwfa_u32 token = open_cfw_hwfa_host_critical_enter();
    while (((open_cfw_hwfa_host_status(index) >> 5) & 1U) == 0U) {
        if (open_cfw_hwfa_host_descriptor_read(instance->bytes + 0x34, &byte, 1U) == 0U) break;
        status = open_cfw_hwfa_host_fifo_write(instance, &byte, 1U, &count);
        if (status != 0U) break;
    }
    open_cfw_hwfa_host_critical_restore(token);
    return status;
}
#endif
