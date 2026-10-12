#include <stdint.h>
extern uint32_t opencfw_em9305_init_callback_32c254(void);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
/* Full native32c254..32c2ae. Named source preserves28Bframe, including
 * untouched5..7 and24..26 bytes and handler27. BaselineLD avoids requiring
 * alternateCD2compactencoding. Sourceplacement/byteequalityunproved. */
__asm__(
".text\n.align 2\n.global opencfw_em9305_init_callback_32c254\n"
".type opencfw_em9305_init_callback_32c254,@function\n"
"opencfw_em9305_init_callback_32c254:\n"
"enter_s [r13-r14,fp,blink]\n"
"sub_s sp,sp,28\n"
"mov_s r14,21\n"
"asl_s r14,r14,16\n"
"1: mov_s r0,0x8053f8\n"
"bl.d opencfw_em9305_wsf_event_remove\n"
"add r1,sp,27\n"
"mov_s r13,r0\n"
"breq_s r0,0,4f\n"
"st 0,[sp,20]\n"
"st 0,[sp,16]\n"
"ld r0,[r13,20]\n"
"ld r1,[r13,16]\n"
"st_s r14,[sp,0]\n"
"st_s r0,[sp,12]\n"
"ldb_s r2,[r13,12]\n"
"st_s r1,[sp,8]\n"
"stb_s r2,[sp,4]\n"
"ld r12,[r13,8]\n"
"ld r3,[r13,4]\n"
"xor_s r0,r0,r12\n"
"xor_s r1,r1,r3\n"
"or.f 0,r1,r0\n"
"bne_s 2f\n"
"ldb_s r0,[r13,0]\n"
"breq r2,r0,3f\n"
"2: bset_s r2,r2,1\n"
"st_s r3,[sp,16]\n"
"st_s r12,[sp,20]\n"
"stb_s r2,[sp,4]\n"
"3: bl.d opencfw_em9305_ll_event_callback_30e79c\n"
"add_s r0,sp,0\n"
"bl.d opencfw_em9305_wsf_event_release\n"
"mov_s r0,r13\n"
"b_s 1b\n"
"4: leave_s [r13-r14,fp,blink,pcl]\n"
".size opencfw_em9305_init_callback_32c254,.-opencfw_em9305_init_callback_32c254\n");
