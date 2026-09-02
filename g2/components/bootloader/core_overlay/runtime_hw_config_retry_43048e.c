/* SPDX-License-Identifier: MIT */
/* Clean-room bounded hardware-configuration retry and callback setup service. */
typedef __UINT8_TYPE__ open_cfw_hw_retry_u8;
typedef __UINT32_TYPE__ open_cfw_hw_retry_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_callback_register_41d92c(void);
extern void open_cfw_bootloader_delay_us_41f9d8(void);
extern void open_cfw_bootloader_hw_config_transaction_42c988(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_config_retry_43048e(void)
{__asm volatile(
 "push {r3,r4,r5,r6,r7,lr}\nmovs r5,r0\nmovs r4,#0\nmovs r0,r5\nuxtb r0,r0\n"
 "cmp r0,#4\nbne retry_init\nldr.w r6,[pc,#0x1a0]\nldr.w r7,[pc,#0x1a0]\n"
 "ldr r1,[r7]\nmovs r0,r5\nuxtb r0,r0\nlsls r0,r0,#4\nadd r0,r6\n"
 "ldr r0,[r0,#8]\nldr r0,[r0]\nbl open_cfw_bootloader_callback_register_41d92c\n"
 "ldr r1,[r7]\nmovs r0,r5\nuxtb r0,r0\nlsls r0,r0,#4\nadd r0,r6\n"
 "ldr r0,[r0,#8]\nldr r0,[r0,#4]\nbl open_cfw_bootloader_callback_register_41d92c\n"
 "retry_init: movs r6,#0\nb retry_test\n"
 "retry_delay: movs r0,#0xa\nbl open_cfw_bootloader_delay_us_41f9d8\nadds r6,r6,#1\n"
 "retry_test: cmp.w r6,#0x3e8\nbge retry_done\nmovs r2,#1\nmovs r1,#2\n"
 "ldr.w r0,[pc,#0x160]\nmovs r3,r5\nuxtb r3,r3\nlsls r3,r3,#4\nadd r0,r3\n"
 "ldr r0,[r0,#4]\nbl open_cfw_bootloader_hw_config_transaction_42c988\nmovs r4,r0\n"
 "cmp r4,#0\nbne retry_delay\n"
 "retry_done: cmp r4,#0\nbeq success\nmovs r0,#4\nb finish\n"
 "success: movs r0,#0\nfinish: pop {r1,r4,r5,r6,r7,pc}\n");}
#else
typedef struct {
    open_cfw_hw_retry_u32 callback_registrations;
    open_cfw_hw_retry_u32 attempts;
    open_cfw_hw_retry_u32 delay_calls;
    open_cfw_hw_retry_u32 last_delay_us;
} open_cfw_hw_retry_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_retry_u32 open_cfw_bootloader_hw_config_retry_43048e_portable(
    open_cfw_hw_retry_model *state, open_cfw_hw_retry_u32 channel,
    const open_cfw_hw_retry_u32 *statuses, open_cfw_hw_retry_u32 status_count)
{
    open_cfw_hw_retry_u32 attempt,status=1U;
    if(state==0U)return 4U;
    if((open_cfw_hw_retry_u8)channel==4U)state->callback_registrations+=2U;
    for(attempt=0U;attempt<1000U;attempt++){
        status=attempt<status_count?statuses[attempt]:1U;
        state->attempts++;
        if(status==0U)return 0U;
        if(attempt+1U<1000U){state->delay_calls++;state->last_delay_us=10U;}
    }
    return 4U;
}
#endif
