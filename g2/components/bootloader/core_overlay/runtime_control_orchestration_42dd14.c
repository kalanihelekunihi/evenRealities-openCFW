/* SPDX-License-Identifier: MIT */
/* Clean-room event/control orchestration and critical dispatch transaction. */
typedef __UINT32_TYPE__ open_cfw_orch_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_control_one_wrapper_42dd9a(void);
extern void open_cfw_bootloader_runtime_queue_context_init_42dd70(void);
extern void open_cfw_bootloader_runtime_context_wrapper_42dd68(void);
extern void open_cfw_bootloader_noop_callback_42dd98(void);
extern void open_cfw_bootloader_control_two_wrapper_42dda4(void);
extern void open_cfw_bootloader_control_bits_dispatch_42e1c4(void);
extern void open_cfw_bootloader_event_wait_4162c4(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_memcpy_words_4156ac(void);
extern void open_cfw_bootloader_alignment_dispatch_42e4f4(void);
extern void open_cfw_bootloader_terminal_mode_42e514(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_orchestrator_42dd14(void)
{__asm volatile(
 "push {r5, r6, r7, lr}\n"
 "bl open_cfw_bootloader_control_one_wrapper_42dd9a\n"
 "bl open_cfw_bootloader_runtime_queue_context_init_42dd70\n"
 "bl open_cfw_bootloader_runtime_context_wrapper_42dd68\n"
 "bl open_cfw_bootloader_noop_callback_42dd98\n"
 "bl open_cfw_bootloader_control_two_wrapper_42dda4\nb 2f\n"
 "1:\nbl open_cfw_bootloader_control_bits_dispatch_42e1c4\n"
 "2:\nmovs.w r2, #-1\nmovs r1, #0\nmvns r0, #0xff000000\n"
 "bl open_cfw_bootloader_event_wait_4162c4\ncmp r0, #0\nbeq 3f\n"
 "cmp.w r0, #-0x80000000\nblo 1b\n"
 "3:\nldr.w r0, [pc, #0x41c]\nstr r0, [sp, #4]\nmovw r0, #0x199\nstr r0, [sp]\n"
 "ldr.w r3, [pc, #0x414]\nldr.w r2, [pc, #0x3b8]\nldr.w r1, [pc, #0x3b8]\n"
 "movs r0, #1\nbl open_cfw_bootloader_log_4176ce\nb 2b\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_critical_dispatch_transaction_42de0e(void)
{__asm volatile(
 "push {r3, r4, r5, lr}\nsub sp, #0x10\n"
 "ldr r0, [pc, #0x364]\nstr r0, [sp, #4]\nmovw r0, #0x1f9\nstr r0, [sp]\n"
 "ldr r3, [pc, #0x35c]\nldr r2, [pc, #0x2f4]\nldr r1, [pc, #0x2f4]\nmovs r0, #1\n"
 "bl open_cfw_bootloader_log_4176ce\nldr r4, [pc, #0x354]\n"
 "bl open_cfw_bootloader_critical_enter_41b8ec\nmovs r5, r0\nmov r0, sp\n"
 "ldr r1, [pc, #0x350]\nmovs r2, #0x10\nbl open_cfw_bootloader_memcpy_words_4156ac\n"
 "movs r3, #4\nmovs r2, r4\nmov r1, sp\nldr r0, [pc, #0x344]\n"
 "bl open_cfw_bootloader_alignment_dispatch_42e4f4\nmovs r0, r5\nmsr primask, r0\n"
 "movs r1, #0\nmovs r0, #0\nbl open_cfw_bootloader_terminal_mode_42e514\n"
 "add sp, #0x14\npop {r4, r5, pc}\n");}
#else
typedef open_cfw_orch_u32 (*open_cfw_orch_dispatch_fn)(const open_cfw_orch_u32 *,open_cfw_orch_u32,open_cfw_orch_u32);

__attribute__((used,noinline,visibility("default")))
open_cfw_orch_u32 open_cfw_bootloader_control_orchestrator_step_42dd14_portable(
    open_cfw_orch_u32 wait_status)
{return wait_status!=0U&&wait_status<0x80000000U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_orch_u32 open_cfw_bootloader_critical_dispatch_transaction_42de0e_portable(
    const open_cfw_orch_u32 source[4],open_cfw_orch_u32 copy[4],
    open_cfw_orch_u32 handle,open_cfw_orch_u32 control,
    open_cfw_orch_dispatch_fn dispatch)
{open_cfw_orch_u32 i;for(i=0;i<4U;i++)copy[i]=source[i];return dispatch(copy,handle,control);}
#endif
