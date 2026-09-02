/* SPDX-License-Identifier: MIT */
/* Clean-room retained hardware-event acknowledgement and timed pulse service. */
typedef __UINT32_TYPE__ open_cfw_hw_apply_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_delay_cycles_41d1c0(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_event_apply_42c0b2(void)
{__asm volatile(
 "push {r3,r4,r5,r6,r7,lr}\nldr.w r3,[r0,#0x864]\nmovs r2,#6\nmul r2,r2,r3\n"
 "ldr r4,[r0,#4]\nldr.w r5,[pc,#0x624]\nadds.w r0,r5,r4,lsl #12\n"
 "ldr.w r6,[r0,#0x200]\nmovs r0,#0\nadds.w r3,r5,r4,lsl #12\nstr.w r0,[r3,#0x200]\n"
 "lsls r0,r1,#0x14\nbpl pulse_test\nadds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x218]\n"
 "lsls r0,r0,#0x1e\nbpl alternate_wait\nldr.w r3,[pc,#0x60c]\n"
 "adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x21c]\nb drain_test\n"
 "drain_subtract: subs r0,r0,#4\n"
 "drain_test: cmp r0,#0\nbeq primary_status_wait\n"
 "drain_ready_wait: adds.w r7,r5,r4,lsl #12\nldr.w r7,[r7,#0x100]\nubfx r7,r7,#8,#8\n"
 "cmp r7,#4\nblt drain_test\nadds.w r7,r5,r4,lsl #12\nstr.w r3,[r7,#0x10c]\n"
 "cmp r0,#5\nbhs drain_subtract\n"
 "primary_status_wait: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x248]\n"
 "ands r0,r0,#6\ncmp r0,#4\nbne primary_status_wait\n"
 "pulse_test: tst.w r1,#0x210\nbeq finish_registers\n"
 "adds.w r0,r5,r4,lsl #12\nldr.w r7,[r0,#0x388]\n"
 "pulse_status_wait: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x248]\n"
 "ands r0,r0,#6\ncmp r0,#4\nbne pulse_status_wait\n"
 "adds.w r0,r5,r4,lsl #12\nadds.w r0,r0,#0x11c\nldr r1,[r0]\nbics r1,r1,#0x10\nstr r1,[r0]\n"
 "adds.w r0,r5,r4,lsl #12\nadds.w r0,r0,#0x110\nldr r1,[r0]\nbics r1,r1,#2\nstr r1,[r0]\n"
 "adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x388]\norrs r0,r0,#2\n"
 "adds.w r1,r5,r4,lsl #12\nstr.w r0,[r1,#0x388]\nmovs r0,r2\nbl open_cfw_bootloader_delay_cycles_41d1c0\n"
 "adds.w r0,r5,r4,lsl #12\nstr.w r7,[r0,#0x388]\n"
 "adds.w r0,r5,r4,lsl #12\nadds.w r0,r0,#0x110\nldr r1,[r0]\norrs r1,r1,#2\nstr r1,[r0]\n"
 "adds.w r0,r5,r4,lsl #12\nadds.w r0,r0,#0x11c\nldr r1,[r0]\norrs r1,r1,#0x10\nstr r1,[r0]\n"
 "finish_registers: movs.w r0,#-1\nadds.w r1,r5,r4,lsl #12\nstr.w r0,[r1,#0x208]\n"
 "adds.w r5,r5,r4,lsl #12\nstr.w r6,[r5,#0x200]\npop {r0,r4,r5,r6,r7,pc}\n"
 "alternate_wait: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x248]\nubfx r0,r0,#1,#1\n"
 "cmp r0,#0\nbeq alternate_status_wait\n"
 "alternate_ready_wait: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x100]\nubfx r0,r0,#16,#8\n"
 "cmp r0,#4\nblt alternate_wait\nadds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x108]\nb alternate_ready_wait\n"
 "alternate_status_wait: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x248]\n"
 "ands r0,r0,#6\ncmp r0,#4\nbne alternate_status_wait\n"
 "alternate_field_test: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x100]\nubfx r0,r0,#16,#8\n"
 "cmp r0,#0\nbeq pulse_test\nb alternate_drain_test\n"
 "alternate_drain: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x108]\n"
 "alternate_drain_test: adds.w r0,r5,r4,lsl #12\nldr.w r0,[r0,#0x100]\nubfx r0,r0,#16,#8\n"
 "cmp r0,#4\nblt alternate_field_test\nb alternate_drain\n");}
#else
typedef struct {
    open_cfw_hw_apply_u32 instance;
    open_cfw_hw_apply_u32 delay_unit;
    open_cfw_hw_apply_u32 register_100;
    open_cfw_hw_apply_u32 register_108;
    open_cfw_hw_apply_u32 register_10c;
    open_cfw_hw_apply_u32 register_110;
    open_cfw_hw_apply_u32 register_11c;
    open_cfw_hw_apply_u32 register_200;
    open_cfw_hw_apply_u32 register_208;
    open_cfw_hw_apply_u32 register_218;
    open_cfw_hw_apply_u32 register_21c;
    open_cfw_hw_apply_u32 status_248;
    open_cfw_hw_apply_u32 register_388;
    open_cfw_hw_apply_u32 drain_writes;
    open_cfw_hw_apply_u32 delay_cycles;
} open_cfw_hw_apply_model;

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_hw_event_apply_42c0b2_portable(
    open_cfw_hw_apply_model *state, open_cfw_hw_apply_u32 events)
{
    open_cfw_hw_apply_u32 saved_200,saved_388,remaining;
    if(state==0)return;
    saved_200=state->register_200;state->register_200=0U;
    if((events&0x800U)!=0U && (state->register_218&2U)!=0U){
        remaining=state->register_21c;
        while(remaining!=0U){
            if(((state->register_100>>8U)&0xFFU)>=4U){
                state->register_10c=0x08000001U;state->drain_writes++;
                if(remaining<5U)break;
                remaining-=4U;
            }else break;
        }
    }
    if((events&0x210U)!=0U && (state->status_248&6U)==4U){
        saved_388=state->register_388;
        state->register_11c&=~0x10U;state->register_110&=~2U;
        state->register_388|=2U;state->delay_cycles=6U*state->delay_unit;
        state->register_388=saved_388;
        state->register_110|=2U;state->register_11c|=0x10U;
    }
    state->register_208=0xFFFFFFFFU;state->register_200=saved_200;
}
#endif
