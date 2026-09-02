/* SPDX-License-Identifier: MIT */
/* Clean-room runtime context, control, and terminal-notification wrappers. */
typedef __UINT32_TYPE__ open_cfw_ctrl_u32;

#if defined(__arm__) || defined(__thumb__)
extern open_cfw_ctrl_u32 open_cfw_bootloader_runtime_context_get_42d88a(void);
extern void open_cfw_bootloader_control_one_42e3e0(void);
extern void open_cfw_bootloader_control_two_42e412(void);
extern void open_cfw_bootloader_control_fault_42de58(void);
extern void open_cfw_bootloader_control_terminal_42e444(void);
extern void open_cfw_bootloader_control_terminal_loop_provider_42e1da(void);
extern void open_cfw_bootloader_runtime_notify_416378(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_ctrl_u32 open_cfw_bootloader_runtime_context_wrapper_42dd68(void)
{__asm volatile("push {r7, lr}\nbl open_cfw_bootloader_runtime_context_get_42d88a\npop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_one_wrapper_42dd9a(void)
{__asm volatile("push {r7, lr}\nmovs r0, #1\nbl open_cfw_bootloader_control_one_42e3e0\npop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_two_wrapper_42dda4(void)
{__asm volatile("push {r7, lr}\nmovs r0, #1\nbl open_cfw_bootloader_control_two_42e412\npop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_bits_dispatch_42e1c4(void)
{__asm volatile(
 "push {r4, lr}\nmovs r4, r0\nlsls r0, r4, #9\nbpl 1f\n"
 "bl open_cfw_bootloader_control_fault_42de58\n1:\nlsls r0, r4, #8\nbpl 2f\n"
 "bl open_cfw_bootloader_control_terminal_loop_provider_42e1da\n2:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,noreturn,visibility("default")))
void open_cfw_bootloader_control_terminal_loop_42e1da(void)
{__asm volatile(
 "push {r7, lr}\nmovs r0, #1\nbl open_cfw_bootloader_control_terminal_42e444\n"
 "1:\nmovs.w r0, #-1\nbl open_cfw_bootloader_runtime_notify_416378\nb 1b\n");}
#else
typedef open_cfw_ctrl_u32 (*open_cfw_ctrl_value_fn)(void);
typedef void (*open_cfw_ctrl_action_fn)(open_cfw_ctrl_u32);
__attribute__((used,noinline,visibility("default")))
open_cfw_ctrl_u32 open_cfw_bootloader_runtime_context_wrapper_42dd68_portable(open_cfw_ctrl_value_fn provider){return provider();}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_control_one_wrapper_42dd9a_portable(open_cfw_ctrl_action_fn provider){provider(1U);}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_control_two_wrapper_42dda4_portable(open_cfw_ctrl_action_fn provider){provider(1U);}
__attribute__((used,noinline,visibility("default")))
open_cfw_ctrl_u32 open_cfw_bootloader_control_bits_dispatch_42e1c4_portable(open_cfw_ctrl_u32 flags,open_cfw_ctrl_action_fn fault,open_cfw_ctrl_action_fn terminal)
{open_cfw_ctrl_u32 calls=0U;if((flags&(1U<<22))!=0U){fault(1U);calls|=1U;}if((flags&(1U<<23))!=0U){terminal(1U);calls|=2U;}return calls;}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_control_terminal_step_42e1da_portable(open_cfw_ctrl_action_fn terminal,open_cfw_ctrl_action_fn notify){terminal(1U);notify(~0U);}
#endif
