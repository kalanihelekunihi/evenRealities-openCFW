#include <stdint.h>
extern uint32_t opencfw_em9305_callback_32c148(void);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_init_callback_32c254(void);
/* Full native32c148..32c174. Named ARC preserves the12-byte stack frame,
 * ambient bytes8..10, handler at11 and event word at4 across child calls. */
__asm__(
".text\n.align 2\n.global opencfw_em9305_callback_32c148\n"
".type opencfw_em9305_callback_32c148,@function\n"
"opencfw_em9305_callback_32c148:\n"
"st.aw blink,[sp,-12]\n"
"1: mov_s r0,0x805694\n"
"bl.d opencfw_em9305_wsf_event_remove\n"
"add r1,sp,11\n"
"st_s r0,[sp,4]\n"
"breq_s r0,0,2f\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\n"
"add_s r0,sp,4\n"
"bl.d opencfw_em9305_wsf_event_release\n"
"ld r0,[sp,4]\n"
"b_s 1b\n"
"2: bl opencfw_em9305_init_callback_32c254\n"
"ld.ab blink,[sp,12]\n"
"j_s [blink]\n"
".size opencfw_em9305_callback_32c148,.-opencfw_em9305_callback_32c148\n");
