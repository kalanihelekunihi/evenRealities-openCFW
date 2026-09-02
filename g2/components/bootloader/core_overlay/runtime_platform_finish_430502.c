/* SPDX-License-Identifier: MIT */
/* Clean-room eight-slot hardware-context and event-service finalizer. */
typedef __UINT8_TYPE__ open_cfw_platform_finish_u8;
typedef __UINT32_TYPE__ open_cfw_platform_finish_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_context_claim_42c4c6(void);
extern void open_cfw_bootloader_callback_register_41d92c(void);
extern void open_cfw_bootloader_hw_config_transaction_42c988(void);
extern void open_cfw_bootloader_hw_instance_configure_42cc34(void);
extern void open_cfw_bootloader_hw_context_enable_42c538(void);
extern void open_cfw_bootloader_hw_config_retry_43048e(void);
extern void open_cfw_bootloader_event_object_create_416610(void);
extern void open_cfw_bootloader_hw_interrupt_enable_42c63a(void);
extern void open_cfw_bootloader_nvic_enable_bit_430470(void);
extern void open_cfw_bootloader_event_flags_create_416762(void);
extern void open_cfw_bootloader_log_4176ce(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_platform_finish_u32 open_cfw_bootloader_platform_finish_430502(void)
{
    __asm volatile(
        "push {r2,r3,r4,r5,r6,lr}\nmovs r6,#0\nmovs r4,#0\nb loop_test\n"
        "active_slot:\nlsls r0,r4,#4\nadd r0,r5\nadds r1,r0,#4\n"
        "lsls r0,r4,#4\nldr r0,[r5,r0]\n"
        "bl open_cfw_bootloader_hw_context_claim_42c4c6\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#8]\nldr r1,[r0,#8]\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#8]\nldr r0,[r0]\n"
        "bl open_cfw_bootloader_callback_register_41d92c\ncmp r0,#0\nbne fail_first_callback\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#8]\nldr r1,[r0,#0xc]\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#8]\nldr r0,[r0,#4]\n"
        "bl open_cfw_bootloader_callback_register_41d92c\ncmp r0,#0\nbne fail_second_callback\n"
        "movs r2,#0\nmovs r1,#0\nlsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#4]\n"
        "bl open_cfw_bootloader_hw_config_transaction_42c988\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r1,[r0,#0xc]\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#4]\n"
        "bl open_cfw_bootloader_hw_instance_configure_42cc34\n"
        "lsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#4]\n"
        "bl open_cfw_bootloader_hw_context_enable_42c538\nmovs r6,r0\n"
        "movs r0,r4\nuxtb r0,r0\nbl open_cfw_bootloader_hw_config_retry_43048e\n"
        "loop_next:\nadds r4,r4,#1\nloop_test:\ncmp r4,#8\nbhs slots_done\n"
        "ldr.w r5,[pc,#0xbc]\nlsls r0,r4,#4\nadd r0,r5\nldr r0,[r0,#8]\n"
        "cmp r0,#0\nbeq inactive_slot\nlsls r0,r4,#4\nadd r0,r5\n"
        "ldr r0,[r0,#0xc]\ncmp r0,#0\nbne slot_has_config\n"
        "inactive_slot:\nb loop_next\n"
        "slot_has_config:\nldr.w r6,[pc,#0xac]\nldr.w r0,[r6,r4,lsl #2]\n"
        "cmp r0,#0\nbne active_slot\nmovs r0,#0\n"
        "bl open_cfw_bootloader_event_object_create_416610\n"
        "str.w r0,[r6,r4,lsl #2]\nldr.w r0,[r6,r4,lsl #2]\n"
        "cmp r0,#0\nbne active_slot\nmovs r0,#1\nb finish\n"
        "fail_first_callback:\nmovs r0,#1\nb finish\n"
        "fail_second_callback:\nmovs r0,#1\nb finish\n"
        "slots_done:\nmovs r1,#0xff\nldr.w r0,[pc,#0x78]\nldr r0,[r0,#0x44]\n"
        "bl open_cfw_bootloader_hw_interrupt_enable_42c63a\n"
        "movs r0,#0xa\nbl open_cfw_bootloader_nvic_enable_bit_430470\n"
        "ldr.w r4,[pc,#0x74]\nmovs r2,#0\nmovs r1,#0\nmovs r0,#1\n"
        "bl open_cfw_bootloader_event_flags_create_416762\nstr r0,[r4]\n"
        "ldr r0,[r4]\ncmp r0,#0\nbne return_status\n"
        "ldr.w r0,[pc,#0x60]\nstr r0,[sp,#4]\nmovw r0,#0x131\nstr r0,[sp]\n"
        "ldr.w r3,[pc,#0x58]\nldr.w r2,[pc,#0x58]\nldr.w r1,[pc,#0x58]\n"
        "movs r0,#1\nbl open_cfw_bootloader_log_4176ce\nmovs r6,#1\n"
        "return_status:\nmovs r0,r6\nfinish:\npop {r1,r2,r4,r5,r6,pc}\n");
}
#else
typedef struct {
    open_cfw_platform_finish_u8 active;
    open_cfw_platform_finish_u8 event_present;
    open_cfw_platform_finish_u8 event_create_success;
    open_cfw_platform_finish_u32 first_callback_status;
    open_cfw_platform_finish_u32 second_callback_status;
    open_cfw_platform_finish_u32 context_enable_status;
    open_cfw_platform_finish_u32 claim_calls;
    open_cfw_platform_finish_u32 configure_calls;
    open_cfw_platform_finish_u32 retry_calls;
} open_cfw_platform_finish_slot;
typedef struct {
    open_cfw_platform_finish_slot slot[8];
    open_cfw_platform_finish_u8 global_event_create_success;
    open_cfw_platform_finish_u32 interrupt_enable_calls;
    open_cfw_platform_finish_u32 nvic_enable_calls;
    open_cfw_platform_finish_u32 global_event_create_calls;
    open_cfw_platform_finish_u32 log_calls;
} open_cfw_platform_finish_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_platform_finish_u32 open_cfw_bootloader_platform_finish_430502_portable(
    open_cfw_platform_finish_model *state)
{
    open_cfw_platform_finish_u32 index, status = 0U;
    if (state == 0U) return 1U;
    for (index = 0U; index < 8U; index++) {
        open_cfw_platform_finish_slot *slot = &state->slot[index];
        if (slot->active == 0U) continue;
        if (slot->event_present == 0U) {
            if (slot->event_create_success == 0U) return 1U;
            slot->event_present = 1U;
        }
        slot->claim_calls++;
        if (slot->first_callback_status != 0U) return 1U;
        if (slot->second_callback_status != 0U) return 1U;
        slot->configure_calls += 2U;
        status = slot->context_enable_status;
        slot->retry_calls++;
    }
    state->interrupt_enable_calls++;
    state->nvic_enable_calls++;
    state->global_event_create_calls++;
    if (state->global_event_create_success == 0U) {
        state->log_calls++;
        return 1U;
    }
    return status;
}
#endif
