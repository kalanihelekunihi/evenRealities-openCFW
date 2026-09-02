/* SPDX-License-Identifier: MIT */
/* Clean-room retained event-state probe, initialization, and control services. */
typedef __UINT32_TYPE__ open_cfw_evst_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_event_flags_create_4164da(void);
extern void open_cfw_bootloader_allocation_failure_41b2f8(void);
extern void open_cfw_bootloader_runtime_prepare_416058(void);
extern void open_cfw_bootloader_runtime_dispatch_4160fe(void);
extern void open_cfw_bootloader_runtime_finalize_4160b0(void);
extern void open_cfw_bootloader_event_wait_4162c4(void);
extern void open_cfw_bootloader_event_bits_set_41652e(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_retained_state_probe_42e224(void)
{__asm volatile(
 "push {r0, r1, r2, r3, r4, lr}\nldr r0, [pc, #0x230]\nmovs r1, #0\n"
 "ldr r4, [r0]\nstr r4, [sp, #8]\nldr r0, [pc, #0x22c]\nstr r0, [sp, #4]\n"
 "movs r0, #0x40\nstr r0, [sp]\nldr r3, [pc, #0x228]\nldr r2, [pc, #0x228]\n"
 "ldr r1, [pc, #0x22c]\nmovs r0, #3\nbl open_cfw_bootloader_log_4176ce\n"
 "cmp.w r4, #0x55555555\nbne 1f\nmovs r0, #1\nb 2f\n1:\nmovs r0, #0\n"
 "2:\nuxtb r0, r0\nadd sp, #0x10\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_flags_init_42e254(void)
{__asm volatile(
 "push {r4, lr}\nldr r4, [pc, #0x214]\nmovs r0, #0\n"
 "bl open_cfw_bootloader_event_flags_create_4164da\nstr r0, [r4, #0x1c]\n"
 "ldr r0, [r4, #0x1c]\ncmp r0, #0\nbne 1f\n"
 "bl open_cfw_bootloader_allocation_failure_41b2f8\nmovs r0, #0\nmovs.w r1, #-1\n"
 "str r0, [r1]\n2:\nb 2b\n1:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_guard_context_init_42e39c(void)
{__asm volatile(
 "push {r4, lr}\nbl open_cfw_bootloader_runtime_prepare_416058\n"
 "ldr r4, [pc, #0xc8]\nldr r2, [pc, #0xe0]\nmovs r1, #0\nldr r0, [pc, #0xe0]\n"
 "bl open_cfw_bootloader_runtime_dispatch_4160fe\nstr r0, [r4, #8]\n"
 "ldr r0, [r4, #8]\ncmp r0, #0\nbne 1f\n"
 "bl open_cfw_bootloader_allocation_failure_41b2f8\nmovs r0, #0\nmovs.w r1, #-1\n"
 "str r0, [r1]\n2:\nb 2b\n1:\nbl open_cfw_bootloader_runtime_finalize_4160b0\n"
 "pop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_one_wait_42e3e0(void)
{__asm volatile(
 "push {r0, r1, r2, r3, r4, lr}\nmovs r4, r0\n"
 "1:\nmovs.w r2, #-1\nmovs r1, #1\nmovs.w r0, #0x800000\n"
 "bl open_cfw_bootloader_event_wait_4162c4\nlsls r0, r0, #8\nbpl 1b\n"
 "uxtb r4, r4\nstr r4, [sp, #8]\nldr r0, [pc, #0x94]\nstr r0, [sp, #4]\n"
 "movw r0, #0x12b\nstr r0, [sp]\nldr r3, [pc, #0x8c]\nldr r2, [pc, #0x5c]\n"
 "ldr r1, [pc, #0x5c]\nmovs r0, #3\nbl open_cfw_bootloader_log_4176ce\n"
 "pop {r0, r1, r2, r3, r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_control_two_publish_42e412(void)
{__asm volatile(
 "push {r0, r1, r2, r3, r4, lr}\nmovs r4, r0\nmovs r0, r4\nuxtb r0, r0\n"
 "str r0, [sp, #8]\nldr r0, [pc, #0x78]\nstr r0, [sp, #4]\n"
 "movw r0, #0x139\nstr r0, [sp]\nldr r3, [pc, #0x74]\nldr r2, [pc, #0x38]\n"
 "ldr r1, [pc, #0x3c]\nmovs r0, #3\nbl open_cfw_bootloader_log_4176ce\n"
 "movs r0, #1\nlsls.w r4, r0, r4\nmovs r1, r4\n"
 "ldr r0, [pc, #0x30]\nldr r0, [r0, #0x1c]\n"
 "bl open_cfw_bootloader_event_bits_set_41652e\n"
 "pop {r0, r1, r2, r3, r4, pc}\n");}
#else
typedef open_cfw_evst_u32 (*open_cfw_evst_unary_fn)(open_cfw_evst_u32);
typedef open_cfw_evst_u32 (*open_cfw_evst_dispatch_fn)(open_cfw_evst_u32,open_cfw_evst_u32,open_cfw_evst_u32);
typedef open_cfw_evst_u32 (*open_cfw_evst_wait_fn)(open_cfw_evst_u32,open_cfw_evst_u32,open_cfw_evst_u32);
typedef void (*open_cfw_evst_pair_fn)(open_cfw_evst_u32,open_cfw_evst_u32);
typedef void (*open_cfw_evst_void_fn)(void);
__attribute__((used,noinline,visibility("default"))) open_cfw_evst_u32 open_cfw_bootloader_retained_state_probe_42e224_portable(open_cfw_evst_u32 value){return value==0x55555555U;}
__attribute__((used,noinline,visibility("default"))) open_cfw_evst_u32 open_cfw_bootloader_event_flags_init_42e254_portable(open_cfw_evst_u32 *slot,open_cfw_evst_unary_fn create){*slot=create(0U);return *slot!=0U;}
__attribute__((used,noinline,visibility("default"))) open_cfw_evst_u32 open_cfw_bootloader_guard_context_init_42e39c_portable(open_cfw_evst_u32 *slot,open_cfw_evst_u32 options,open_cfw_evst_u32 callback,open_cfw_evst_void_fn prepare,open_cfw_evst_dispatch_fn dispatch,open_cfw_evst_void_fn finalize){prepare();*slot=dispatch(options,0U,callback);if(*slot!=0U)finalize();return *slot!=0U;}
__attribute__((used,noinline,visibility("default"))) open_cfw_evst_u32 open_cfw_bootloader_control_one_wait_42e3e0_portable(open_cfw_evst_u32 handle,open_cfw_evst_wait_fn wait){open_cfw_evst_u32 calls=0U;do{calls++;}while((wait(handle,1U,~0U)&0x00800000U)==0U);return calls;}
__attribute__((used,noinline,visibility("default"))) void open_cfw_bootloader_control_two_publish_42e412_portable(open_cfw_evst_u32 handle,open_cfw_evst_u32 bit,open_cfw_evst_pair_fn publish){publish(handle,1U<<bit);}
#endif
