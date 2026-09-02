/* SPDX-License-Identifier: MIT */
/* Clean-room validated seven-field hardware profile encoder and publisher. */
typedef __UINT8_TYPE__ open_cfw_hw_profile_u8;
typedef __UINT32_TYPE__ open_cfw_hw_profile_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_profile_apply_42ea68(void)
{__asm volatile(
 "push {r3,r4,r5,lr}\nmovs r4,r1\nmovs r1,r0\nldr r1,[r1,#4]\ncmp r0,#0\n"
 "beq invalid_handle\nldr r0,[r0]\nbic r0,r0,#0xfe000000\nldr.w r1,[pc,#0x700]\n"
 "cmp r0,r1\nbeq handle_ok\ninvalid_handle: movs r0,#2\nb finish\n"
 "handle_ok: movs r5,#0\nldrb r0,[r4]\ncmp r0,#2\nbeq profile_ok\nmovs r0,#6\nb finish\n"
 "profile_ok: movs r1,#0xf\nmovs r0,#4\nbl open_cfw_bootloader_mode_enable_route_4222f0\n"
 "cmp r0,#0\nbne finish\nldrb r0,[r4]\nlsls r0,r0,#24\nands r0,r0,#0x7000000\norrs r5,r0\n"
 "ldrb r0,[r4,#1]\nlsls r0,r0,#20\nands r0,r0,#0x100000\norrs r5,r0\n"
 "ldrb r0,[r4,#2]\nlsls r0,r0,#19\nands r0,r0,#0x80000\norrs r5,r0\n"
 "ldrb r0,[r4,#3]\nlsls r0,r0,#16\nands r0,r0,#0x70000\norrs r5,r0\n"
 "orrs r5,r5,#0x1000\nldrb r0,[r4,#4]\nlsls r0,r0,#4\nands r0,r0,#0x10\norrs r5,r0\n"
 "ldrb r0,[r4,#5]\nlsls r0,r0,#3\nands r0,r0,#8\norrs r5,r0\n"
 "ldrb r0,[r4,#6]\nlsls r0,r0,#2\nands r0,r0,#4\norrs r5,r0\n"
 "lsrs r5,r5,#1\nlsls r5,r5,#1\nldr.w r0,[pc,#0x690]\nstr r5,[r0]\n"
 "movs r0,#0\nfinish: pop {r1,r4,r5,pc}\n");}
#else
typedef struct {open_cfw_hw_profile_u32 header;open_cfw_hw_profile_u32 published;} open_cfw_hw_profile_model;
__attribute__((used,noinline,visibility("default")))
open_cfw_hw_profile_u32 open_cfw_bootloader_hw_profile_apply_42ea68_portable(
    open_cfw_hw_profile_model *state,const open_cfw_hw_profile_u8 profile[7],
    open_cfw_hw_profile_u32 route_status)
{
    open_cfw_hw_profile_u32 value;
    if(state==0U || (state->header&0x01FFFFFFU)!=0x01AFAFAFU)return 2U;
    if(profile==0U || profile[0]!=2U)return 6U;
    if(route_status!=0U)return route_status;
    value=((open_cfw_hw_profile_u32)(profile[0]&7U)<<24U)|
        ((open_cfw_hw_profile_u32)(profile[1]&1U)<<20U)|
        ((open_cfw_hw_profile_u32)(profile[2]&1U)<<19U)|
        ((open_cfw_hw_profile_u32)(profile[3]&7U)<<16U)|0x1000U|
        ((open_cfw_hw_profile_u32)(profile[4]&1U)<<4U)|
        ((open_cfw_hw_profile_u32)(profile[5]&1U)<<3U)|
        ((open_cfw_hw_profile_u32)(profile[6]&1U)<<2U);
    state->published=value&~1U;return 0U;
}
#endif
