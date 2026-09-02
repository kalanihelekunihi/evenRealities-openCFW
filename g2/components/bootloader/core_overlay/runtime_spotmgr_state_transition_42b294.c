/* SPDX-License-Identifier: MIT */
/* Clean-room SPOT-manager state transition, trim, and register orchestrator. */
typedef __UINT8_TYPE__ open_cfw_spot_state_u8;
typedef __UINT32_TYPE__ open_cfw_spot_state_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_spotmgr_power_transition_trims_42b06c(void);
extern void open_cfw_bootloader_spotmgr_trim_enable_42adb8(void);
extern void open_cfw_bootloader_spotmgr_transition_start_41cc48(void);
extern void open_cfw_bootloader_spotmgr_transition_wait_41cc92(void);
extern void open_cfw_bootloader_spotmgr_irq_pause_41e22e(void);
extern void open_cfw_bootloader_delay_cycles_41d1c0(void);
extern void open_cfw_bootloader_spotmgr_irq_resume_41e1e8(void);
extern void open_cfw_bootloader_spotmgr_trim_finalize_41ccd6(void);
extern void open_cfw_bootloader_spotmgr_trim_restore_42ae6c(void);
extern void open_cfw_bootloader_spotmgr_profile_trim_42ae24(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_spot_state_u32 open_cfw_bootloader_spotmgr_state_transition_42b294(
    open_cfw_spot_state_u32 from,open_cfw_spot_state_u32 to,
    open_cfw_spot_state_u32 observed,open_cfw_spot_state_u32 guard)
{
    __asm volatile(
        "push.w {r3,r4,r5,r6,r7,r8,r9,r10,r11,lr}\nmovs r4,r0\nmovs r5,r1\n"
        "movs r0,r2\nmovs r1,#0\nldr.w r2,[pc,#0x400]\n"
        "add.w r6,r2,r4,lsl #2\nadds r6,r6,#4\nadd.w r7,r2,r5,lsl #2\n"
        "adds r7,r7,#4\nldr.w r8,[pc,#0x748]\nldr.w r12,[r8]\n"
        "add.w r2,r2,r12,lsl #2\nadds.w r9,r2,#4\nmovs.w r10,#0\n"
        "movs r2,#0\nmovs r2,#0\nmovs r2,#0\nmovs r2,#0\nmovs r2,#0\n"
        "cmp r4,r5\nbne distinct_states\ncmp r0,r3\nbeq.w finish\nmovs r1,r4\n"
        "bl open_cfw_bootloader_spotmgr_power_transition_trims_42b06c\nb finish\n"
        "distinct_states:\nldr.w r11,[pc,#0xab8]\nldr.w r2,[r11,r5,lsl #2]\n"
        "ldr.w r12,[r11,r4,lsl #2]\ncmp r2,r12\nblo ascending\n"
        "ldr.w r2,[pc,#0xaf4]\nldr.w r12,[r2,r5,lsl #2]\n"
        "ldr.w r2,[r2,r4,lsl #2]\ncmp r12,r2\nbhs direction_ready\n"
        "ascending:\nmovs r1,#1\ndirection_ready:\nuxtb r1,r1\ncmp r1,#0\n"
        "beq.w reverse_path\ncmp r0,r3\nbne maybe_pretrim\ncmp r4,#1\n"
        "beq maybe_pretrim\ncmp r4,#5\nbeq maybe_pretrim\ncmp r4,#0x11\n"
        "beq maybe_pretrim\ncmp r4,#8\nbeq maybe_pretrim\ncmp r4,#0xc\n"
        "beq maybe_pretrim\ncmp r4,#0xe\nbeq maybe_pretrim\ncmp r4,#0xf\n"
        "beq maybe_pretrim\ncmp r5,#1\nbeq maybe_pretrim\ncmp r5,#5\n"
        "beq maybe_pretrim\ncmp r5,#0x11\nbeq maybe_pretrim\ncmp r5,#8\n"
        "beq maybe_pretrim\ncmp r5,#0xc\nbeq maybe_pretrim\ncmp r5,#0xe\n"
        "beq maybe_pretrim\ncmp r5,#0xf\nbne ascending_registers\n"
        "maybe_pretrim:\nmovs r1,r4\nbl open_cfw_bootloader_spotmgr_power_transition_trims_42b06c\n"
        "ascending_registers:\nldr.w r3,[pc,#0x364]\nldr r0,[r6]\n"
        "ubfx r0,r0,#0x15,#7\nstr r0,[r3]\nldr.w r2,[pc,#0x668]\n"
        "ldrb r0,[r6]\nands r0,r0,#0x7f\nstr r0,[r2]\nldr r0,[r6]\n"
        "ubfx r0,r0,#0x11,#4\nldr.w r12,[pc,#0x33c]\nldr.w r1,[r12]\n"
        "bfi r1,r0,#0xa,#4\nstr.w r1,[r12]\nldr.w r1,[pc,#0xa70]\n"
        "ldr r0,[r1]\nlsls r0,r0,#0x1f\nbmi add_delta\nldr r0,[r6]\n"
        "ubfx r0,r0,#7,#0xa\nldr.w r6,[r12]\nlsrs r6,r6,#0xa\n"
        "lsls r6,r6,#0xa\norrs r0,r6\nstr.w r0,[r12]\nldr r0,[r7]\n"
        "ubfx r6,r0,#0x15,#7\nldrb r7,[r7]\nands r7,r7,#0x7f\n"
        "b compare_fields\nadd_delta:\nldr r0,[r6]\nubfx r0,r0,#7,#0xa\n"
        "adds r0,r0,#7\ncmp.w r0,#0x400\nblo delta_seven\nmovw r7,#0x3ff\n"
        "ldr r0,[r6]\nubfx r0,r0,#7,#0xa\nsubs r7,r7,r0\n"
        "ldr.w r0,[pc,#0x5f8]\nstr r7,[r0]\nb delta_ready\ndelta_seven:\n"
        "movs r0,#7\nldr.w r7,[pc,#0x5f0]\nstr r0,[r7]\ndelta_ready:\n"
        "ldr r6,[r6]\nldr.w r0,[pc,#0x5e8]\nldr r0,[r0]\n"
        "adds.w r0,r0,r6,lsr #7\nlsls r0,r0,#0x16\nlsrs r0,r0,#0x16\n"
        "ldr.w r6,[r12]\nlsrs r6,r6,#0xa\nlsls r6,r6,#0xa\norrs r0,r6\n"
        "str.w r0,[r12]\nldr.w r0,[r9]\nubfx r6,r0,#0x15,#7\n"
        "ldrb.w r7,[r9]\nands r7,r7,#0x7f\ncompare_fields:\nldr r0,[r3]\n"
        "cmp r6,r0\nbhs high_field_down\nldr.w r12,[r3]\nsubs.w r12,r12,r6\n"
        "lsls.w r12,r12,#1\nb high_delta_ready\nhigh_field_down:\nldr.w r12,[r3]\n"
        "subs.w r12,r6,r12\nrsbs.w r12,r12,#0\nhigh_delta_ready:\n"
        "ldr r0,[r2]\ncmp r7,r0\nbhs low_field_down\nldr.w r14,[r2]\n"
        "subs.w r14,r14,r7\nlsls.w r14,r14,#1\nb low_delta_ready\n"
        "low_field_down:\nldr.w r14,[r2]\nsubs.w r14,r7,r14\n"
        "rsbs.w r14,r14,#0\nlow_delta_ready:\nadds.w r0,r12,r6\ncmp r0,#0x80\n"
        "bhs publish_targets\nadds.w r0,r14,r7\ncmp r0,#0x80\nbhs publish_targets\n"
        "ldr r0,[pc,#0x25c]\nldrb r0,[r0]\ncmp r0,#0\nbeq interpolate\n"
        "publish_targets:\nldr r6,[pc,#0x258]\nldr r7,[r6]\nlsrs r7,r7,#7\n"
        "lsls r7,r7,#7\nldr r0,[r3]\norrs r7,r0\nstr r7,[r6]\n"
        "ldr.w r3,[pc,#0x558]\nldr r6,[r3]\nlsrs r6,r6,#7\n"
        "lsls r6,r6,#7\nldr r0,[r2]\norrs r6,r0\nstr r6,[r3]\n"
        "ldr r0,[pc,#0x234]\nldrb r0,[r0]\ncmp r0,#0\nbeq delay_short\n"
        "mov.w r6,#0x7d0\nb transition_apply\ndelay_short:\nmovs r6,#0xc8\n"
        "b transition_apply\ninterpolate:\nldr r0,[pc,#0x228]\nadds.w r6,r12,r6\n"
        "ldr r2,[r0]\nbfi r2,r6,#0,#7\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x528]\nadds.w r7,r14,r7\nldr r2,[r0]\n"
        "bfi r2,r7,#0,#7\nstr r2,[r0]\nmovs r6,#0x32\n"
        "transition_apply:\nldr r0,[r1]\nlsls r0,r0,#0x1f\nbmi transition_wait\n"
        "movs r0,#1\nbl open_cfw_bootloader_spotmgr_trim_enable_42adb8\n"
        "movs r0,r6\nbl open_cfw_bootloader_spotmgr_transition_start_41cc48\n"
        "str.w r5,[r8]\nb post_transition\ntransition_wait:\nmovs r0,r6\n"
        "bl open_cfw_bootloader_spotmgr_transition_wait_41cc92\npost_transition:\n"
        "cmp r5,#8\nblo wake_check\nsubs r5,#0x10\ncmp r5,#4\nbhs settle\n"
        "wake_check:\nsubs r4,#8\ncmp r4,#8\nbhs settle\n"
        "ldr.w r0,[pc,#0xa78]\nldr r0,[r0]\nlsls r0,r0,#0xe\nbpl wake_publish\n"
        "bl open_cfw_bootloader_spotmgr_irq_pause_41e22e\nmovs.w r10,#1\n"
        "wake_publish:\nldr.w r0,[pc,#0x4e8]\nldr r1,[r0]\norrs r1,r1,#0x10000\n"
        "str r1,[r0]\nmovs r0,#1\nldr.w r1,[pc,#0x4d0]\nstrb r0,[r1]\n"
        "settle:\nmovs r0,#0x14\nbl open_cfw_bootloader_delay_cycles_41d1c0\n"
        "uxtb.w r10,r10\ncmp.w r10,#0\nbeq.w finish\n"
        "bl open_cfw_bootloader_spotmgr_irq_resume_41e1e8\nb finish\n"
        "reverse_path:\nldr.w r7,[pc,#0x8d8]\nldr r1,[r7]\nlsls r1,r1,#0x1f\n"
        "bpl reverse_order_ready\nldr.w r1,[r8]\nldr.w r1,[r11,r1,lsl #2]\n"
        "ldr.w r2,[r11,r4,lsl #2]\ncmp r1,r2\nblo reverse_order_true\n"
        "ldr.w r1,[pc,#0x8b8]\nldr.w r2,[r8]\nldr.w r2,[r1,r2,lsl #2]\n"
        "ldr.w r1,[r1,r4,lsl #2]\ncmp r2,r1\nbhs reverse_order_ready\n"
        "reverse_order_true:\nmovs r1,#1\nb reverse_order_set\nreverse_order_ready:\nmovs r1,#0\n"
        "reverse_order_set:\nuxtb r1,r1\ncmp r1,#0\nbeq reverse_direct\n"
        "ldr r1,[r6]\nubfx r1,r1,#7,#0xa\nadds r1,r1,#7\n"
        "cmp.w r1,#0x400\nblo reverse_delta_seven\nmovw r2,#0x3ff\n"
        "ldr r1,[r6]\nubfx r1,r1,#7,#0xa\nsubs r2,r2,r1\n"
        "ldr.w r1,[pc,#0x454]\nstr r2,[r1]\nb reverse_delta_ready\n"
        "reverse_delta_seven:\nmovs r1,#7\nldr.w r2,[pc,#0x448]\nstr r1,[r2]\n"
        "reverse_delta_ready:\nldr r2,[r6]\nldr.w r1,[pc,#0x440]\nldr r1,[r1]\n"
        "adds.w r1,r1,r2,lsr #7\nlsls r1,r1,#0x16\nlsrs r1,r1,#0x16\n"
        "ldr r2,[pc,#0x120]\nldr.w r12,[r2]\nlsrs.w r12,r12,#0xa\n"
        "lsls.w r12,r12,#0xa\norrs.w r1,r1,r12\nstr r1,[r2]\n"
        "b reverse_fields\nreverse_direct:\nldr r1,[r6]\nubfx r1,r1,#7,#0xa\n"
        "ldr r2,[pc,#0x104]\nldr.w r12,[r2]\nlsrs.w r12,r12,#0xa\n"
        "lsls.w r12,r12,#0xa\norrs.w r1,r1,r12\nstr r1,[r2]\n"
        "reverse_fields:\nldr r1,[r6]\nubfx r1,r1,#0x11,#4\nldr r2,[pc,#0xe8]\n"
        "ldr.w r12,[r2]\nbfi r12,r1,#0xa,#4\nstr.w r12,[r2]\n"
        "ldr r1,[pc,#0xe0]\nldrb r1,[r1]\ncmp r1,#0\nbne reverse_merge\n"
        "ldr r1,[r7]\nlsls r1,r1,#0x1f\nbmi reverse_store\nreverse_merge:\n"
        "ldr r1,[r6]\nubfx r1,r1,#0x15,#7\nldr r2,[pc,#0xd0]\n"
        "ldr.w r12,[r2]\nlsrs.w r12,r12,#7\nlsls.w r12,r12,#7\n"
        "orrs.w r1,r1,r12\nstr r1,[r2]\nldrb r1,[r6]\nands r1,r1,#0x7f\n"
        "ldr.w r2,[pc,#0x3c4]\nldr r6,[r2]\nlsrs r6,r6,#7\n"
        "lsls r6,r6,#7\norrs r1,r6\nstr r1,[r2]\nb reverse_after_fields\n"
        "reverse_store:\nldr r1,[r6]\nubfx r1,r1,#0x15,#7\nldr r2,[pc,#0xa4]\n"
        "str r1,[r2]\nldrb r1,[r6]\nands r1,r1,#0x7f\n"
        "ldr.w r2,[pc,#0x3a8]\nstr r1,[r2]\nreverse_after_fields:\n"
        "cmp r0,r3\nbne reverse_maybe_pretrim\ncmp r4,#1\nbeq reverse_maybe_pretrim\n"
        "cmp r4,#5\nbeq reverse_maybe_pretrim\ncmp r4,#0x11\nbeq reverse_maybe_pretrim\n"
        "cmp r4,#8\nbeq reverse_maybe_pretrim\ncmp r4,#0xc\nbeq reverse_maybe_pretrim\n"
        "cmp r4,#0xe\nbeq reverse_maybe_pretrim\ncmp r4,#0xf\nbeq reverse_maybe_pretrim\n"
        "cmp r5,#1\nbeq reverse_maybe_pretrim\ncmp r5,#5\nbeq reverse_maybe_pretrim\n"
        "cmp r5,#0x11\nbeq reverse_maybe_pretrim\ncmp r5,#8\nbeq reverse_maybe_pretrim\n"
        "cmp r5,#0xc\nbeq reverse_maybe_pretrim\ncmp r5,#0xe\nbeq reverse_maybe_pretrim\n"
        "cmp r5,#0xf\nbne reverse_finalize_check\nreverse_maybe_pretrim:\nmovs r1,r4\n"
        "bl open_cfw_bootloader_spotmgr_power_transition_trims_42b06c\n"
        "reverse_finalize_check:\nldr r0,[r7]\nlsls r0,r0,#0x1f\nbpl finish\n"
        "ldr.w r0,[r8]\nldr.w r0,[r11,r0,lsl #2]\nldr.w r1,[r11,r4,lsl #2]\n"
        "cmp r0,r1\nblo finish\nldr.w r0,[pc,#0x770]\nldr.w r1,[r8]\n"
        "ldr.w r1,[r0,r1,lsl #2]\nldr.w r0,[r0,r4,lsl #2]\ncmp r1,r0\n"
        "blo finish\nbl open_cfw_bootloader_spotmgr_trim_finalize_41ccd6\n"
        "bl open_cfw_bootloader_spotmgr_trim_restore_42ae6c\nmovs r0,#0\n"
        "bl open_cfw_bootloader_spotmgr_profile_trim_42ae24\nfinish:\n"
        "pop.w {r0,r4,r5,r6,r7,r8,r9,r10,r11,pc}\n");
}
#else
typedef struct {
    open_cfw_spot_state_u32 rank_from,rank_to,secondary_from,secondary_to;
    open_cfw_spot_state_u32 current_rank,current_secondary;
    open_cfw_spot_state_u32 from_word,to_word,current_word;
    open_cfw_spot_state_u32 control80,control44,control4c,control37c;
    open_cfw_spot_state_u32 observed,guard_value;
    open_cfw_spot_state_u8 active,feature,force_publish,protected_state;
    open_cfw_spot_state_u32 pretrim_calls,trim_enable_calls,start_calls,wait_calls;
    open_cfw_spot_state_u32 delay_calls,irq_pause_calls,irq_resume_calls;
    open_cfw_spot_state_u32 finalize_calls,restore_calls,profile_clear_calls;
    open_cfw_spot_state_u32 transition_delay,stored_state;
} open_cfw_spot_state_model;
static open_cfw_spot_state_u32 open_cfw_spot_state_field(open_cfw_spot_state_u32 v,
    open_cfw_spot_state_u32 n,open_cfw_spot_state_u32 w)
{return(v>>n)&((1U<<w)-1U);}
static open_cfw_spot_state_u32 open_cfw_spot_state_insert(open_cfw_spot_state_u32 d,
    open_cfw_spot_state_u32 s,open_cfw_spot_state_u32 n,open_cfw_spot_state_u32 w)
{open_cfw_spot_state_u32 m=((1U<<w)-1U)<<n;return(d&~m)|((s<<n)&m);}
static open_cfw_spot_state_u32 open_cfw_spot_state_special(open_cfw_spot_state_u32 v)
{return v==1U||v==5U||v==17U||v==8U||v==12U||v==14U||v==15U;}
__attribute__((used,noinline,visibility("default")))
open_cfw_spot_state_u32 open_cfw_bootloader_spotmgr_state_transition_42b294_portable(
    open_cfw_spot_state_model *m,open_cfw_spot_state_u32 from,
    open_cfw_spot_state_u32 to)
{
    open_cfw_spot_state_u32 forward,ordered,source10,delta,high,low;
    if(m==0U)return ~0U;
    if(from==to){if(m->observed!=m->guard_value)m->pretrim_calls++;return 0U;}
    forward=m->rank_to<m->rank_from||m->secondary_to<m->secondary_from;
    if(forward!=0U){
        if(m->observed!=m->guard_value||open_cfw_spot_state_special(from)||
           open_cfw_spot_state_special(to))m->pretrim_calls++;
        high=open_cfw_spot_state_field(m->from_word,21U,7U);
        low=m->from_word&127U;m->control80=open_cfw_spot_state_insert(m->control80,
            open_cfw_spot_state_field(m->from_word,17U,4U),10U,4U);
        ordered=(m->active==0U);
        source10=open_cfw_spot_state_field(m->from_word,7U,10U);
        if(ordered!=0U)m->control80=open_cfw_spot_state_insert(m->control80,source10,0U,10U);
        else{delta=source10+7U>=1024U?1023U-source10:7U;
            m->control80=open_cfw_spot_state_insert(m->control80,(source10+delta)&1023U,0U,10U);
            high=open_cfw_spot_state_field(m->current_word,21U,7U);low=m->current_word&127U;}
        if(m->force_publish!=0U||high>=128U||low>=128U){m->control44=open_cfw_spot_state_insert(m->control44,high,0U,7U);m->control4c=open_cfw_spot_state_insert(m->control4c,low,0U,7U);m->transition_delay=m->feature?2000U:200U;}
        else{m->control44=open_cfw_spot_state_insert(m->control44,high,0U,7U);m->control4c=open_cfw_spot_state_insert(m->control4c,low,0U,7U);m->transition_delay=50U;}
        if(m->active==0U){m->trim_enable_calls++;m->start_calls++;m->stored_state=to;}else m->wait_calls++;
        m->delay_calls++;if(((from-8U)<8U)&&((to<8U)||((to-16U)<4U))){m->control37c|=0x10000U;if(m->protected_state!=0U){m->irq_pause_calls++;m->irq_resume_calls++;}}
    }else{
        ordered=m->active!=0U&&(m->current_rank<m->rank_from||m->current_secondary<m->secondary_from);
        source10=open_cfw_spot_state_field(m->from_word,7U,10U);
        if(ordered!=0U){delta=source10+7U>=1024U?1023U-source10:7U;source10=(source10+delta)&1023U;}
        m->control80=open_cfw_spot_state_insert(m->control80,source10,0U,10U);
        m->control80=open_cfw_spot_state_insert(m->control80,open_cfw_spot_state_field(m->from_word,17U,4U),10U,4U);
        m->control44=open_cfw_spot_state_insert(m->control44,open_cfw_spot_state_field(m->from_word,21U,7U),0U,7U);
        m->control4c=open_cfw_spot_state_insert(m->control4c,m->from_word&127U,0U,7U);
        if(m->observed!=m->guard_value||open_cfw_spot_state_special(from)||open_cfw_spot_state_special(to))m->pretrim_calls++;
        if(m->active!=0U&&m->current_rank>=m->rank_from&&m->current_secondary>=m->secondary_from){m->finalize_calls++;m->restore_calls++;m->profile_clear_calls++;}
    }
    return 0U;
}
#endif
