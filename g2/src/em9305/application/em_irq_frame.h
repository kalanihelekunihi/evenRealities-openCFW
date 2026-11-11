/* SPDX-License-Identifier: MIT
 * Shared interrupt frame for the em9305 ARC EM handlers (g2-2.2.6.10 firmware_ble_em9305.bin, wave 28).
 * The stock handlers are compiler-generated: an 88-byte frame that saves r0-r12, r30, blink, r58/r59,
 * lp_count and the aux registers lp_start, lp_end, 1411 and 1409, then runs the handler body and leaves
 * through `rtie`. The ARC gcc `interrupt` attribute does not emit this frame, so it is kept as one asm
 * template and every handler body is a plain C function that the template calls with `bl`.
 * Difference from stock: the body is a call instead of inline code, so each handler is a few bytes larger.
 * FLAG: the 1409/1411 aux numbers are as lowered from the stock bytes; their architectural names were not checked.
 */
#ifndef OPENCFW_EM_IRQ_FRAME_H
#define OPENCFW_EM_IRQ_FRAME_H
#include <stdint.h>

#define EM_IRQ_SAVE \
  "st.aw r0,[sp,-88]\n" "st_s r1,[sp,0x4]\n" "st_s r2,[sp,0x8]\n" "st_s r3,[sp,0xc]\n" \
  "st r4,[sp,16]\n" "st r5,[sp,20]\n" "st r6,[sp,24]\n" "st r7,[sp,28]\n" "st r8,[sp,32]\n" \
  "st r9,[sp,36]\n" "st r10,[sp,40]\n" "st r11,[sp,44]\n" "st_s r12,[sp,0x30]\n" "st r30,[sp,52]\n" \
  "st blink,[sp,56]\n" "st r58,[sp,60]\n" "st r59,[sp,64]\n" "st lp_count,[sp,68]\n" \
  "lr r0,[lp_start]\n" "st_s r0,[sp,0x48]\n" "lr r0,[lp_end]\n" "st_s r0,[sp,0x4c]\n" \
  "lr r0,[1411]\n" "st_s r0,[sp,0x50]\n" "lr r0,[1409]\n" "st_s r0,[sp,0x54]\n"
#define EM_IRQ_RESTORE \
  "ld_s r0,[sp,0x54]\n" "sr r0,[1409]\n" "ld_s r0,[sp,0x50]\n" "sr r0,[1411]\n" \
  "ld_s r0,[sp,0x4c]\n" "sr r0,[lp_end]\n" "ld_s r0,[sp,0x48]\n" "sr r0,[lp_start]\n" \
  "ld_s r0,[sp,0x44]\n" "ld r59,[sp,64]\n" "mov lp_count,r0\n" "ld r58,[sp,60]\n" "ld blink,[sp,56]\n" \
  "ld r30,[sp,52]\n" "ld_s r12,[sp,0x30]\n" "ld r11,[sp,44]\n" "ld r10,[sp,40]\n" "ld r9,[sp,36]\n" \
  "ld r8,[sp,32]\n" "ld r7,[sp,28]\n" "ld r6,[sp,24]\n" "ld r5,[sp,20]\n" "ld r4,[sp,16]\n" \
  "ld_s r3,[sp,0xc]\n" "ld_s r2,[sp,0x8]\n" "ld_s r1,[sp,0x4]\n" "ld.ab r0,[sp,88]\n" "rtie\n"

/* Emits SYM: frame save, `bl BODY`, frame restore, rtie. */
#define EM_IRQ_HANDLER(SYM, BODY) \
  __asm__(".text\n.balign 4\n.global " #SYM "\n.type " #SYM ",@function\n" #SYM ":\n" \
          EM_IRQ_SAVE "bl " #BODY "\n" EM_IRQ_RESTORE)

#define EM_R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
typedef void (*em_irq_cb_t)(void);
/* Calls the callback stored at address A when it is non-zero (the stock handlers all test `breq_s r0,0` first). */
#define EM_IRQ_CALL_SLOT(a) do { em_irq_cb_t cb_ = (em_irq_cb_t)(uintptr_t)EM_R32(a); if (cb_) cb_(); } while (0)
#endif
