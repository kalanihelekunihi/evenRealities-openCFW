/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader dual-mode transaction. */

typedef __UINT8_TYPE__ open_cfw_dual_u8;
typedef __UINT32_TYPE__ open_cfw_dual_u32;
typedef __UINTPTR_TYPE__ open_cfw_dual_uintptr;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_dual_u32 open_cfw_bootloader_dual_query_426c24(
    open_cfw_dual_u32, open_cfw_dual_uintptr, open_cfw_dual_u32,
    open_cfw_dual_u32 *);
extern open_cfw_dual_u32 open_cfw_bootloader_critical_save_41b8ec(void);
extern open_cfw_dual_u32 open_cfw_bootloader_bitmap_count_4215fe(open_cfw_dual_u32);
extern void *open_cfw_bootloader_memcpy_41568c(void *, const void *, open_cfw_dual_u32);
extern open_cfw_dual_u32 open_cfw_bootloader_mode0_enable_421bd2(open_cfw_dual_u32);
extern open_cfw_dual_u32 open_cfw_bootloader_mode1_enable_421b08(open_cfw_dual_u32);
extern open_cfw_dual_u32 open_cfw_bootloader_dual_null_commit_426d1e(void);
extern open_cfw_dual_u32 open_cfw_bootloader_dual_commit_426ccc(open_cfw_dual_u8 *);
extern open_cfw_dual_u32 open_cfw_bootloader_mode1_disable_421b5c(open_cfw_dual_u32);
extern open_cfw_dual_u32 open_cfw_bootloader_mode0_disable_421cce(open_cfw_dual_u32);
#define OPEN_CFW_DUAL_ATTR __attribute__((used, naked, noinline))
#else
open_cfw_dual_u32 open_cfw_dual_host_query(
    open_cfw_dual_u32, open_cfw_dual_uintptr, open_cfw_dual_u32,
    open_cfw_dual_u32 *);
open_cfw_dual_u32 open_cfw_dual_host_critical_save(void);
void open_cfw_dual_host_critical_restore(open_cfw_dual_u32);
open_cfw_dual_u32 open_cfw_dual_host_bitmap_count(open_cfw_dual_u32);
void open_cfw_dual_host_copy(void *, const void *, open_cfw_dual_u32);
open_cfw_dual_u32 open_cfw_dual_host_mode0_enable(open_cfw_dual_u32);
open_cfw_dual_u32 open_cfw_dual_host_mode1_enable(open_cfw_dual_u32);
open_cfw_dual_u32 open_cfw_dual_host_null_commit(void);
open_cfw_dual_u32 open_cfw_dual_host_commit(open_cfw_dual_u8 *);
open_cfw_dual_u32 open_cfw_dual_host_mode1_disable(open_cfw_dual_u32);
open_cfw_dual_u32 open_cfw_dual_host_mode0_disable(open_cfw_dual_u32);
extern open_cfw_dual_u32 open_cfw_dual_host_controller0;
extern open_cfw_dual_u32 open_cfw_dual_host_controller1;
extern open_cfw_dual_uintptr open_cfw_dual_host_current;
extern open_cfw_dual_u32 open_cfw_dual_host_configuration[3];
extern open_cfw_dual_u8 open_cfw_dual_host_ready;
#define OPEN_CFW_DUAL_ATTR __attribute__((used, noinline))
#endif

#define OPEN_CFW_DUAL_SPECIAL_A ((open_cfw_dual_uintptr)0x0EE6B280U)
#define OPEN_CFW_DUAL_SPECIAL_B ((open_cfw_dual_uintptr)0x0BB80000U)

OPEN_CFW_DUAL_ATTR
open_cfw_dual_u32 open_cfw_bootloader_dual_mode_service_4217d2(
    open_cfw_dual_uintptr instance,
    const open_cfw_dual_u32 *configuration)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r4, r0\n"
        "movs r6, r1\n"
        "movs r5, #0\n"
        "cmp r4, #0\n"
        "beq 1f\n"
        "ldr.w r0, [pc, #0xaf4]\n"
        "cmp r4, r0\n"
        "bne 2f\n"
        "1:\n"
        "ldr.w r1, [pc, #0xaf0]\n"
        "ldr r0, [r1]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr r0, [r1]\n"
        "ldr.w r1, [pc, #0xae0]\n"
        "cmp r0, r1\n"
        "bne 2f\n"
        "3:\n"
        "movs r7, #1\n"
        "b 4f\n"
        "2:\n"
        "movs r7, #0\n"
        "4:\n"
        "add r0, sp, #4\n"
        "ldr.w r1, [pc, #0xad8]\n"
        "ldm.w r1, {r2, r3, r12}\n"
        "stm.w r0, {r2, r3, r12}\n"
        "cmp r4, #0\n"
        "beq 5f\n"
        "ldr.w r0, [pc, #0xacc]\n"
        "cmp r4, r0\n"
        "beq 5f\n"
        "ldr.w r0, [pc, #0xab8]\n"
        "cmp r4, r0\n"
        "beq 5f\n"
        "movs r0, #5\n"
        "b 24f\n"
        "5:\n"
        "cmp r4, #0\n"
        "beq 10f\n"
        "cmp r6, #0\n"
        "bne 12f\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x9e8]\n"
        "ldr r0, [r1, #4]\n"
        "cmp r0, #0\n"
        "beq 7f\n"
        "movs r0, #0\n"
        "strb.w r0, [sp, #4]\n"
        "ldr r0, [r1, #4]\n"
        "6:\n"
        "add r3, sp, #8\n"
        "ldrb.w r2, [sp, #5]\n"
        "movs r1, r4\n"
        "bl open_cfw_bootloader_dual_query_426c24\n"
        "movs r5, r0\n"
        "add r6, sp, #4\n"
        "10:\n"
        "cmp r5, #0\n"
        "bne 23f\n"
        "movs.w r8, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "beq 14f\n"
        "uxtb r7, r7\n"
        "cmp r7, #0\n"
        "beq 15f\n"
        "movs.w r8, #1\n"
        "b 14f\n"
        "7:\n"
        "ldr r0, [r1, #0x10]\n"
        "cmp r0, #0\n"
        "beq 9f\n"
        "movs r0, #1\n"
        "strb.w r0, [sp, #4]\n"
        "ldr r0, [r1, #0x10]\n"
        "b 6b\n"
        "9:\n"
        "movs r0, #7\n"
        "b 24f\n"
        "12:\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 13f\n"
        "ldr.w r0, [pc, #0x984]\n"
        "ldr r0, [r0, #4]\n"
        "cmp r0, #0\n"
        "bne 13f\n"
        "movs r0, #7\n"
        "b 24f\n"
        "13:\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #1\n"
        "bne 10b\n"
        "ldr.w r0, [pc, #0x970]\n"
        "ldr r0, [r0, #0x10]\n"
        "cmp r0, #0\n"
        "bne 10b\n"
        "movs r0, #7\n"
        "b 24f\n"
        "15:\n"
        "movs r5, #3\n"
        "14:\n"
        "cmp r5, #0\n"
        "bne 17f\n"
        "cmp r4, #0\n"
        "beq 16f\n"
        "movs r2, #0xc\n"
        "ldr.w r7, [pc, #0xa24]\n"
        "movs r1, r6\n"
        "movs r0, r7\n"
        "bl open_cfw_bootloader_memcpy_41568c\n"
        "16:\n"
        "ldr.w r0, [pc, #0xa0c]\n"
        "str r4, [r0]\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xa14]\n"
        "strb r0, [r1]\n"
        "17:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "uxtb.w r8, r8\n"
        "cmp.w r8, #0\n"
        "beq 23f\n"
        "ldr.w r6, [pc, #0x9f8]\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 18f\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_enable_421bd2\n"
        "b 19f\n"
        "18:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_enable_421b08\n"
        "19:\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_bitmap_count_4215fe\n"
        "cmp r0, #0\n"
        "beq 22f\n"
        "ldr.w r4, [pc, #0x9c4]\n"
        "ldr r0, [r4]\n"
        "cmp r0, #0\n"
        "bne 20f\n"
        "bl open_cfw_bootloader_dual_null_commit_426d1e\n"
        "movs r5, r0\n"
        "b 21f\n"
        "20:\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_dual_commit_426ccc\n"
        "movs r5, r0\n"
        "cmp r5, #0\n"
        "bne 21f\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0\n"
        "bne 20f\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "b 21f\n"
        "20:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "21:\n"
        "cmp r5, #0\n"
        "bne 21f\n"
        "ldr r0, [r4]\n"
        "cmp r0, #0\n"
        "bne 25f\n"
        "21:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "b 25f\n"
        "22:\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode0_disable_421cce\n"
        "movs r0, #0x36\n"
        "bl open_cfw_bootloader_mode1_disable_421b5c\n"
        "25:\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "23:\n"
        "movs r0, r5\n"
        "24:\n"
        "add sp, #0x10\n"
        "pop.w {r4, r5, r6, r7, r8, pc}\n");
#else
    open_cfw_dual_u32 local[3] = {0x00020000U, 0x000C49BAU, 0U};
    open_cfw_dual_u32 status = 0U;
    open_cfw_dual_u32 mask;
    open_cfw_dual_u8 prior_compatible =
        (open_cfw_dual_u8)((instance == 0U || instance == OPEN_CFW_DUAL_SPECIAL_A) &&
        (open_cfw_dual_host_current == 0U ||
         open_cfw_dual_host_current == OPEN_CFW_DUAL_SPECIAL_A));
    open_cfw_dual_u8 run_transition = 0U;

    if (instance != 0U && instance != OPEN_CFW_DUAL_SPECIAL_A &&
        instance != OPEN_CFW_DUAL_SPECIAL_B) {
        return 5U;
    }
    if (instance != 0U && configuration == (const open_cfw_dual_u32 *)0) {
        if (open_cfw_dual_host_controller0 != 0U) {
            ((open_cfw_dual_u8 *)local)[0] = 0U;
            status = open_cfw_dual_host_query(
                open_cfw_dual_host_controller0, instance,
                ((open_cfw_dual_u8 *)local)[1], &local[1]);
            configuration = local;
        } else if (open_cfw_dual_host_controller1 != 0U) {
            ((open_cfw_dual_u8 *)local)[0] = 1U;
            status = open_cfw_dual_host_query(
                open_cfw_dual_host_controller1, instance,
                ((open_cfw_dual_u8 *)local)[1], &local[1]);
            configuration = local;
        } else {
            return 7U;
        }
    } else if (instance != 0U) {
        open_cfw_dual_u8 mode = ((const open_cfw_dual_u8 *)configuration)[0];
        if ((mode == 0U && open_cfw_dual_host_controller0 == 0U) ||
            (mode == 1U && open_cfw_dual_host_controller1 == 0U)) {
            return 7U;
        }
    }
    if (status != 0U) {
        return status;
    }
    mask = open_cfw_dual_host_critical_save();
    if (open_cfw_dual_host_bitmap_count(5U) != 0U) {
        if (prior_compatible != 0U) {
            run_transition = 1U;
        } else {
            status = 3U;
        }
    }
    if (status == 0U) {
        if (instance != 0U) {
            open_cfw_dual_host_copy(open_cfw_dual_host_configuration,
                                    configuration, 12U);
        }
        open_cfw_dual_host_current = instance;
        open_cfw_dual_host_ready = 1U;
    }
    open_cfw_dual_host_critical_restore(mask);
    if (run_transition == 0U) {
        return status;
    }
    if (((open_cfw_dual_u8 *)open_cfw_dual_host_configuration)[0] == 0U) {
        (void)open_cfw_dual_host_mode0_enable(0x36U);
    } else {
        (void)open_cfw_dual_host_mode1_enable(0x36U);
    }
    mask = open_cfw_dual_host_critical_save();
    if (open_cfw_dual_host_bitmap_count(5U) != 0U) {
        if (open_cfw_dual_host_current == 0U) {
            status = open_cfw_dual_host_null_commit();
        } else {
            status = open_cfw_dual_host_commit(
                (open_cfw_dual_u8 *)open_cfw_dual_host_configuration);
            if (status == 0U) {
                if (((open_cfw_dual_u8 *)open_cfw_dual_host_configuration)[0] == 0U) {
                    (void)open_cfw_dual_host_mode1_disable(0x36U);
                } else {
                    (void)open_cfw_dual_host_mode0_disable(0x36U);
                }
            }
        }
        if (status != 0U || open_cfw_dual_host_current == 0U) {
            (void)open_cfw_dual_host_mode1_disable(0x36U);
            (void)open_cfw_dual_host_mode0_disable(0x36U);
        }
    } else {
        (void)open_cfw_dual_host_mode0_disable(0x36U);
        (void)open_cfw_dual_host_mode1_disable(0x36U);
    }
    open_cfw_dual_host_critical_restore(mask);
    return status;
#endif
}
