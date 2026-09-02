/* SPDX-License-Identifier: MIT */
/* Clean-room event-runtime setup and callback-dispatch wrappers. */
typedef __UINT32_TYPE__ open_cfw_evts_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_event_runtime_init_42e53c(void);
extern void open_cfw_bootloader_event_callback_dispatch_provider_42e284(void);
extern void open_cfw_bootloader_runtime_value_4161c6(void);
extern void open_cfw_bootloader_runtime_call_4161ce(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_runtime_setup_42e278(void)
{__asm volatile(
 "push {r7, lr}\n"
 "bl open_cfw_bootloader_event_runtime_init_42e53c\n"
 "bl open_cfw_bootloader_event_callback_dispatch_provider_42e284\n"
 "pop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_callback_dispatch_42e284(void)
{__asm volatile(
 "push {r7, lr}\n"
 "bl open_cfw_bootloader_runtime_value_4161c6\n"
 "movs r1, #8\n"
 "bl open_cfw_bootloader_runtime_call_4161ce\n"
 "ldr r0, [pc, #0x1dc]\n"
 "ldr r0, [r0]\n"
 "blx r0\n"
 "bl open_cfw_bootloader_runtime_value_4161c6\n"
 "movs r1, #0x30\n"
 "bl open_cfw_bootloader_runtime_call_4161ce\n"
 "pop {r0, pc}\n");}
#else
typedef void (*open_cfw_evts_void_fn)(void);
typedef open_cfw_evts_u32 (*open_cfw_evts_value_fn)(void);
typedef void (*open_cfw_evts_pair_fn)(open_cfw_evts_u32,open_cfw_evts_u32);

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_event_callback_dispatch_42e284_portable(
    open_cfw_evts_value_fn value,
    open_cfw_evts_pair_fn call,
    open_cfw_evts_void_fn callback)
{
    call(value(), 8U);
    callback();
    call(value(), 0x30U);
}

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_event_runtime_setup_42e278_portable(
    open_cfw_evts_void_fn initialize,
    open_cfw_evts_value_fn value,
    open_cfw_evts_pair_fn call,
    open_cfw_evts_void_fn callback)
{
    initialize();
    open_cfw_bootloader_event_callback_dispatch_42e284_portable(
        value, call, callback);
}
#endif
