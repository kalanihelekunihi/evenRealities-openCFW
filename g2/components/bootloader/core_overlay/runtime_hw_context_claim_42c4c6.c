/* SPDX-License-Identifier: MIT */
/* Clean-room hardware-context validation, ownership claim, and publication. */
typedef __UINT32_TYPE__ open_cfw_hw_claim_u32;
typedef __UINTPTR_TYPE__ open_cfw_hw_claim_uptr;

#define OPEN_CFW_HW_CLAIM_MAGIC 0x00123456U
#define OPEN_CFW_HW_CLAIM_STRIDE 0x000008A8U

#if defined(__arm__) || defined(__thumb__)
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_context_claim_42c4c6(void)
{__asm volatile(
 "push {r4,r5,r6}\ncmp r0,#8\nblo 1f\nmovs r0,#5\nb 4f\n"
 "1: cmp r1,#0\nbne 2f\nmovs r0,#6\nb 4f\n"
 "2: movw r3,#0x8a8\nldr.w r4,[pc,#0x8d4]\nmul r2,r3,r0\nldr r2,[r4,r2]\n"
 "ubfx r2,r2,#24,#1\ncmp r2,#0\nbeq 3f\nmovs r0,#7\nb 4f\n"
 "3: mul r2,r3,r0\nadd r2,r4\nldr r5,[r2]\norrs r5,r5,#0x1000000\nstr r5,[r2]\n"
 "mul r2,r3,r0\nadd r2,r4\nldr r5,[r2]\nbics r5,r5,#0x2000000\nstr r5,[r2]\n"
 "mul r2,r3,r0\nadd.w r5,r4,r2\nldr r6,[r5]\nands r6,r6,#0xff000000\n"
 "ldr.w r2,[pc,#0x898]\norrs r6,r2\nstr r6,[r5]\n"
 "mul r2,r3,r0\nadd r2,r4\nstr r0,[r2,#4]\nmuls r0,r3,r0\nadd r0,r4\nstr r0,[r1]\n"
 "movs r0,#0\n4: pop {r4,r5,r6}\nbx lr\n");}
#else
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_claim_u32 open_cfw_bootloader_hw_context_claim_42c4c6_portable(
    open_cfw_hw_claim_u32 index,
    open_cfw_hw_claim_u32 output_present,
    open_cfw_hw_claim_u32 *control_word,
    open_cfw_hw_claim_u32 *instance_word,
    open_cfw_hw_claim_uptr context_base,
    open_cfw_hw_claim_uptr *published_context)
{
    if(index>=8U)return 5U;
    if(output_present==0U)return 6U;
    if((*control_word&0x01000000U)!=0U)return 7U;
    *control_word=(*control_word&0xFC000000U)|0x01000000U|OPEN_CFW_HW_CLAIM_MAGIC;
    *instance_word=index;
    *published_context=context_base+(open_cfw_hw_claim_uptr)(OPEN_CFW_HW_CLAIM_STRIDE*index);
    return 0U;
}
#endif
