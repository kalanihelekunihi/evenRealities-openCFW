#include <stdint.h>

/* Source-owned ARC transport for the native 32b774..32b7aa register ABI.
 * The six-word private snapshot lives in the parent C stack frame. */
extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_four_slots_then_object_init_regs(
    uintptr_t slot, uintptr_t object, void *regs);
extern uint32_t opencfw_em9305_associated_optional_call_regs(
    uintptr_t callback, uint32_t address, uint32_t budget, const void *regs);

__asm__(
    ".text\n.balign 4\n"
    ".global opencfw_em9305_associated_four_slots_then_object_init_regs\n"
    ".type opencfw_em9305_associated_four_slots_then_object_init_regs,@function\n"
    "opencfw_em9305_associated_four_slots_then_object_init_regs:\n"
    "enter_s [r13-r14,blink]\n"
    "mov_s r13,r1\n"
    "mov_s r14,r2\n"
    "bl opencfw_em9305_init_callback_child_3246c0\n"
    "mov_s r1,0\n"
    "mov_s r0,r13\n"
    "bl opencfw_em9305_associated_object_init_312918\n"
    "st r2,[r14,0]\n"
    "st r3,[r14,4]\n"
    "st r4,[r14,8]\n"
    "st r5,[r14,12]\n"
    "st r6,[r14,16]\n"
    "st r7,[r14,20]\n"
    "leave_s [r13-r14,blink,pcl]\n"
    ".size opencfw_em9305_associated_four_slots_then_object_init_regs,.-opencfw_em9305_associated_four_slots_then_object_init_regs\n"

    ".balign 4\n"
    ".global opencfw_em9305_associated_optional_call_regs\n"
    ".type opencfw_em9305_associated_optional_call_regs,@function\n"
    "opencfw_em9305_associated_optional_call_regs:\n"
    "enter_s [r13,blink]\n"
    "mov_s r13,r0\n"
    "mov_s r12,r3\n"
    "mov_s r0,r1\n"
    "mov_s r1,r2\n"
    "ld r2,[r12,0]\n"
    "ld r3,[r12,4]\n"
    "ld r4,[r12,8]\n"
    "ld r5,[r12,12]\n"
    "ld r6,[r12,16]\n"
    "ld r7,[r12,20]\n"
    "jl_s [r13]\n"
    "mov_s r2,r0\n" /* Native 32b7aa immediately forwards callback R0. */
    "leave_s [r13,blink,pcl]\n"
    ".size opencfw_em9305_associated_optional_call_regs,.-opencfw_em9305_associated_optional_call_regs\n");
