/* SPDX-License-Identifier: MIT */
/* Clean-room hardware instance validation and mode-specific configuration. */
typedef __UINT8_TYPE__ open_cfw_hw_instance_u8;
typedef __UINT32_TYPE__ open_cfw_hw_instance_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_clock_encode_42c26a(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_instance_configure_42cc34(void)
{__asm volatile(
 "push.w {r4,r5,r6,r7,r8,lr}\nmovs r5,r0\nmovs.w r8,#0\ncmp r0,#0\nbeq invalid_handle\n"
 "ldr r2,[r0]\nbic r2,r2,#0xfe000000\nldr r3,[pc,#0x164]\ncmp r2,r3\nbeq handle_ok\n"
 "invalid_handle: movs r0,#2\nb finish\n"
 "handle_ok: cmp r0,#0\nbeq invalid_args\nmovs r4,r1\ncmp r4,#0\nbeq invalid_args\n"
 "ldr r0,[r5,#4]\ncmp r0,#8\nblo args_ok\n"
 "invalid_args: movs r0,#6\nb finish\n"
 "args_ok: ldr r0,[r5]\nubfx r0,r0,#25,#1\ncmp r0,#0\nbeq inactive\n"
 "movs r0,#7\nb finish\n"
 "inactive: ldr r6,[r5,#4]\nldrb r0,[r4]\nstrb r0,[r5,#8]\nldr.w r7,[pc,#0x144]\n"
 "movw r0,#0x1010\nadds.w r1,r7,r6,lsl #12\nstr.w r0,[r1,#0x104]\n"
 "ldrb r0,[r4]\ncmp r0,#0\nbne mode_one\n"
 "ldrb r0,[r4,#8]\ncmp r0,#4\nblt flags_ok\nmovs r0,#6\nb finish\n"
 "flags_ok: ldr r0,[r4,#4]\nldr.w r1,[pc,#0x12c]\ncmp r0,r1\nblo rate_ok\n"
 "movs r0,#6\nb finish\n"
 "rate_ok: ldrb r0,[r4,#8]\nubfx r1,r0,#1,#1\nldr r0,[r4,#4]\n"
 "bl open_cfw_bootloader_hw_clock_encode_42c26a\n"
 "ldrb r1,[r4,#8]\nands r1,r1,#3\nadds.w r2,r7,r6,lsl #12\nstr.w r1,[r2,#0x280]\n"
 "set_control: orrs r0,r0,#1\nadds.w r7,r7,r6,lsl #12\nstr.w r0,[r7,#0x118]\n"
 "common_rate: ldr.w r0,[pc,#0x100]\nldr r1,[r4,#4]\nudiv r0,r0,r1\nstr.w r0,[r5,#0x864]\n"
 "mov.w r0,#0x3e8\nstr.w r0,[r5,#0x860]\nldr r0,[r4,#0xc]\nstr r0,[r5,#0xc]\n"
 "ldr r0,[r4,#0x10]\nstr r0,[r5,#0x10]\nldr r0,[r5,#0xc]\ncmp r0,#0\nbeq clear_slots\n"
 "ldr r0,[r5,#0xc]\nldr r1,[r5,#0x10]\nadds.w r0,r0,r1,lsl #2\n"
 "ldr.w r1,[pc,#0xd8]\ncmp r0,r1\nbhs unsafe_buffer\nmovs r0,#1\nb buffer_flag\n"
 "mode_one: ldrb r0,[r4]\ncmp r0,#1\nbne unsupported_mode\n"
 "ldr r0,[r4,#4]\nldr.w r1,[pc,#0xc8]\ncmp r0,r1\nbeq rate_100k\n"
 "ldr.w r1,[pc,#0xc4]\ncmp r0,r1\nbeq rate_400k\n"
 "ldr.w r1,[pc,#0xb0]\ncmp r0,r1\nbeq rate_1m\nb bad_rate\n"
 "rate_100k: ldr.w r0,[pc,#0xb4]\nldr.w r1,[pc,#0xb4]\nadds.w r2,r7,r6,lsl #12\n"
 "str.w r1,[r2,#0x2c0]\nb set_control\n"
 "rate_400k: ldr.w r0,[pc,#0xac]\nldr.w r1,[pc,#0xac]\nadds.w r2,r7,r6,lsl #12\n"
 "str.w r1,[r2,#0x2c0]\nb set_control\n"
 "rate_1m: ldr.w r0,[pc,#0xa0]\nldr.w r1,[pc,#0xa0]\nadds.w r2,r7,r6,lsl #12\n"
 "str.w r1,[r2,#0x2c0]\nb set_control\n"
 "bad_rate: movs r0,#6\nb finish\n"
 "unsupported_mode: movs r0,#5\nb finish\n"
 "unsafe_buffer: movs r0,#0\n"
 "buffer_flag: strb.w r0,[r5,#0x8a4]\nldr r0,[r5,#0x10]\nsubs r0,#8\nlsls r0,r0,#2\n"
 "movs r1,#0x60\nudiv r0,r0,r1\nstr.w r0,[r5,#0x858]\nldr.w r0,[r5,#0x858]\n"
 "movw r1,#0x101\ncmp r0,r1\nblo clear_slots\nmov.w r0,#0x100\nstr.w r0,[r5,#0x858]\n"
 "clear_slots: movs r0,#0\nb clear_test\n"
 "clear_loop: movs r1,#0\nmovs r2,r0\nuxtb r2,r2\nadd r2,r5\nstrb.w r1,[r2,#0x8a0]\n"
 "adds r0,r0,#1\nclear_test: movs r1,r0\nuxtb r1,r1\ncmp r1,#4\nblt clear_loop\n"
 "mov r0,r8\nfinish: pop.w {r4,r5,r6,r7,r8,pc}\n");}
#else
typedef struct {
    open_cfw_hw_instance_u32 header;
    open_cfw_hw_instance_u32 instance;
    open_cfw_hw_instance_u8 mode;
    open_cfw_hw_instance_u32 control_118;
    open_cfw_hw_instance_u32 control_280;
    open_cfw_hw_instance_u32 control_2c0;
    open_cfw_hw_instance_u32 rate_divisor;
    open_cfw_hw_instance_u32 timeout;
    open_cfw_hw_instance_u32 buffer;
    open_cfw_hw_instance_u32 count;
    open_cfw_hw_instance_u32 window;
    open_cfw_hw_instance_u8 buffer_safe;
    open_cfw_hw_instance_u8 slots[4];
} open_cfw_hw_instance_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_instance_u32 open_cfw_bootloader_hw_instance_configure_42cc34_portable(
    open_cfw_hw_instance_model *state,
    open_cfw_hw_instance_u32 mode,
    open_cfw_hw_instance_u32 rate,
    open_cfw_hw_instance_u32 flags,
    open_cfw_hw_instance_u32 encoded_clock,
    open_cfw_hw_instance_u32 buffer,
    open_cfw_hw_instance_u32 count)
{
    open_cfw_hw_instance_u32 index;
    if(state==0 || (state->header&0x01FFFFFFU)!=0x01123456U)return 2U;
    if(state->instance>=8U)return 6U;
    if((state->header&0x02000000U)!=0U)return 7U;
    state->mode=(open_cfw_hw_instance_u8)mode;
    if(mode==0U){
        if(flags>=4U || rate>48000000U || rate==0U)return 6U;
        state->control_280=flags&3U;
        state->control_118=encoded_clock|1U;
    }else if(mode==1U){
        if(rate==100000U){state->control_118=0x773B2301U;state->control_2c0=0x0003F070U;}
        else if(rate==400000U){state->control_118=0x1D0E2301U;state->control_2c0=0x0003F270U;}
        else if(rate==1000000U){state->control_118=0x0B052301U;state->control_2c0=0x00023040U;}
        else return 6U;
    }else return 5U;
    state->rate_divisor=1000000U/rate;
    state->timeout=1000U;
    state->buffer=buffer;
    state->count=count;
    if(buffer!=0U){
        state->buffer_safe=(open_cfw_hw_instance_u8)
            (((__UINT64_TYPE__)buffer+(__UINT64_TYPE__)count*4U)<0x20080000U);
        state->window=((count-8U)*4U)/96U;
        if(state->window>=257U)state->window=256U;
    }
    for(index=0U;index<4U;index++)state->slots[index]=0U;
    return 0U;
}
#endif
