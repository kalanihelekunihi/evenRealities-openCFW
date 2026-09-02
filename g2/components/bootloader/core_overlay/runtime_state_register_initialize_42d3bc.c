/* SPDX-License-Identifier: MIT */
/* Clean-room state-transition register initialization and restoration. */
typedef __UINT8_TYPE__ open_cfw_state_init_u8;
typedef __UINT32_TYPE__ open_cfw_state_init_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_delay_us_41d1c0(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_state_init_u32 open_cfw_bootloader_state_register_initialize_42d3bc(void)
{
    __asm volatile(
        "push.w {r4,r5,r6,r7,r8,lr}\nldr.w r0,[pc,#0x3e0]\nldr r0,[r0]\n"
        "ubfx r0,r0,#4,#2\ncmp r0,#3\nbeq active_path\nldr.w r0,[pc,#0x418]\n"
        "ldr.w r1,[pc,#0x418]\nldr r1,[r1]\nldr r2,[r0]\nbfi r2,r1,#0,#6\n"
        "str r2,[r0]\nldr.w r0,[pc,#0x3fc]\nldr.w r1,[pc,#0x3fc]\n"
        "ldr r1,[r1]\nldr r2,[r0]\nbfi r2,r1,#0xa,#4\nstr r2,[r0]\nb finish\n"
        "active_path:\nldr.w r7,[pc,#0x3e8]\nldr r0,[r7]\nlsls r0,r0,#0x16\n"
        "lsrs r0,r0,#0x16\nadds r0,#0xc\ncmp.w r0,#0x400\nblo delta_twelve\n"
        "movw r6,#0x3ff\nldr r0,[r7]\nlsls r0,r0,#0x16\nlsrs r0,r0,#0x16\n"
        "subs r6,r6,r0\nb delta_ready\ndelta_twelve:\nmovs r6,#0xc\ndelta_ready:\n"
        "ldr r0,[r7]\nlsrs r1,r0,#0xa\nlsls r1,r1,#0xa\nadds r0,r6,r0\n"
        "lsls r0,r0,#0x16\nlsrs r0,r0,#0x16\norrs r0,r1\nstr r0,[r7]\n"
        "ldr.w r4,[pc,#0x3c0]\nmovs.w r8,#5\nldr r0,[r4]\nbfi r0,r8,#0,#6\n"
        "str r0,[r4]\nmovs r0,#5\nbl open_cfw_bootloader_delay_us_41d1c0\n"
        "ldr.w r5,[pc,#0x3b4]\nldr r0,[r5]\norrs r0,r0,#0x20000000\nstr r0,[r5]\n"
        "ldr r0,[r5]\norrs r0,r0,#0x10000000\nstr r0,[r5]\nldr r0,[r5]\n"
        "orrs r0,r0,#0x80000000\nstr r0,[r5]\nldr r0,[r5]\norrs r0,r0,#0x40000000\n"
        "str r0,[r5]\nmovs r0,#0xa\nbl open_cfw_bootloader_delay_us_41d1c0\n"
        "ldr.w r0,[pc,#0x398]\nmovs r1,#6\nldr r2,[r0]\nbfi r2,r1,#0x19,#5\n"
        "str r2,[r0]\nldr r2,[r0]\nbfi r2,r1,#0xb,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x384]\nldr r1,[r0]\nbfi r1,r8,#0x19,#5\nstr r1,[r0]\n"
        "ldr r1,[r0]\nbfi r1,r8,#0xb,#5\nstr r1,[r0]\nldr.w r0,[pc,#0x374]\n"
        "movs r1,#7\nldr r2,[r0]\nbfi r2,r1,#8,#5\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x36c]\nmovs r1,#0xa\nldr r2,[r0]\nbfi r2,r1,#0x11,#5\n"
        "str r2,[r0]\nldr.w r0,[pc,#0x2fc]\nldrb r0,[r0]\ncmp r0,#0\nbeq restore_delta\n"
        "ldr.w r0,[pc,#0x2fc]\nldr r1,[r0]\nands r1,r1,#0x7f\ncmp r1,#0x10\n"
        "blt first_zero\nldr r1,[r0]\nands r1,r1,#0x7f\nsubs r1,#0xf\nb first_ready\n"
        "first_zero:\nmovs r1,#0\nfirst_ready:\nldr r2,[r0]\nbfi r2,r1,#0,#7\n"
        "str r2,[r0]\nldr.w r0,[pc,#0x31c]\nldr r1,[r0]\nands r1,r1,#0x7f\n"
        "cmp r1,#0xa\nblt second_zero\nldr r1,[r0]\nands r1,r1,#0x7f\n"
        "subs r1,#9\nb second_ready\nsecond_zero:\nmovs r1,#0\nsecond_ready:\n"
        "ldr r2,[r0]\nbfi r2,r1,#0,#7\nstr r2,[r0]\nldr r0,[pc,#0x2f4]\n"
        "ldr r0,[r0]\nldr r1,[r7]\nbfi r1,r0,#0xa,#4\nstr r1,[r7]\n"
        "ldr r0,[pc,#0x2f4]\nldr r1,[r0]\nbics r1,r1,#0x100\nstr r1,[r0]\n"
        "restore_delta:\nldr r0,[r7]\nlsrs r1,r0,#0xa\nlsls r1,r1,#0xa\n"
        "subs r6,r0,r6\nlsls r6,r6,#0x16\nlsrs r6,r6,#0x16\norrs r6,r1\n"
        "str r6,[r7]\nldr r0,[pc,#0x2ec]\nldrb r0,[r0]\ncmp r0,#0\nbne clear_low6\n"
        "movs r0,#1\nldr r1,[r4]\nbfi r1,r0,#0,#6\nstr r1,[r4]\nb clear_power_bits\n"
        "clear_low6:\nldr r0,[r4]\nlsrs r0,r0,#6\nlsls r0,r0,#6\nstr r0,[r4]\n"
        "clear_power_bits:\nldr r0,[r5]\nbics r0,r0,#0x20000000\nstr r0,[r5]\n"
        "ldr r0,[r5]\nbics r0,r0,#0x10000000\nstr r0,[r5]\nldr r0,[r5]\n"
        "bic r0,r0,#0x80000000\nstr r0,[r5]\nldr r0,[r5]\nbics r0,r0,#0x40000000\n"
        "str r0,[r5]\nfinish:\nmovs r0,#0\npop.w {r4,r5,r6,r7,r8,pc}\n");
}
#else
typedef struct {
    open_cfw_state_init_u32 mode_register;
    open_cfw_state_init_u32 control80;
    open_cfw_state_init_u32 control88;
    open_cfw_state_init_u32 power380;
    open_cfw_state_init_u32 tune344;
    open_cfw_state_init_u32 tune34c;
    open_cfw_state_init_u32 tune358;
    open_cfw_state_init_u32 tune354;
    open_cfw_state_init_u32 adjust4c;
    open_cfw_state_init_u32 adjust44;
    open_cfw_state_init_u32 control1b0;
    open_cfw_state_init_u32 saved_low6;
    open_cfw_state_init_u32 saved_field4;
    open_cfw_state_init_u32 saved_restore4;
    open_cfw_state_init_u8 adjust_enabled;
    open_cfw_state_init_u8 low6_clear;
    open_cfw_state_init_u32 delay_calls;
    open_cfw_state_init_u32 delay_total;
} open_cfw_state_init_model;
static open_cfw_state_init_u32 open_cfw_state_init_insert(open_cfw_state_init_u32 d,open_cfw_state_init_u32 s,open_cfw_state_init_u32 n,open_cfw_state_init_u32 w){open_cfw_state_init_u32 m=((1U<<w)-1U)<<n;return(d&~m)|((s<<n)&m);}
__attribute__((used,noinline,visibility("default")))
open_cfw_state_init_u32 open_cfw_bootloader_state_register_initialize_42d3bc_portable(open_cfw_state_init_model *m)
{
    open_cfw_state_init_u32 low,delta,value;
    if(m==0U)return ~0U;
    if(((m->mode_register>>4U)&3U)!=3U){m->control88=open_cfw_state_init_insert(m->control88,m->saved_low6,0U,6U);m->control80=open_cfw_state_init_insert(m->control80,m->saved_field4,10U,4U);return 0U;}
    low=m->control80&0x3FFU;delta=low+12U>=0x400U?0x3FFU-low:12U;m->control80=(m->control80&~0x3FFU)|((low+delta)&0x3FFU);m->control88=open_cfw_state_init_insert(m->control88,5U,0U,6U);m->delay_calls+=2U;m->delay_total+=15U;m->power380|=0xF0000000U;
    m->tune344=open_cfw_state_init_insert(open_cfw_state_init_insert(m->tune344,6U,25U,5U),6U,11U,5U);m->tune34c=open_cfw_state_init_insert(open_cfw_state_init_insert(m->tune34c,5U,25U,5U),5U,11U,5U);m->tune358=open_cfw_state_init_insert(m->tune358,7U,8U,5U);m->tune354=open_cfw_state_init_insert(m->tune354,10U,17U,5U);
    if(m->adjust_enabled!=0U){value=m->adjust4c&0x7FU;m->adjust4c=open_cfw_state_init_insert(m->adjust4c,value>=16U?value-15U:0U,0U,7U);value=m->adjust44&0x7FU;m->adjust44=open_cfw_state_init_insert(m->adjust44,value>=10U?value-9U:0U,0U,7U);m->control80=open_cfw_state_init_insert(m->control80,m->saved_restore4,10U,4U);m->control1b0&=~0x100U;}
    low=m->control80&0x3FFU;m->control80=(m->control80&~0x3FFU)|((low-delta)&0x3FFU);m->control88=open_cfw_state_init_insert(m->control88,m->low6_clear!=0U?0U:1U,0U,6U);m->power380&=~0xF0000000U;return 0U;
}
#endif
