/* SPDX-License-Identifier: MIT */
/* Clean-room retained runtime-context lifecycle and sequencing helpers. */
typedef __UINT32_TYPE__ open_cfw_ctxl_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_runtime_queue_create_416816(void);
extern void open_cfw_bootloader_runtime_dispatch_4160fe(void);
extern void open_cfw_bootloader_runtime_action_416200(void);
extern void open_cfw_bootloader_allocation_failure_41b2f8(void);
extern void open_cfw_bootloader_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_runtime_enable_41f8ba(void);
extern void open_cfw_bootloader_runtime_mode_set_41ba80(void);
extern void open_cfw_bootloader_runtime_commit_41c990(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_runtime_queue_context_init_42dd70(void)
{__asm volatile(
 "push {r4, lr}\nldr.w r4, [pc, #0x3e4]\nmovs r2, #0\nmovs r1, #0x28\nmovs r0, #0x32\n"
 "bl open_cfw_bootloader_runtime_queue_create_416816\nstr r0, [r4, #0xc]\n"
 "ldr r0, [r4, #0xc]\ncmp r0, #0\nbne 1f\n"
 "bl open_cfw_bootloader_allocation_failure_41b2f8\nmovs r0, #0\nmovs.w r1, #-1\n"
 "str r0, [r1]\n2:\nb 2b\n1:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_runtime_action_context_init_42ddae(void)
{__asm volatile(
 "push {r4, lr}\nldr.w r4, [pc, #0x3a4]\nldr.w r2, [pc, #0x3b8]\n"
 "movs r1, #0\nldr.w r0, [pc, #0x3b8]\n"
 "bl open_cfw_bootloader_runtime_dispatch_4160fe\nstr r0, [r4, #8]\n"
 "ldr r0, [r4, #8]\ncmp r0, #0\nbne 1f\n"
 "bl open_cfw_bootloader_allocation_failure_41b2f8\nmovs r0, #0\nmovs.w r1, #-1\n"
 "str r0, [r1]\n2:\nb 2b\n1:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_runtime_action_context_deinit_42ddda(void)
{__asm volatile(
 "push {r4, lr}\nldr.w r4, [pc, #0x378]\nldr r0, [r4, #8]\ncmp r0, #0\nbeq 1f\n"
 "ldr r0, [r4, #8]\nbl open_cfw_bootloader_runtime_action_416200\n"
 "movs r0, #0\nstr r0, [r4, #8]\n1:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_runtime_enable_sequence_42ddf2(void)
{__asm volatile(
 "push {r7, lr}\nbl open_cfw_bootloader_critical_enter_41b8ec\n"
 "movs r0, #1\nbl open_cfw_bootloader_runtime_enable_41f8ba\n"
 "movs r0, #0\nmov r8, r8\nmovs r0, #1\n"
 "bl open_cfw_bootloader_runtime_mode_set_41ba80\n"
 "bl open_cfw_bootloader_runtime_commit_41c990\npop {r0, pc}\n");}
#else
typedef open_cfw_ctxl_u32 (*open_cfw_ctxl_create_fn)(open_cfw_ctxl_u32,open_cfw_ctxl_u32,open_cfw_ctxl_u32);
typedef open_cfw_ctxl_u32 (*open_cfw_ctxl_dispatch_fn)(open_cfw_ctxl_u32,open_cfw_ctxl_u32,open_cfw_ctxl_u32);
typedef void (*open_cfw_ctxl_action_fn)(open_cfw_ctxl_u32);
typedef void (*open_cfw_ctxl_void_fn)(void);

__attribute__((used,noinline,visibility("default")))
open_cfw_ctxl_u32 open_cfw_bootloader_runtime_queue_context_init_42dd70_portable(
    open_cfw_ctxl_u32 *slot, open_cfw_ctxl_create_fn create)
{*slot=create(0x32U,0x28U,0U);return *slot!=0U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_ctxl_u32 open_cfw_bootloader_runtime_action_context_init_42ddae_portable(
    open_cfw_ctxl_u32 *slot, open_cfw_ctxl_u32 options,
    open_cfw_ctxl_u32 callback, open_cfw_ctxl_dispatch_fn dispatch)
{*slot=dispatch(options,0U,callback);return *slot!=0U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_ctxl_u32 open_cfw_bootloader_runtime_action_context_deinit_42ddda_portable(
    open_cfw_ctxl_u32 *slot, open_cfw_ctxl_action_fn action)
{if(*slot==0U)return 0U;action(*slot);*slot=0U;return 1U;}

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_runtime_enable_sequence_42ddf2_portable(
    open_cfw_ctxl_void_fn critical_enter, open_cfw_ctxl_action_fn enable,
    open_cfw_ctxl_action_fn set_mode, open_cfw_ctxl_void_fn commit)
{critical_enter();enable(1U);set_mode(1U);commit();}
#endif
