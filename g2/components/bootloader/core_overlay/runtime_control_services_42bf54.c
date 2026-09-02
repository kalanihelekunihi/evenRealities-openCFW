/* SPDX-License-Identifier: MIT */
/* Clean-room readiness, event wait, guarded dispatch, and enable controls. */
typedef __UINT32_TYPE__ open_cfw_ctrls_u32;
typedef __UINT8_TYPE__ open_cfw_ctrls_u8;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_query_41bf84(void);
extern void open_cfw_bootloader_float_probe_41ca2c(void);
extern void open_cfw_bootloader_delay_status_change_41d21c(void);
extern void open_cfw_bootloader_runtime_transfer_41623a(void);
extern void open_cfw_bootloader_runtime_flags_wait_416590(void);
extern void open_cfw_bootloader_log_4176ce(void);
extern void open_cfw_bootloader_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_runtime_lock_41bd92(void);
extern void open_cfw_bootloader_guarded_call_cleanup_42e8a4(void);
extern void open_cfw_bootloader_runtime_unlock_41bde4(void);
extern void open_cfw_bootloader_delay_cycles_41d1c0(void);
extern void open_cfw_bootloader_power_control_41c838(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hardware_readiness_gate_42bf54(void)
{__asm volatile(
 "push {r5, r6, r7, lr}\nldr r0, [pc, #0x80]\nldr r0, [r0]\ncmp r0, #0\nbne 4f\n"
 "ldr r0, [pc, #0x7c]\nldr r0, [r0]\ncmp r0, #0\nbne 4f\n"
 "movs r0, #0x1d\nbl open_cfw_bootloader_mode_query_41bf84\ncmp r0, #0\nbeq 1f\n"
 "movs r0, #1\nb 7f\n1:\nmov r0, sp\nvldr s0, [pc, #0x2c]\n"
 "bl open_cfw_bootloader_float_probe_41ca2c\ncmp r0, #0\nbne 5f\n"
 "movs r3, #0\nmovs r2, #1\nldr r1, [pc, #0xa8]\nmovw r0, #0x9c4\n"
 "bl open_cfw_bootloader_delay_status_change_41d21c\ncmp r0, #0\nbeq 3f\n"
 "movs r0, #4\nb 7f\n4:\nmovs r0, #1\nb 7f\n"
 "5:\nmovs r0, #1\nb 7f\n3:\nmovs r0, #0\n"
 "7:\npop {r1, r2, r3, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_event_wait_mask_42e2a2(void)
{__asm volatile(
 "push {r3, r4, r5, lr}\nsub sp, #0x10\nmovs r4, r1\nmovs r5, #1\nlsls r5, r4\n"
 "movs.w r1, #0x800000\nbl open_cfw_bootloader_runtime_transfer_41623a\n"
 "movw r3, #0x4e20\nmovs r2, #1\nmovs r1, r5\nldr r0, [pc, #0x1ac]\n"
 "ldr r0, [r0, #0x1c]\nbl open_cfw_bootloader_runtime_flags_wait_416590\n"
 "ands.w r1, r5, r0\ncmp r1, r5\nbeq 1f\nuxtb r4, r4\nstr r4, [sp, #0xc]\n"
 "str r0, [sp, #8]\nldr r0, [pc, #0x1a0]\nstr r0, [sp, #4]\n"
 "movs r0, #0x87\nstr r0, [sp]\nldr r3, [pc, #0x19c]\nldr r2, [pc, #0x184]\n"
 "ldr r1, [pc, #0x188]\nmovs r0, #1\nbl open_cfw_bootloader_log_4176ce\n"
 "1:\nadd sp, #0x14\npop {r4, r5, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_aligned_guarded_dispatch_42e4a0(void)
{__asm volatile(
 "push {r1, r2, r3, r4, r5, r6, r7, lr}\nmovs r4, r0\nmovs r5, r1\n"
 "movs r6, r2\nmovs r7, r3\nands r0, r6, #3\ncmp r0, #0\nbeq 1f\n"
 "ldr r0, [pc, #0x5c]\nb 4f\n1:\nsubs.w r6, r6, #0x400000\nlsrs r6, r6, #2\n"
 "bl open_cfw_bootloader_critical_enter_41b8ec\nstr r0, [sp, #4]\n"
 "bl open_cfw_bootloader_runtime_lock_41bd92\nstr r7, [sp]\nmovs r3, r6\n"
 "movs r2, r5\nmovs r1, #1\nmovs r0, r4\n"
 "bl open_cfw_bootloader_guarded_call_cleanup_42e8a4\nmovs r4, r0\n"
 "bl open_cfw_bootloader_runtime_unlock_41bde4\nldr r0, [sp, #4]\nmsr primask, r0\n"
 "cmp r4, #0\nbne 2f\nmovs r4, #0\nb 3f\n"
 "2:\norr r4, r4, #0x8000000\norrs r4, r4, #0x100\n3:\nmovs r0, r4\n"
 "4:\npop {r1, r2, r3, r4, r5, r6, r7, pc}\n");}

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_register_power_toggle_42f1c8(void)
{__asm volatile(
 "push {r7, lr}\nuxtb r0, r0\ncmp r0, #0\nbeq 1f\n"
 "ldr.w r0, [pc, #0x41c]\nldr r1, [r0]\norrs r1, r1, #1\nstr r1, [r0]\n"
 "movs r0, #5\nbl open_cfw_bootloader_delay_cycles_41d1c0\nmovs r0, #1\n"
 "bl open_cfw_bootloader_power_control_41c838\nb 2f\n"
 "1:\nmovs r0, #0\nbl open_cfw_bootloader_power_control_41c838\n"
 "movs r0, #5\nbl open_cfw_bootloader_delay_cycles_41d1c0\n"
 "ldr.w r0, [pc, #0x3f8]\nldr r1, [r0]\nlsrs r1, r1, #1\nlsls r1, r1, #1\nstr r1, [r0]\n"
 "2:\npop {r0, pc}\n");}
#else
typedef open_cfw_ctrls_u32 (*open_cfw_ctrls_unary_fn)(open_cfw_ctrls_u32);
typedef open_cfw_ctrls_u32 (*open_cfw_ctrls_wait_fn)(open_cfw_ctrls_u32,open_cfw_ctrls_u32,open_cfw_ctrls_u32);
typedef open_cfw_ctrls_u32 (*open_cfw_ctrls_dispatch_fn)(open_cfw_ctrls_u32,open_cfw_ctrls_u32,open_cfw_ctrls_u32,open_cfw_ctrls_u32,open_cfw_ctrls_u32);
typedef void (*open_cfw_ctrls_void_fn)(void);

__attribute__((used,noinline,visibility("default")))
open_cfw_ctrls_u32 open_cfw_bootloader_hardware_readiness_gate_42bf54_portable(
    open_cfw_ctrls_u32 busy_a, open_cfw_ctrls_u32 busy_b,
    open_cfw_ctrls_u32 mode_result, open_cfw_ctrls_u32 float_result,
    open_cfw_ctrls_u32 delay_result)
{if(busy_a||busy_b||mode_result||float_result)return 1U;return delay_result?4U:0U;}

__attribute__((used,noinline,visibility("default")))
open_cfw_ctrls_u32 open_cfw_bootloader_event_wait_mask_42e2a2_portable(
    open_cfw_ctrls_u32 handle, open_cfw_ctrls_u32 bit,
    open_cfw_ctrls_u32 event_handle, open_cfw_ctrls_wait_fn wait,
    open_cfw_ctrls_unary_fn transfer)
{open_cfw_ctrls_u32 mask=1U<<bit;transfer(handle);return (wait(event_handle,mask,0x4e20U)&mask)==mask;}

__attribute__((used,noinline,visibility("default")))
open_cfw_ctrls_u32 open_cfw_bootloader_aligned_guarded_dispatch_42e4a0_portable(
    open_cfw_ctrls_u32 handle, open_cfw_ctrls_u32 value,
    open_cfw_ctrls_u32 address, open_cfw_ctrls_u32 extra,
    open_cfw_ctrls_u32 alignment_error, open_cfw_ctrls_dispatch_fn dispatch)
{open_cfw_ctrls_u32 result;if(address&3U)return alignment_error;result=dispatch(handle,1U,value,(address-0x400000U)>>2,extra);return result?(result|0x08000100U):0U;}

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_register_power_toggle_42f1c8_portable(
    open_cfw_ctrls_u32 enable, open_cfw_ctrls_u32 *control,
    open_cfw_ctrls_unary_fn power, open_cfw_ctrls_unary_fn delay)
{if(enable){*control|=1U;delay(5U);power(1U);}else{power(0U);delay(5U);*control&=~1U;}}
#endif
