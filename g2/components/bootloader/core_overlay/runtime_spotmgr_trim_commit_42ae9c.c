/* SPDX-License-Identifier: BSD-3-Clause */
/* Apollo510 SPOT-manager critical trim commit at 0x0042AE9C. */
typedef __UINT32_TYPE__ open_cfw_spotmgr_commit_u32;
#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default"))) void open_cfw_bootloader_spotmgr_trim_commit_42ae9c(void){__asm volatile(
 "push {r7, lr}\n" "bl open_cfw_bootloader_critical_enter_41b8ec\n" "str r0, [sp]\n" "bl open_cfw_bootloader_spotmgr_trim_restore_42ae6c\n"
 "ldr.w r1, [pc, #0xb1c]\n" "ldrb r0, [r1]\n" "cmp r0, #0\n" "beq.n .Lcommit_after_flag\n"
 "ldr.w r0, [pc, #0xb18]\n" "ldr r2, [r0]\n" "cmp r2, #8\n" "beq.n .Lcommit_clear_flag\n" "ldr r0, [r0]\n" "cmp r0, #12\n" "beq.n .Lcommit_clear_flag\n"
 "ldr.w r0, [pc, #0xb0c]\n" "ldr r2, [r0]\n" "orrs r2, r2, #8\n" "str r2, [r0]\n" "ldr r2, [r0]\n" "orrs r2, r2, #0x40\n" "str r2, [r0]\n"
 ".Lcommit_clear_flag:\n" "movs r0, #0\n" "strb r0, [r1]\n"
 ".Lcommit_after_flag:\n" "bl open_cfw_bootloader_spotmgr_trim_finalize_41ccd6\n" "movs r0, #1\n" "bl open_cfw_bootloader_spotmgr_profile_trim_42ae24\n" "ldr r0, [sp]\n" "msr primask, r0\n" "pop {r0, pc}\n");}
#else
__attribute__((used,noinline,visibility("default"))) open_cfw_spotmgr_commit_u32 open_cfw_bootloader_spotmgr_trim_commit_42ae9c_portable(open_cfw_spotmgr_commit_u32 pending,open_cfw_spotmgr_commit_u32 power_state,open_cfw_spotmgr_commit_u32*control){if(pending&&power_state!=8U&&power_state!=12U)*control|=0x48U;return 0U;}
#endif
