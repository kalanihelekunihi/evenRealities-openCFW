/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader row-four enable service. */

typedef __UINT8_TYPE__ open_cfw_row4_u8;
typedef __UINT32_TYPE__ open_cfw_row4_u32;
typedef __UINTPTR_TYPE__ open_cfw_row4_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_row4_u32 open_cfw_bootloader_bitmap_test_4215dc(open_cfw_row4_u32, open_cfw_row4_u32);
extern open_cfw_row4_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_row4_u32);
extern open_cfw_row4_u32 open_cfw_bootloader_bitmap_update_421632(open_cfw_row4_u32, open_cfw_row4_u32, open_cfw_row4_u32);
extern open_cfw_row4_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_mode0_poll_cleanup_421d28(open_cfw_row4_u32 *);
extern open_cfw_row4_u32 open_cfw_bootloader_row4_switch_426c58(open_cfw_row4_u32);
extern open_cfw_row4_u32 open_cfw_bootloader_mode_apply_426c72(open_cfw_row4_u32);
#define OPEN_CFW_ROW4_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_row4_u32 open_cfw_row4_host_bitmap_test(open_cfw_row4_u32, open_cfw_row4_u32);
open_cfw_row4_u32 open_cfw_row4_host_bitmap_count(open_cfw_row4_u32);
open_cfw_row4_u32 open_cfw_row4_host_bitmap_update(open_cfw_row4_u32, open_cfw_row4_u32, open_cfw_row4_u32);
open_cfw_row4_u32 open_cfw_row4_host_critical_save(void);
void open_cfw_row4_host_critical_restore(open_cfw_row4_u32);
void open_cfw_row4_host_cleanup(open_cfw_row4_u32 *);
open_cfw_row4_u32 open_cfw_row4_host_switch(open_cfw_row4_u32);
open_cfw_row4_u32 open_cfw_row4_host_apply(open_cfw_row4_u32);
extern open_cfw_row4_u8 open_cfw_row4_host_active;
extern open_cfw_row4_u8 open_cfw_row4_host_ready;
extern open_cfw_row4_u8 open_cfw_row4_host_complete;
extern open_cfw_row4_u32 open_cfw_row4_host_current;
extern open_cfw_row4_u32 open_cfw_row4_host_configuration;
extern open_cfw_row4_u32 *open_cfw_row4_host_state_pointer;
#define OPEN_CFW_ROW4_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_ROW4_ATTR
open_cfw_row4_u32 open_cfw_bootloader_row4_enable_421d5e(open_cfw_row4_u32 bit)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r2, r3, r4, r5, r6, lr}\n"
        "movs r5, r0\n"
        "movs r4, #0\n"
        "mov.w r0, #0x3e8\n"
        "str r0, [sp]\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_test_4215dc\n"
        "cmp r0, #0\n"
        "beq 2f\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r0, [pc, #0x518]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr.w r0, [pc, #0x510]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp]\n"
        "1:\n"
        "mov r0, sp\n"
        "ldr.w r1, [pc, #0x504]\n"
        "str r0, [r1]\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_mode0_poll_cleanup_421d28\n"
        "movs r0, #0\n"
        "b 10f\n"
        "2:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp, #4]\n"
        "ldr.w r6, [pc, #0x4e4]\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr.w r0, [pc, #0x4e0]\n"
        "ldr r0, [r0]\n"
        "ldr r0, [r0]\n"
        "str r0, [sp]\n"
        "3:\n"
        "ldr.w r0, [pc, #0x50c]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 4f\n"
        "movs r4, #1\n"
        "4:\n"
        "cmp r4, #0\n"
        "bne 9f\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne 7f\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_row4_switch_426c58\n"
        "ldr.w r0, [pc, #0x4a8]\n"
        "ldr r0, [r0]\n"
        "cmp r0, #0\n"
        "beq 7f\n"
        "ldr.w r0, [pc, #0x4a0]\n"
        "ldr r0, [r0]\n"
        "bl open_cfw_bootloader_mode_apply_426c72\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        "bne 6f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 7f\n"
        "ldr.w r0, [pc, #0x644]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne 7f\n"
        "movs r0, #1\n"
        "strb r0, [r6]\n"
        "b 7f\n"
        "6:\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_row4_switch_426c58\n"
        "7:\n"
        "cmp r4, #0\n"
        "bne 8f\n"
        "movs r2, #1\n"
        "movs r1, r5\n"
        "uxtb r1, r1\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_bitmap_update_421632\n"
        "8:\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "mov r0, sp\n"
        "ldr.w r1, [pc, #0x464]\n"
        "str r0, [r1]\n"
        "9:\n"
        "ldr r0, [sp, #4]\n"
        "msr primask, r0\n"
        "mov r0, sp\n"
        "bl open_cfw_bootloader_mode0_poll_cleanup_421d28\n"
        "movs r0, r4\n"
        "10:\n"
        "pop {r1, r2, r4, r5, r6, pc}\n");
#else
    open_cfw_row4_u32 status = 0U;
    open_cfw_row4_u32 remaining = 1000U;
    open_cfw_row4_u32 mask;
    if (open_cfw_row4_host_bitmap_test(4U, (open_cfw_row4_u8)bit) != 0U) {
        mask = open_cfw_row4_host_critical_save();
        if (open_cfw_row4_host_active != 0U && open_cfw_row4_host_state_pointer != (open_cfw_row4_u32 *)0) remaining = *open_cfw_row4_host_state_pointer;
        open_cfw_row4_host_state_pointer = &remaining;
        open_cfw_row4_host_critical_restore(mask);
        open_cfw_row4_host_cleanup(&remaining);
        return 0U;
    }
    mask = open_cfw_row4_host_critical_save();
    if (open_cfw_row4_host_active != 0U && open_cfw_row4_host_state_pointer != (open_cfw_row4_u32 *)0) remaining = *open_cfw_row4_host_state_pointer;
    if (open_cfw_row4_host_ready == 0U) status = 1U;
    if (status == 0U) {
        if ((open_cfw_row4_u8)open_cfw_row4_host_bitmap_count(4U) == 0U) {
            (void)open_cfw_row4_host_switch(1U);
            if (open_cfw_row4_host_current != 0U) {
                status = open_cfw_row4_host_apply(open_cfw_row4_host_configuration);
                if (status != 0U) (void)open_cfw_row4_host_switch(0U);
                else if (open_cfw_row4_host_active == 0U && open_cfw_row4_host_complete == 0U) open_cfw_row4_host_active = 1U;
            }
        }
        if (status == 0U) (void)open_cfw_row4_host_bitmap_update(4U, (open_cfw_row4_u8)bit, 1U);
    }
    if (open_cfw_row4_host_active != 0U) open_cfw_row4_host_state_pointer = &remaining;
    open_cfw_row4_host_critical_restore(mask);
    open_cfw_row4_host_cleanup(&remaining);
    return status;
#endif
}
