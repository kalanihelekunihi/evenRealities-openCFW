/* SPDX-License-Identifier: MIT */
/* Clean-room event wait, guarded teardown, and event-bit control wrappers. */
typedef __UINT32_TYPE__ open_cfw_evtc_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_event_wait_42e2a2(void);
extern void open_cfw_bootloader_guarded_action_416200(void);
extern void open_cfw_bootloader_event_bits_set_41652e(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_wait_one_wrapper_42e2ea(void)
{__asm volatile(
 "push {r7, lr}\nmovs r1, #1\nldr r0, [pc, #0x180]\nldr r0, [r0, #8]\n"
 "bl open_cfw_bootloader_event_wait_42e2a2\npop {r0, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_guarded_context_teardown_42e3ca(void)
{__asm volatile(
 "push {r4, lr}\nldr r4, [pc, #0x9c]\nldr r0, [r4, #8]\ncmp r0, #0\nbeq 1f\n"
 "ldr r0, [r4, #8]\nbl open_cfw_bootloader_guarded_action_416200\nmovs r0, #0\n"
 "str r0, [r4, #8]\n1:\npop {r4, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_bit_set_42e444(void)
{__asm volatile(
 "push {r7, lr}\nmovs r1, r0\nmovs r0, #1\nlsls.w r1, r0, r1\n"
 "ldr r0, [pc, #0x1c]\nldr r0, [r0, #0x1c]\n"
 "bl open_cfw_bootloader_event_bits_set_41652e\npop {r0, pc}\n");}
#else
typedef void (*open_cfw_evtc_pair_fn)(open_cfw_evtc_u32,open_cfw_evtc_u32);
typedef void (*open_cfw_evtc_action_fn)(open_cfw_evtc_u32);
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_event_wait_one_wrapper_42e2ea_portable(open_cfw_evtc_u32 handle,open_cfw_evtc_pair_fn wait){wait(handle,1U);}
__attribute__((used,noinline,visibility("default")))
open_cfw_evtc_u32 open_cfw_bootloader_guarded_context_teardown_42e3ca_portable(open_cfw_evtc_u32 *context,open_cfw_evtc_action_fn action)
{if(*context==0U)return 0U;action(*context);*context=0U;return 1U;}
__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_event_bit_set_42e444_portable(open_cfw_evtc_u32 handle,open_cfw_evtc_u32 bit,open_cfw_evtc_pair_fn publish){publish(handle,1U<<bit);}
#endif
