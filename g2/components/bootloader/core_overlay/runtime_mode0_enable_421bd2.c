/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader mode-zero enable service. */

typedef __UINT8_TYPE__ open_cfw_mode0_u8;
typedef __UINT32_TYPE__ open_cfw_mode0_u32;
typedef __UINTPTR_TYPE__ open_cfw_mode0_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_mode0_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_mode0_u32, open_cfw_mode0_u32);
extern open_cfw_mode0_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_mode0_u32, open_cfw_mode0_u32, open_cfw_mode0_u32);
extern open_cfw_mode0_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_mode1_poll_cleanup_421ba4(open_cfw_mode0_u32 *);
extern void open_cfw_bootloader_mode0_state_query_41d676(open_cfw_mode0_u8 *);
extern open_cfw_mode0_u32 open_cfw_bootloader_mode0_control_41d3e4(open_cfw_mode0_u32, open_cfw_mode0_u8 *);
#define OPEN_CFW_MODE0_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_mode0_u32 open_cfw_mode0_host_bitmap_test(open_cfw_mode0_u32, open_cfw_mode0_u32);
open_cfw_mode0_u32 open_cfw_mode0_host_bitmap_update(open_cfw_mode0_u32, open_cfw_mode0_u32, open_cfw_mode0_u32);
open_cfw_mode0_u32 open_cfw_mode0_host_critical_save(void);
void open_cfw_mode0_host_critical_restore(open_cfw_mode0_u32);
void open_cfw_mode0_host_cleanup(open_cfw_mode0_u32 *);
void open_cfw_mode0_host_state_query(open_cfw_mode0_u8 *);
open_cfw_mode0_u32 open_cfw_mode0_host_control(open_cfw_mode0_u32, open_cfw_mode0_u8 *);
extern open_cfw_mode0_uintptr open_cfw_mode0_host_controller;
extern open_cfw_mode0_u8 open_cfw_mode0_host_table_mode;
extern open_cfw_mode0_u8 open_cfw_mode0_host_active;
extern open_cfw_mode0_u32 open_cfw_mode0_host_runtime_value;
extern open_cfw_mode0_u32 *open_cfw_mode0_host_state_pointer;
#define OPEN_CFW_MODE0_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_MODE0_ATTR
open_cfw_mode0_u32 open_cfw_bootloader_mode0_enable_421bd2(open_cfw_mode0_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r1, r2, r3, r4, r5, r6, r7, lr}\n"
        "movs r5, r0\n"
        "movs r4, #0\n"
        "movs r0, #0x96\n"
        "str r0, [sp, #4]\n"
        "ldr.w r6, [pc, #0x63c]\n"
        "ldr r0, [r6, #4]\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #7\n"
        "b 12f\n"
        "1:\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #2\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 4f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr.w r0, [pc, #0x844]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "ldr.w r0, [pc, #0x83c]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp, #4]\n"
        "2:\n"
        "add r0, sp, #4\n"
        "ldr.w r1, [pc, #0x830]\n"
        "str r0, [r1]\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "add r0, sp, #4\n"
        "bl open_cfw_bootloader_mode1_poll_cleanup_421ba4\n"
        "movs r0, #0\n"
        "b 12f\n"
        "4:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #8]\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_mode0_state_query_41d676\n"
        "ldr.w r7, [pc, #0x80c]\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr.w r0, [pc, #0x804]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp, #4]\n"
        "5:\n"
        "ldrb.w r0, [sp]\n"
        "cmp r0, #0\n"
        "bne 8f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #1\n"
        "bne 6f\n"
        "movs r0, #1\n"
        "strb.w r0, [sp, #1]\n"
        "add.w r1, sp, #1\n"
        "movs r0, #3\n"
        "bl open_cfw_bootloader_mode0_control_41d3e4\n"
        "b 10f\n"
        "6:\n"
        "movs r1, #0\n"
        "movs r0, #2\n"
        "bl open_cfw_bootloader_mode0_control_41d3e4\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "bne 10f\n"
        "movs r0, #1\n"
        "strb r0, [r7]\n"
        "b 10f\n"
        "8:\n"
        "ldrb.w r0, [sp]\n"
        "cmp r0, #2\n"
        "bne 9f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 9f\n"
        "movs r4, #3\n"
        "b 10f\n"
        "9:\n"
        "ldrb.w r0, [sp]\n"
        "cmp r0, #1\n"
        "bne 10f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #1\n"
        "bne 10f\n"
        "movs r4, #3\n"
        "10:\n"
        "cmp r4, #0\n"
        "bne 11f\n"
        "movs r2, #1\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #2\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "11:\n"
        "ldrb r0, [r7]\n"
        "cmp r0, #0\n"
        "beq 13f\n"
        "add r0, sp, #4\n"
        "ldr.w r1, [pc, #0x78c]\n"
        "str r0, [r1]\n"
        "13:\n"
        "ldr r0, [sp, #8]\n"
        "msr primask, r0\n"
        "add r0, sp, #4\n"
        "bl open_cfw_bootloader_mode1_poll_cleanup_421ba4\n"
        "movs r0, r4\n"
        "12:\n"
        "pop {r1, r2, r3, r4, r5, r6, r7, pc}\n");
#else
    open_cfw_mode0_u32 status = 0U;
    open_cfw_mode0_u32 remaining = 150U;
    open_cfw_mode0_u32 mask;
    open_cfw_mode0_u8 state = 0U;
    if (open_cfw_mode0_host_controller == 0U) return 7U;
    if (open_cfw_mode0_host_bitmap_test(2U, (open_cfw_mode0_u8)bit) != 0U) {
        mask = open_cfw_mode0_host_critical_save();
        if (open_cfw_mode0_host_active != 0U && open_cfw_mode0_host_state_pointer != (open_cfw_mode0_u32 *)0) {
            remaining = *open_cfw_mode0_host_state_pointer;
        }
        open_cfw_mode0_host_state_pointer = &remaining;
        open_cfw_mode0_host_critical_restore(mask);
        open_cfw_mode0_host_cleanup(&remaining);
        return 0U;
    }
    mask = open_cfw_mode0_host_critical_save();
    open_cfw_mode0_host_state_query(&state);
    if (open_cfw_mode0_host_active != 0U && open_cfw_mode0_host_state_pointer != (open_cfw_mode0_u32 *)0) {
        remaining = *open_cfw_mode0_host_state_pointer;
    }
    if (state == 0U) {
        if (open_cfw_mode0_host_table_mode == 1U) {
            open_cfw_mode0_u8 one = 1U;
            (void)open_cfw_mode0_host_control(3U, &one);
        } else {
            (void)open_cfw_mode0_host_control(2U, (open_cfw_mode0_u8 *)0);
            if (open_cfw_mode0_host_active == 0U) open_cfw_mode0_host_active = 1U;
        }
    } else if ((state == 2U && open_cfw_mode0_host_table_mode == 0U) ||
               (state == 1U && open_cfw_mode0_host_table_mode == 1U)) {
        status = 3U;
    }
    if (status == 0U) {
        (void)open_cfw_mode0_host_bitmap_update(2U, (open_cfw_mode0_u8)bit, 1U);
    }
    if (open_cfw_mode0_host_active != 0U) open_cfw_mode0_host_state_pointer = &remaining;
    open_cfw_mode0_host_critical_restore(mask);
    open_cfw_mode0_host_cleanup(&remaining);
    return status;
#endif
}
