/* SPDX-License-Identifier: MIT */
/* Clean-room retained-event initialization and bounded-wait service loop. */
typedef __UINT32_TYPE__ open_cfw_event_loop_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_event_flags_init_42e254(void);
extern void open_cfw_bootloader_noop_callback_42e276(void);
extern void open_cfw_bootloader_event_runtime_setup_42e278(void);
extern void open_cfw_bootloader_event_wait_one_wrapper_42e2ea(void);
extern void open_cfw_bootloader_retained_state_probe_42e224(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_memset_wrapper_426c10(void);
extern void open_cfw_bootloader_runtime_context_create_42dca2(void);
extern void open_cfw_bootloader_noop_callback_42e39a(void);
extern void open_cfw_bootloader_event_wait_4162c4(void);
extern void open_cfw_bootloader_runtime_time_4160e8(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_service_loop_42e2f8(void)
{__asm volatile(
 "push {r4, r5, r6, lr}\nsub sp, #0x50\nmovs r5, #0\n"
 "bl open_cfw_bootloader_event_flags_init_42e254\n"
 "bl open_cfw_bootloader_noop_callback_42e276\n"
 "bl open_cfw_bootloader_event_runtime_setup_42e278\n"
 "bl open_cfw_bootloader_event_wait_one_wrapper_42e2ea\n"
 "bl open_cfw_bootloader_retained_state_probe_42e224\ncmp r0, #0\nbeq 2f\n"
 "ldr r0, [pc, #0x164]\nstr r0, [sp, #4]\nmovs r0, #0xd1\nstr r0, [sp]\n"
 "ldr r3, [pc, #0x160]\nldr r2, [pc, #0x140]\nldr r1, [pc, #0x144]\nmovs r0, #3\n"
 "bl open_cfw_bootloader_log_4176ce\nmovs r2, #0x28\nmovs r1, #0\nadd r0, sp, #0x28\n"
 "bl open_cfw_bootloader_memset_wrapper_426c10\nmovs r0, #1\nstr r0, [sp, #0x28]\n"
 "add r0, sp, #0x28\nbl open_cfw_bootloader_runtime_context_create_42dca2\nb 4f\n"
 "2:\nldr r0, [pc, #0x140]\nstr r0, [sp, #4]\nmovs r0, #0xd8\nstr r0, [sp]\n"
 "ldr r3, [pc, #0x134]\nldr r2, [pc, #0x118]\nldr r1, [pc, #0x118]\nmovs r0, #3\n"
 "bl open_cfw_bootloader_log_4176ce\nmovs r2, #0x28\nmovs r1, #0\nmov r0, sp\n"
 "bl open_cfw_bootloader_memset_wrapper_426c10\nmovs r0, #0\nstr r0, [sp]\nmov r0, sp\n"
 "bl open_cfw_bootloader_runtime_context_create_42dca2\nb 4f\n"
 "3:\nmovs r0, r4\nbl open_cfw_bootloader_noop_callback_42e39a\n"
 "4:\nmovw r6, #0xea60\nmovs r2, r6\nmovs r1, #0\nmvns r0, #0xff000000\n"
 "bl open_cfw_bootloader_event_wait_4162c4\nmovs r4, r0\n"
 "bl open_cfw_bootloader_runtime_time_4160e8\ncmp r4, #0\nbeq 5f\n"
 "cmp.w r4, #-0x80000000\nblo 3b\n5:\nsubs r1, r0, r5\ncmp r1, r6\nblo 4b\n"
 "movs r5, r0\nb 4b\n");}
#else
typedef void (*open_cfw_event_loop_void_fn)(void);

__attribute__((used,noinline,visibility("default")))
open_cfw_event_loop_u32 open_cfw_bootloader_event_service_context_42e2f8_portable(
    open_cfw_event_loop_u32 retained_state,
    open_cfw_event_loop_u32 context[10])
{open_cfw_event_loop_u32 i;for(i=0;i<10U;i++)context[i]=0U;context[0]=retained_state?1U:0U;return retained_state?0xd1U:0xd8U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_event_loop_u32 open_cfw_bootloader_event_service_step_42e2f8_portable(
    open_cfw_event_loop_u32 wait_status,open_cfw_event_loop_u32 now,
    open_cfw_event_loop_u32 last,open_cfw_event_loop_void_fn callback)
{if(wait_status!=0U&&wait_status<0x80000000U)callback();return now-last<60000U?last:now;}
#endif
