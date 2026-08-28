/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 per-instance FIFO read/write services. */

typedef __UINT8_TYPE__ open_cfw_hwfifo_u8;
typedef __UINT32_TYPE__ open_cfw_hwfifo_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_fifo_read_4232c8(void)
{
    __asm__ volatile(
        "push {r4, r5, r6, r7}\n"
        "movs r4, r0\n"
        "movs r5, #0\n"
        "movs r0, #0\n"
        "ldr r6, [r4, #0x28]\n"
        "b 2f\n"
        "1:\n"
        "adds.w r7, r7, r6, lsl #12\n"
        "ldr r4, [r7]\n"
        "tst.w r4, #0xf00\n"
        "bne 4f\n"
        "cmp r1, #0\n"
        "beq 2f\n"
        "strb r4, [r1, r5]\n"
        "adds r5, r5, #1\n"
        "2:\n"
        "cmp r5, r2\n"
        "bhs 5f\n"
        "ldr.w r7, [pc, #0x474]\n"
        "adds.w r4, r7, r6, lsl #12\n"
        "ldr r4, [r4, #0x18]\n"
        "ubfx r4, r4, #4, #1\n"
        "cmp r4, #0\n"
        "beq 1b\n"
        "b 5f\n"
        "4:\n"
        "movs.w r0, #0x08000000\n"
        "5:\n"
        "cmp r3, #0\n"
        "beq 6f\n"
        "str r5, [r3]\n"
        "6:\n"
        "pop {r4, r5, r6, r7}\n"
        "bx lr\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_fifo_write_42330e(void)
{
    __asm__ volatile(
        "push {r4, r5, r6}\n"
        "movs r4, #0\n"
        "ldr r5, [r0, #0x28]\n"
        "b 2f\n"
        "1:\n"
        "ldrb r0, [r1, r4]\n"
        "adds.w r6, r6, r5, lsl #12\n"
        "str r0, [r6]\n"
        "adds r4, r4, #1\n"
        "2:\n"
        "cmp r4, r2\n"
        "bhs 3f\n"
        "ldr.w r6, [pc, #0x43c]\n"
        "adds.w r0, r6, r5, lsl #12\n"
        "ldr r0, [r0, #0x18]\n"
        "ubfx r0, r0, #5, #1\n"
        "cmp r0, #0\n"
        "beq 1b\n"
        "3:\n"
        "cmp r3, #0\n"
        "beq 4f\n"
        "str r4, [r3]\n"
        "4:\n"
        "movs r0, #0\n"
        "pop {r4, r5, r6}\n"
        "bx lr\n");
}

#else
typedef struct { open_cfw_hwfifo_u8 bytes[0x11c]; } open_cfw_hwfifo_instance;
extern open_cfw_hwfifo_u32 open_cfw_hwfifo_host_status(open_cfw_hwfifo_u32 index);
extern open_cfw_hwfifo_u32 open_cfw_hwfifo_host_read(open_cfw_hwfifo_u32 index);
extern void open_cfw_hwfifo_host_write(open_cfw_hwfifo_u32 index, open_cfw_hwfifo_u32 value);

static open_cfw_hwfifo_u32 open_cfw_hwfifo_read32(const open_cfw_hwfifo_u8 *p)
{
    return (open_cfw_hwfifo_u32)p[0] | ((open_cfw_hwfifo_u32)p[1] << 8) |
           ((open_cfw_hwfifo_u32)p[2] << 16) | ((open_cfw_hwfifo_u32)p[3] << 24);
}

open_cfw_hwfifo_u32 open_cfw_bootloader_hw_fifo_read_4232c8(
    open_cfw_hwfifo_instance *instance, open_cfw_hwfifo_u8 *output,
    open_cfw_hwfifo_u32 capacity, open_cfw_hwfifo_u32 *count)
{
    open_cfw_hwfifo_u32 index = open_cfw_hwfifo_read32(instance->bytes + 0x28);
    open_cfw_hwfifo_u32 done = 0U, status = 0U;
    while (done < capacity && ((open_cfw_hwfifo_host_status(index) >> 4) & 1U) == 0U) {
        open_cfw_hwfifo_u32 value = open_cfw_hwfifo_host_read(index);
        if ((value & 0xF00U) != 0U) { status = 0x08000000U; break; }
        if (output != (open_cfw_hwfifo_u8 *)0) output[done++] = (open_cfw_hwfifo_u8)value;
    }
    if (count != (open_cfw_hwfifo_u32 *)0) *count = done;
    return status;
}

open_cfw_hwfifo_u32 open_cfw_bootloader_hw_fifo_write_42330e(
    open_cfw_hwfifo_instance *instance, const open_cfw_hwfifo_u8 *input,
    open_cfw_hwfifo_u32 size, open_cfw_hwfifo_u32 *count)
{
    open_cfw_hwfifo_u32 index = open_cfw_hwfifo_read32(instance->bytes + 0x28);
    open_cfw_hwfifo_u32 done = 0U;
    while (done < size && ((open_cfw_hwfifo_host_status(index) >> 5) & 1U) == 0U)
        open_cfw_hwfifo_host_write(index, input[done++]);
    if (count != (open_cfw_hwfifo_u32 *)0) *count = done;
    return 0U;
}

#endif
