/* SPDX-License-Identifier: MIT */
/* Clean-room state-one register tuning and restoration service. */
typedef __UINT8_TYPE__ open_cfw_state_one_u8;
typedef __UINT32_TYPE__ open_cfw_state_one_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_delay_us_41d1c0(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_state_one_u32 open_cfw_bootloader_state_event_one_value_42d104(
    open_cfw_state_one_u32 profile)
{
    __asm volatile(
        "push.w {r4,r5,r6,r7,r8,r9,r10,lr}\nmovs r4,r0\n"
        "ldr.w r0,[pc,#0x698]\nldr r0,[r0]\nubfx r0,r0,#4,#2\ncmp r0,#3\n"
        "beq active_path\nldr.w r0,[pc,#0x6c4]\nldr r1,[r0]\n"
        "ubfx r1,r1,#0xa,#4\nldr.w r2,[pc,#0x6c0]\nstr r1,[r2]\n"
        "movs r1,#2\nldr r2,[r0]\nbfi r2,r1,#0xa,#4\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x6b4]\nldr r1,[r0]\nands r1,r1,#0x3f\n"
        "ldr.w r2,[pc,#0x6ac]\nstr r1,[r2]\nldr r1,[r0]\n"
        "ands r1,r1,#0x3f\nadds r1,r1,#5\ncmp r1,#0x40\n"
        "blo.w nonactive_add\nmovs r1,#0x3f\nb nonactive_store\n"
        "active_path:\nldr.w r10,[pc,#0x654]\nldrb.w r0,[r10]\ncmp r0,#0\n"
        "beq saved_field_done\nldr.w r0,[pc,#0x67c]\nldr r1,[r0]\n"
        "ubfx r1,r1,#0xa,#4\nldr.w r2,[pc,#0x684]\nstr r1,[r2]\n"
        "movs r1,#1\nldr r2,[r0]\nbfi r2,r1,#0xa,#4\nstr r2,[r0]\n"
        "saved_field_done:\nldr.w r5,[pc,#0x664]\nldr r0,[r5]\n"
        "lsls r0,r0,#0x16\nlsrs r0,r0,#0x16\nadds r0,#0xc\n"
        "cmp.w r0,#0x400\nblo delta_twelve\nmovw r6,#0x3ff\n"
        "ldr r0,[r5]\nlsls r0,r0,#0x16\nlsrs r0,r0,#0x16\n"
        "subs r6,r6,r0\nb delta_ready\ndelta_twelve:\nmovs r6,#0xc\n"
        "delta_ready:\nldr r0,[r5]\nlsrs r1,r0,#0xa\nlsls r1,r1,#0xa\n"
        "adds r0,r6,r0\nlsls r0,r0,#0x16\nlsrs r0,r0,#0x16\n"
        "orrs r0,r1\nstr r0,[r5]\nldr.w r7,[pc,#0x638]\nmovs.w r8,#5\n"
        "ldr r0,[r7]\nbfi r0,r8,#0,#6\nstr r0,[r7]\nmovs r0,#5\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\nldrb.w r0,[r10]\ncmp r0,#0\n"
        "beq first_adjust_done\nldr.w r0,[pc,#0x5e8]\nldr r1,[r0]\n"
        "ands r1,r1,#0x7f\nadds r1,#0xf\ncmp r1,#0x80\nblo first_add\n"
        "movs r1,#0x7f\nb first_store\nfirst_add:\nldr r1,[r0]\n"
        "ands r1,r1,#0x7f\nadds r1,#0xf\nfirst_store:\nldr r2,[r0]\n"
        "bfi r2,r1,#0,#7\nstr r2,[r0]\nfirst_adjust_done:\n"
        "ldr.w r9,[pc,#0x604]\nldr.w r0,[r9]\norrs r0,r0,#0x20000000\n"
        "str.w r0,[r9]\nldr.w r0,[r9]\norrs r0,r0,#0x10000000\n"
        "str.w r0,[r9]\nldr.w r0,[r9]\norrs r0,r0,#0x80000000\n"
        "str.w r0,[r9]\nldr.w r0,[r9]\norrs r0,r0,#0x40000000\n"
        "str.w r0,[r9]\nmovs r0,#0xa\nbl open_cfw_bootloader_delay_us_41d1c0\n"
        "ldrb.w r0,[r10]\ncmp r0,#0\nbeq second_adjust_done\n"
        "ldr.w r0,[pc,#0x5c4]\nldr r1,[r0]\nands r1,r1,#0x7f\n"
        "adds r1,#9\ncmp r1,#0x80\nblo second_add\nmovs r1,#0x7f\n"
        "b second_store\nsecond_add:\nldr r1,[r0]\nands r1,r1,#0x7f\n"
        "adds r1,#9\nsecond_store:\nldr r2,[r0]\nbfi r2,r1,#0,#7\n"
        "str r2,[r0]\nldr.w r0,[pc,#0x5a4]\nldr r1,[r0]\n"
        "orrs r1,r1,#0x100\nstr r1,[r0]\nsecond_adjust_done:\n"
        "ldrb.w r0,[r10]\ncmp r0,#0\nbeq default_tuning\n"
        "ldr.w r0,[pc,#0x594]\nmovs r1,#0xa\nldr r2,[r0]\n"
        "bfi r2,r1,#0x19,#5\nstr r2,[r0]\nldr r2,[r0]\n"
        "bfi r2,r1,#0xb,#5\nstr r2,[r0]\nldr.w r0,[pc,#0x584]\n"
        "movs r1,#8\nldr r2,[r0]\nbfi r2,r1,#0x19,#5\nstr r2,[r0]\n"
        "ldr r2,[r0]\nbfi r2,r1,#0xb,#5\nstr r2,[r0]\nuxtb r4,r4\n"
        "cmp r4,#1\nbne adjusted_profile_other\nldr.w r0,[pc,#0x56c]\n"
        "movs r1,#0x10\nldr r2,[r0]\nbfi r2,r1,#8,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x560]\nmovs r1,#0x14\nldr r2,[r0]\n"
        "bfi r2,r1,#0x11,#5\nstr r2,[r0]\nb tuning_done\n"
        "adjusted_profile_other:\nldr.w r0,[pc,#0x54c]\nmovs r1,#0x14\n"
        "ldr r2,[r0]\nbfi r2,r1,#8,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x544]\nmovs r1,#0x16\nldr r2,[r0]\n"
        "bfi r2,r1,#0x11,#5\nstr r2,[r0]\nb tuning_done\n"
        "default_tuning:\nldr.w r0,[pc,#0x528]\nmovs r1,#6\nldr r2,[r0]\n"
        "bfi r2,r1,#0x19,#5\nstr r2,[r0]\nldr r2,[r0]\n"
        "bfi r2,r1,#0xb,#5\nstr r2,[r0]\nldr.w r0,[pc,#0x514]\n"
        "ldr r1,[r0]\nbfi r1,r8,#0x19,#5\nstr r1,[r0]\nldr r1,[r0]\n"
        "bfi r1,r8,#0xb,#5\nstr r1,[r0]\nuxtb r4,r4\ncmp r4,#1\n"
        "bne default_profile_other\nldr.w r0,[pc,#0x500]\nmovs r1,#9\n"
        "ldr r2,[r0]\nbfi r2,r1,#8,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x4f4]\nmovs r1,#0xd\nldr r2,[r0]\n"
        "bfi r2,r1,#0x11,#5\nstr r2,[r0]\nb tuning_done\n"
        "default_profile_other:\nldr.w r0,[pc,#0x4e0]\nmovs r1,#0xd\n"
        "ldr r2,[r0]\nbfi r2,r1,#8,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x4d8]\nmovs r1,#0x13\nldr r2,[r0]\n"
        "bfi r2,r1,#0x11,#5\nstr r2,[r0]\ntuning_done:\n"
        "ldr.w r0,[r9]\nbics r0,r0,#0x20000000\nstr.w r0,[r9]\n"
        "ldr.w r0,[r9]\nbics r0,r0,#0x10000000\nstr.w r0,[r9]\n"
        "ldr.w r0,[r9]\nbic r0,r0,#0x80000000\nstr.w r0,[r9]\n"
        "ldr.w r0,[r9]\nbics r0,r0,#0x40000000\nstr.w r0,[r9]\n"
        "ldr r0,[r5]\nlsrs r1,r0,#0xa\nlsls r1,r1,#0xa\nsubs r6,r0,r6\n"
        "lsls r6,r6,#0x16\nlsrs r6,r6,#0x16\norrs r6,r1\nstr r6,[r5]\n"
        "ldr.w r0,[pc,#0x48c]\nldrb r0,[r0]\ncmp r0,#0\nbne clear_low6\n"
        "movs r0,#1\nldr r1,[r7]\nbfi r1,r0,#0,#6\nstr r1,[r7]\n"
        "b finish\nclear_low6:\nldr r0,[r7]\nlsrs r0,r0,#6\nlsls r0,r0,#6\n"
        "str r0,[r7]\nb finish\nnonactive_add:\nldr r1,[r0]\n"
        "ands r1,r1,#0x3f\nadds r1,r1,#5\nnonactive_store:\nldr r2,[r0]\n"
        "bfi r2,r1,#0,#6\nstr r2,[r0]\nmovs r0,#0xf\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\nfinish:\nmovs r0,#0\n"
        "pop.w {r4,r5,r6,r7,r8,r9,r10,pc}\n");
}
#else
typedef struct {
    open_cfw_state_one_u32 mode_register, control80, control88, power380;
    open_cfw_state_one_u32 tune344, tune34c, tune358, tune354;
    open_cfw_state_one_u32 adjust4c, adjust44, control1b0;
    open_cfw_state_one_u32 saved_nonactive_field4, saved_nonactive_low6;
    open_cfw_state_one_u32 saved_active_field4;
    open_cfw_state_one_u8 adjust_enabled, low6_clear;
    open_cfw_state_one_u32 delay_calls, delay_total;
} open_cfw_state_one_model;
static open_cfw_state_one_u32 open_cfw_state_one_insert(open_cfw_state_one_u32 d,
    open_cfw_state_one_u32 s,open_cfw_state_one_u32 n,open_cfw_state_one_u32 w)
{open_cfw_state_one_u32 m=((1U<<w)-1U)<<n;return(d&~m)|((s<<n)&m);}
static open_cfw_state_one_u32 open_cfw_state_one_sat_add(open_cfw_state_one_u32 v,
    open_cfw_state_one_u32 add,open_cfw_state_one_u32 maximum)
{return v+add>maximum?maximum:v+add;}
__attribute__((used,noinline,visibility("default")))
open_cfw_state_one_u32 open_cfw_bootloader_state_event_one_value_42d104_portable(
    open_cfw_state_one_model *m,open_cfw_state_one_u32 profile)
{
    open_cfw_state_one_u32 low,delta,a,b,c,d;
    if(m==0U)return ~0U;
    if(((m->mode_register>>4U)&3U)!=3U){
        m->saved_nonactive_field4=(m->control80>>10U)&15U;
        m->control80=open_cfw_state_one_insert(m->control80,2U,10U,4U);
        m->saved_nonactive_low6=m->control88&63U;
        m->control88=open_cfw_state_one_insert(m->control88,
            open_cfw_state_one_sat_add(m->control88&63U,5U,63U),0U,6U);
        m->delay_calls++;m->delay_total+=15U;return 0U;
    }
    if(m->adjust_enabled!=0U){m->saved_active_field4=(m->control80>>10U)&15U;
        m->control80=open_cfw_state_one_insert(m->control80,1U,10U,4U);}
    low=m->control80&0x3FFU;delta=low+12U>=0x400U?0x3FFU-low:12U;
    m->control80=(m->control80&~0x3FFU)|((low+delta)&0x3FFU);
    m->control88=open_cfw_state_one_insert(m->control88,5U,0U,6U);
    m->delay_calls++;m->delay_total+=5U;
    if(m->adjust_enabled!=0U)m->adjust4c=open_cfw_state_one_insert(m->adjust4c,
        open_cfw_state_one_sat_add(m->adjust4c&127U,15U,127U),0U,7U);
    m->power380|=0xF0000000U;m->delay_calls++;m->delay_total+=10U;
    if(m->adjust_enabled!=0U){m->adjust44=open_cfw_state_one_insert(m->adjust44,
        open_cfw_state_one_sat_add(m->adjust44&127U,9U,127U),0U,7U);
        m->control1b0|=0x100U;a=10U;b=8U;c=profile==1U?16U:20U;
        d=profile==1U?20U:22U;
    }else{a=6U;b=5U;c=profile==1U?9U:13U;d=profile==1U?13U:19U;}
    m->tune344=open_cfw_state_one_insert(open_cfw_state_one_insert(m->tune344,a,25U,5U),a,11U,5U);
    m->tune34c=open_cfw_state_one_insert(open_cfw_state_one_insert(m->tune34c,b,25U,5U),b,11U,5U);
    m->tune358=open_cfw_state_one_insert(m->tune358,c,8U,5U);
    m->tune354=open_cfw_state_one_insert(m->tune354,d,17U,5U);
    m->power380&=~0xF0000000U;low=m->control80&0x3FFU;
    m->control80=(m->control80&~0x3FFU)|((low-delta)&0x3FFU);
    m->control88=open_cfw_state_one_insert(m->control88,m->low6_clear!=0U?0U:1U,0U,6U);
    return 0U;
}
#endif
