/* SPDX-License-Identifier: MIT */
/* Clean-room hardware configuration save/restore and resource transaction. */
typedef __UINT8_TYPE__ open_cfw_hw_config_u8;
typedef __UINT32_TYPE__ open_cfw_hw_config_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_pwrctrl_periph_enable_41bf84(void);
extern void open_cfw_bootloader_cmdq_adapter_enable_42c420(void);
extern void open_cfw_bootloader_retained_status_check_41d246(void);
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);
extern void open_cfw_bootloader_cmdq_adapter_disable_42c44e(void);
extern void open_cfw_bootloader_pwrctrl_periph_disable_41c17a(void);
extern void open_cfw_bootloader_mode_disable_route_422364(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_config_transaction_42c988(void)
{__asm volatile(
 "push {r3,r4,r5,lr}\nmovs r5,r2\nmovs r4,r0\nmovs r2,#0\ncmp r0,#0\nbeq invalid\n"
 "ldr r0,[r0]\nbic r0,r0,#0xfe000000\nldr.w r2,[pc,#0x414]\ncmp r0,r2\nbeq valid\n"
 "invalid: movs r0,#2\nb return_now\n"
 "valid: uxtb r1,r1\ncmp r1,#0\nbeq restore_mode\ncmp r1,#2\nbeq.w save_mode\n"
 "blo.w save_mode\nb bad_mode\n"
 "restore_mode: movs r0,r5\nuxtb r0,r0\ncmp r0,#0\nbeq resource_on\n"
 "ldrb.w r0,[r4,#0x868]\ncmp r0,#0\nbne resource_on\nmovs r0,#7\nb return_now\n"
 "resource_on: ldr r0,[r4,#4]\nadds r0,r0,#3\nuxtb r0,r0\n"
 "bl open_cfw_bootloader_pwrctrl_periph_enable_41bf84\nuxtb r5,r5\ncmp r5,#0\nbeq route_on\n"
 "ldr.w r5,[pc,#0x3e8]\nldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\n"
 "ldr.w r1,[r4,#0x86c]\nstr.w r1,[r0,#0x104]\nldr r0,[r4,#4]\n"
 "adds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x874]\nstr.w r1,[r0,#0x118]\n"
 "ldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x880]\n"
 "str.w r1,[r0,#0x22c]\nldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\n"
 "ldr.w r1,[r4,#0x884]\nstr.w r1,[r0,#0x234]\nldr r0,[r4,#4]\n"
 "adds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x888]\nstr.w r1,[r0,#0x23c]\n"
 "ldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x88c]\n"
 "str.w r1,[r0,#0x240]\nldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\n"
 "ldr.w r1,[r4,#0x890]\nstr.w r1,[r0,#0x244]\nldr r0,[r4,#4]\n"
 "adds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x894]\nstr.w r1,[r0,#0x280]\n"
 "ldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x898]\n"
 "str.w r1,[r0,#0x2c0]\nldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\n"
 "ldr.w r1,[r4,#0x89c]\nstr.w r1,[r0,#0x200]\nldr r0,[r4,#4]\n"
 "adds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x870]\nstr.w r1,[r0,#0x210]\n"
 "ldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x87c]\n"
 "lsrs r1,r1,#1\nlsls r1,r1,#1\nstr.w r1,[r0,#0x228]\n"
 "ldr r0,[r4,#4]\nadds.w r0,r5,r0,lsl #12\nldr.w r1,[r4,#0x878]\n"
 "str.w r1,[r0,#0x11c]\nldrb.w r0,[r4,#0x87c]\nlsls r0,r0,#31\n"
 "bpl restored_queue\nmovs r0,r4\nbl open_cfw_bootloader_cmdq_adapter_enable_42c420\n"
 "restored_queue: ldr r0,[r4]\nubfx r0,r0,#25,#1\ncmp r0,#0\nbeq clear_saved\n"
 "movs r0,#1\nstr r0,[sp]\nmovs r3,#4\nmovs r2,#6\nldr r0,[r4,#4]\n"
 "adds.w r5,r5,r0,lsl #12\nadds.w r1,r5,#0x248\nmov.w r0,#0x3e8\n"
 "bl open_cfw_bootloader_retained_status_check_41d246\n"
 "clear_saved: movs r0,#0\nstrb.w r0,[r4,#0x868]\n"
 "route_on: ldr r1,[r4,#4]\nadds r1,r1,#3\nuxtb r1,r1\nmovs r0,#4\n"
 "bl open_cfw_bootloader_mode_enable_route_4222f0\ncmp r0,#0\nbne return_now\n"
 "route_success: movs r0,#0\nreturn_now: pop {r1,r4,r5,pc}\n"
 "save_mode: ldr r0,[r4]\nubfx r0,r0,#25,#1\ncmp r0,#0\nbeq capture_check\n"
 "ldr r0,[r4,#4]\nldr.w r1,[pc,#0x2d4]\nadds.w r1,r1,r0,lsl #12\n"
 "ldr.w r0,[r1,#0x248]\nands r0,r0,#6\ncmp r0,#4\nbne active_busy\n"
 "ldr r0,[r4,#0x24]\ncmp r0,#0\nbeq capture_check\n"
 "active_busy: movs r0,#3\nb return_now\n"
 "capture_check: uxtb r5,r5\ncmp r5,#0\nbeq controls_off\n"
 "ldr.w r0,[pc,#0x2b0]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "ldr.w r1,[r1,#0x104]\nstr.w r1,[r4,#0x86c]\nldr r1,[r4,#4]\n"
 "adds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x118]\nstr.w r1,[r4,#0x874]\n"
 "ldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x11c]\n"
 "str.w r1,[r4,#0x878]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "ldr.w r1,[r1,#0x228]\nstr.w r1,[r4,#0x87c]\nldr r1,[r4,#4]\n"
 "adds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x22c]\nstr.w r1,[r4,#0x880]\n"
 "ldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x234]\n"
 "str.w r1,[r4,#0x884]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "ldr.w r1,[r1,#0x23c]\nstr.w r1,[r4,#0x888]\nldr r1,[r4,#4]\n"
 "adds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x240]\nstr.w r1,[r4,#0x88c]\n"
 "ldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x244]\n"
 "str.w r1,[r4,#0x890]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "ldr.w r1,[r1,#0x280]\nstr.w r1,[r4,#0x894]\nldr r1,[r4,#4]\n"
 "adds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x2c0]\nstr.w r1,[r4,#0x898]\n"
 "ldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\nldr.w r1,[r1,#0x200]\n"
 "str.w r1,[r4,#0x89c]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "ldr.w r1,[r1,#0x210]\nstr.w r1,[r4,#0x870]\nldr r1,[r4,#4]\n"
 "adds.w r0,r0,r1,lsl #12\nldr.w r0,[r0,#0x228]\nlsls r0,r0,#31\n"
 "bpl mark_saved\nmovs r0,r4\nbl open_cfw_bootloader_cmdq_adapter_disable_42c44e\n"
 "mark_saved: movs r0,#1\nstrb.w r0,[r4,#0x868]\n"
 "controls_off: ldr.w r0,[pc,#0x1dc]\nldr r1,[r4,#4]\nadds.w r1,r0,r1,lsl #12\n"
 "adds.w r1,r1,#0x11c\nldr r2,[r1]\nlsrs r2,r2,#1\nlsls r2,r2,#1\nstr r2,[r1]\n"
 "ldr r1,[r4,#4]\nadds.w r0,r0,r1,lsl #12\nadds.w r0,r0,#0x11c\n"
 "ldr r1,[r0]\nbics r1,r1,#0x10\nstr r1,[r0]\n"
 "ldr r0,[r4,#4]\nadds r0,r0,#3\nuxtb r0,r0\n"
 "bl open_cfw_bootloader_pwrctrl_periph_disable_41c17a\n"
 "ldr r1,[r4,#4]\nadds r1,r1,#3\nuxtb r1,r1\nmovs r0,#4\n"
 "bl open_cfw_bootloader_mode_disable_route_422364\ncmp r0,#0\nbne.w return_now\n"
 "b route_success\n"
 "bad_mode: movs r0,#6\nb return_now\n");}
#else
typedef struct {
    open_cfw_hw_config_u32 header;
    open_cfw_hw_config_u32 pending;
    open_cfw_hw_config_u32 status_248;
    open_cfw_hw_config_u32 registers[13];
    open_cfw_hw_config_u32 saved[13];
    open_cfw_hw_config_u8 saved_valid;
} open_cfw_hw_config_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_config_u32 open_cfw_bootloader_hw_config_transaction_42c988_portable(
    open_cfw_hw_config_model *state,
    open_cfw_hw_config_u32 mode,
    open_cfw_hw_config_u32 transfer,
    open_cfw_hw_config_u32 route_status)
{
    open_cfw_hw_config_u32 index;
    if(state==0 || (state->header&0x01FFFFFFU)!=0x01123456U)return 2U;
    mode&=0xFFU;
    if(mode>2U)return 6U;
    if(mode==0U){
        if(transfer!=0U && state->saved_valid==0U)return 7U;
        if(transfer!=0U){
            for(index=0U;index<13U;index++)state->registers[index]=state->saved[index];
            state->registers[3]&=~1U;
            state->saved_valid=0U;
        }
        return route_status;
    }
    if((state->header&0x02000000U)!=0U &&
       (((state->status_248&6U)!=4U)||state->pending!=0U))return 3U;
    if(transfer!=0U){
        for(index=0U;index<13U;index++)state->saved[index]=state->registers[index];
        state->saved_valid=1U;
    }
    state->registers[2]&=~0x11U;
    return route_status;
}
#endif
