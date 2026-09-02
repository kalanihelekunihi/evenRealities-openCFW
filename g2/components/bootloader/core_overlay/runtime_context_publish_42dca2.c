/* SPDX-License-Identifier: MIT */
/* Clean-room queued runtime-context publication and event notification. */
typedef __UINT32_TYPE__ open_cfw_ctx_publish_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_queue_send_4168a2(void);
extern void open_cfw_bootloader_runtime_transfer_41623a(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_runtime_context_publish_42dca2(void)
{__asm volatile(
 "push {r1, r2, r3, r4, r5, lr}\nmovs r1, r0\nmovs r4, #1\n"
 "ldr.w r5, [pc, #0x4ac]\nldr r0, [r5, #0xc]\ncmp r0, #0\nbne 1f\n"
 "ldr.w r0, [pc, #0x4a8]\nstr r0, [sp, #4]\nmov.w r0, #0x164\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x4a0]\nldr.w r2, [pc, #0x450]\nldr.w r1, [pc, #0x450]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nmovs r0, #0\nb 3f\n"
 "1:\nmovs r3, #0\nmovs r2, #0\nldr r0, [r5, #0xc]\n"
 "bl open_cfw_bootloader_queue_send_4168a2\ncmp r0, #0\nbeq 2f\n"
 "ldr.w r0, [pc, #0x480]\nstr r0, [sp, #4]\nmovw r0, #0x169\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x470]\nldr.w r2, [pc, #0x420]\nldr.w r1, [pc, #0x420]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nmovs r4, #0\nb 4f\n"
 "2:\nmovs.w r1, #0x400000\nldr r0, [r5, #8]\n"
 "bl open_cfw_bootloader_runtime_transfer_41623a\n"
 "4:\nmovs r0, r4\nuxtb r0, r0\n3:\npop {r1, r2, r3, r4, r5, pc}\n");}
#else
__attribute__((used,noinline,visibility("default")))
open_cfw_ctx_publish_u32 open_cfw_bootloader_runtime_context_publish_42dca2_portable(
    open_cfw_ctx_publish_u32 queue_ready,open_cfw_ctx_publish_u32 send_status,
    open_cfw_ctx_publish_u32 *event_mask)
{if(queue_ready==0U)return 0U;if(send_status!=0U)return 0U;*event_mask|=0x00400000U;return 1U;}
#endif
