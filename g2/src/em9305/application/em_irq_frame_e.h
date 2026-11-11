/* SPDX-License-Identifier: MIT
 * Second shared interrupt frame for the em9305 ARC EM handlers (g2-2.2.6.10 firmware_ble_em9305.bin, wave 28): the `enter_s` variant used by
 * IRQHandler_GPIO, IRQHandler_PmlSvld and IRQHandler_SleepTimerOutCmp3. The stock handler starts with `enter_s [REGS,blink]` (REGS is r13, or r13-r15
 * for PmlSvld; the body keeps values in those callee-saved registers), pushes r59/r58/r12..r0/r30, the aux registers 1409/1411/lp_end/lp_start and
 * lp_count, runs the body inline, restores everything, `leave_s` and `rtie`. Here the body is a C function called with `bl`; its own prologue saves
 * whatever callee-saved registers it uses, so the stock `enter_s` is kept only to keep the stock frame layout.
 * FLAG: the 1409/1411 aux numbers are as lowered from the stock bytes; their architectural names were not checked.
 */
#ifndef OPENCFW_EM_IRQ_FRAME_E_H
#define OPENCFW_EM_IRQ_FRAME_E_H
#include "em_irq_frame.h"

#define EM_IRQ_SAVE_E \
  "st.aw r59,[sp,-4]\n" "st.aw r58,[sp,-4]\n" "push_s r12\n" "st.aw r11,[sp,-4]\n" "st.aw r10,[sp,-4]\n" "st.aw r9,[sp,-4]\n" \
  "st.aw r8,[sp,-4]\n" "st.aw r7,[sp,-4]\n" "st.aw r6,[sp,-4]\n" "st.aw r5,[sp,-4]\n" "st.aw r4,[sp,-4]\n" "push_s r3\n" "push_s r2\n" \
  "push_s r1\n" "push_s r0\n" "st.aw r30,[sp,-4]\n" "lr r13,[1409]\n" "push_s r13\n" "lr r13,[1411]\n" "push_s r13\n" \
  "lr r13,[lp_end]\n" "push_s r13\n" "lr r13,[lp_start]\n" "push_s r13\n" "st.aw lp_count,[sp,-4]\n"
#define EM_IRQ_RESTORE_E \
  "pop_s r13\n" "mov lp_count,r13\n" "pop_s r13\n" "sr r13,[lp_start]\n" "pop_s r13\n" "sr r13,[lp_end]\n" "pop_s r13\n" \
  "sr r13,[1411]\n" "pop_s r13\n" "sr r13,[1409]\n" "ld.ab r30,[sp,4]\n" "pop_s r0\n" "pop_s r1\n" "pop_s r2\n" "pop_s r3\n" \
  "ld.ab r4,[sp,4]\n" "ld.ab r5,[sp,4]\n" "ld.ab r6,[sp,4]\n" "ld.ab r7,[sp,4]\n" "ld.ab r8,[sp,4]\n" "ld.ab r9,[sp,4]\n" \
  "ld.ab r10,[sp,4]\n" "ld.ab r11,[sp,4]\n" "pop_s r12\n" "ld.ab r58,[sp,4]\n" "ld.ab r59,[sp,4]\n"

/* REGS is a string literal: "r13" or "r13-r15". */
#define EM_IRQ_HANDLER_E(SYM, BODY, REGS) \
  __asm__(".text\n.balign 4\n.global " #SYM "\n.type " #SYM ",@function\n" #SYM ":\n" \
          "enter_s [" REGS ",blink]\n" EM_IRQ_SAVE_E "bl " #BODY "\n" EM_IRQ_RESTORE_E "leave_s [" REGS ",blink]\n" "rtie\n")
#endif
