#include <stdint.h>
/* Native322fdc..323026. The exact20-byte caller-relative frame preserves
 * native ambient event byte5 and trailing bytes14/15. Instructions are
 * semantic assembler, not stock bytes. All executable children named. */
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t,uint32_t);
__asm__(
 ".text\n.align 2\n.global opencfw_em9305_mode_event_322fdc\n"
 ".type opencfw_em9305_mode_event_322fdc,@function\n"
 "opencfw_em9305_mode_event_322fdc:\n"
 "st.aw blink,[sp,-20]\nmov_s r2,0x805c70\nld_s r2,[r2,0]\n"
 "stb_s r1,[sp,8]\nstb r1,[sp,7]\nsub_s r2,r0,r2\ndiv r2,r2,912\n"
 "cmp_s r1,0\nsth 0,[sp,16]\nst 0,[sp,12]\nstb 7,[sp,6]\n"
 "extb_s r1,r2\nmov_s r2,sp\nsth_s r1,[r2,10]\nsth_s r1,[r2,4]\n"
 "bne .Lopencfw_mode_stack20_dispatch\nmov r1,680\nld.as r2,[r0,169]\n"
 "ldh_s r0,[r0,r1]\nst_s r2,[sp,12]\nsth r0,[sp,16]\n"
 ".Lopencfw_mode_stack20_dispatch:\n"
 "bl.d opencfw_em9305_ll_event_callback_30e79c\nadd_s r0,sp,4\n"
 "ld.ab blink,[sp,20]\nj_s [blink]\n"
 ".size opencfw_em9305_mode_event_322fdc,.-opencfw_em9305_mode_event_322fdc\n");
uint32_t opencfw_em9305_mode_event_31ac3c(uintptr_t context)
{
 uint32_t flags=*(volatile uint32_t *)(context+636u);
 if((flags&(1u<<17u))==0u)return (uint32_t)context;
 uint32_t byte12=*(volatile uint8_t *)(context+12u);
 *(volatile uint32_t *)(context+636u)=flags&~(1u<<17u);
 *(volatile uint32_t *)(context+640u)=0u;
 return opencfw_em9305_mode_event_322fdc(context,byte12);
}
