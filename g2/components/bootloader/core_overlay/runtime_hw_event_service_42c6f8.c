/* SPDX-License-Identifier: MIT */
/* Clean-room hardware event, descriptor, callback, and command-queue service. */
typedef __UINT8_TYPE__ open_cfw_hw_event_u8;
typedef __UINT32_TYPE__ open_cfw_hw_event_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_error_classify_42c076(void);
extern void open_cfw_bootloader_hw_event_apply_42c0b2(void);
extern void open_cfw_bootloader_hw_descriptor_publish_42c45a(void);
extern void open_cfw_bootloader_cmdq_get_status_427a56(void);
extern void open_cfw_bootloader_cmdq_error_resume_427b38(void);
extern void open_cfw_bootloader_cmdq_adapter_enable_42c420(void);
extern void open_cfw_bootloader_cmdq_adapter_disable_42c44e(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_hw_event_service_42c6f8(void)
{__asm volatile(
 "push.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,lr}\n"
 "movs r4,r0\nmov r8,r1\nmovs r7,#0\nmovs r6,r4\ncmp r4,#0\nbeq invalid\n"
 "ldr r0,[r4]\nbic r0,r0,#0xfe000000\nldr.w r1,[pc,#0x6a0]\ncmp r0,r1\nbeq valid\n"
 "invalid: movs r0,#2\nb finish\n"
 "valid: ldr r5,[r6,#4]\nldrb.w r0,[r6,#0x83c]\ncmp r0,#0\nbeq inactive\n"
 "ldr r0,[r6,#0x18]\norrs.w r8,r8,r0\nstr.w r8,[r6,#0x18]\n"
 "ldr r0,[r6,#0x18]\nmovw r1,#0x801\ntst r0,r1\nbeq active_done\n"
 "ldr.w r4,[pc,#0x684]\nadds.w r0,r4,r5,lsl #12\nldr.w r0,[r0,#0x218]\n"
 "lsls r0,r0,#31\nbpl active_gate_true\nldr r0,[r6,#0x18]\nmovw r1,#0x4e7c\n"
 "tst r0,r1\nbeq active_gate_false\nactive_gate_true: movs r0,#1\nb active_gate_join\n"
 "active_gate_false: movs r0,#0\nactive_gate_join: uxtb r0,r0\ncmp r0,#0\nbeq active_done\n"
 "ldr.w r0,[r6,#0x850]\nadds r0,r0,#1\nstr.w r0,[r6,#0x850]\n"
 "ldr.w r0,[r6,#0x840]\nsubs r0,r0,#1\nstr.w r0,[r6,#0x840]\n"
 "ldr.w r0,[r6,#0x850]\nldr.w r1,[r6,#0x848]\nudiv r2,r0,r1\n"
 "mls r0,r1,r2,r0\nldr.w r1,[r6,#0x854]\nlsls r0,r0,#5\nadd.w r7,r1,r0\n"
 "ldr r0,[r7,#0x18]\ncmp r0,#0\nbeq callback_done\nldr r1,[r6,#0x18]\n"
 "movs r0,r5\nbl open_cfw_bootloader_hw_error_classify_42c076\nmovs r1,r0\n"
 "ldr r0,[r7,#0x1c]\nldr r2,[r7,#0x18]\nblx r2\nmovs r0,#0\nstr r0,[r7,#0x18]\n"
 "callback_done: movw r1,#0x4a7c\nldr r0,[r6,#0x18]\ntst r0,r1\nbeq pending_check\n"
 "adds.w r0,r4,r5,lsl #12\nadds.w r0,r0,#0x218\nldr r2,[r0]\nlsrs r2,r2,#1\n"
 "lsls r2,r2,#1\nstr r2,[r0]\nmovs r0,#0\nadds.w r2,r4,r5,lsl #12\n"
 "str.w r0,[r2,#0x224]\nldr r0,[r6,#0x18]\nands r1,r0\nmovs r0,r6\n"
 "bl open_cfw_bootloader_hw_event_apply_42c0b2\n"
 "pending_check: ldr.w r0,[r6,#0x840]\ncmp r0,#0\nbeq active_empty\n"
 "movs r0,#0\nadds.w r4,r4,r5,lsl #12\nstr.w r0,[r4,#0x224]\n"
 "movs r0,#0\nstr r0,[r6,#0x18]\nmovs r0,r6\n"
 "bl open_cfw_bootloader_hw_descriptor_publish_42c45a\nb active_done\n"
 "active_empty: movs r0,#0\nstrb.w r0,[r6,#0x83c]\nadds.w r0,r4,r5,lsl #12\n"
 "ldr.w r1,[r0,#0x200]\nldr.w r0,[pc,#0x5c0]\nands r1,r0\n"
 "adds.w r0,r4,r5,lsl #12\nstr.w r1,[r0,#0x200]\nmovs.w r0,#0x800000\n"
 "adds.w r4,r4,r5,lsl #12\nstr.w r0,[r4,#0x238]\n"
 "active_done: movs r0,#0\nb finish\n"
 "inactive: ldr r0,[r6,#0x24]\ncmp r0,#0\nbeq.w return_status\n"
 "ldr.w r0,[r6,#0x828]\ncmp r0,#0\nbeq.w cleanup_adapter\n"
 "mov r1,sp\nldr.w r0,[r6,#0x828]\nbl open_cfw_bootloader_cmdq_get_status_427a56\n"
 "movs r7,r0\ncmp r0,#0\nbne.w cleanup_adapter\n"
 "movs r0,#0\nstrb.w r0,[r6,#0x834]\nb drain_test\n"
 "drain_loop: ldrb.w r0,[r6,#0x834]\ncmp r0,#0\nbne drain_done\n"
 "ldr r0,[r6,#0x1c]\nadds r0,r0,#1\nstr r0,[r6,#0x1c]\n"
 "ldr r0,[r6,#0x24]\nsubs r0,r0,#1\nstr r0,[r6,#0x24]\n"
 "ldrb.w r9,[r6,#0x1c]\nand r9,r9,#0xff\nadd.w r0,r6,r9,lsl #2\n"
 "ldr r0,[r0,#0x28]\ncmp r0,#0\nbeq drain_test\nmovs r1,#0\n"
 "add.w r0,r6,r9,lsl #2\nldr.w r0,[r0,#0x428]\n"
 "add.w r2,r6,r9,lsl #2\nldr r2,[r2,#0x28]\nblx r2\n"
 "ldrb.w r0,[r6,#0x82c]\ncmp r0,#2\nbeq drain_test\nmovs r0,#0\n"
 "add.w r1,r6,r9,lsl #2\nstr r0,[r1,#0x28]\n"
 "drain_test: ldr r0,[r6,#0x1c]\nldr r1,[sp]\ncmp r0,r1\nbne drain_loop\n"
 "drain_done: ldrb.w r0,[r6,#0x834]\ncmp r0,#0\nbne adapter_state\n"
 "movw r9,#0x4a7c\ntst.w r8,r9\nbeq adapter_state\n"
 "ldr r0,[r6,#0x1c]\nadds r0,r0,#1\nstr r0,[r6,#0x1c]\n"
 "ldr r0,[r6,#0x24]\nsubs r0,r0,#1\nstr r0,[r6,#0x24]\n"
 "ldrb.w r10,[r6,#0x1c]\nand r10,r10,#0xff\nadd.w r0,r6,r10,lsl #2\n"
 "ldr r0,[r0,#0x28]\ncmp r0,#0\nbeq post_callback\nmov r1,r8\nmovs r0,r5\n"
 "bl open_cfw_bootloader_hw_error_classify_42c076\nmovs r1,r0\n"
 "add.w r0,r6,r10,lsl #2\nldr.w r0,[r0,#0x428]\n"
 "add.w r2,r6,r10,lsl #2\nldr r2,[r2,#0x28]\nblx r2\n"
 "ldrb.w r0,[r6,#0x82c]\ncmp r0,#2\nbeq post_callback\nmovs r0,#0\n"
 "add.w r1,r6,r10,lsl #2\nstr r0,[r1,#0x28]\n"
 "post_callback: ldr.w r0,[pc,#0x4c8]\nadds.w r1,r0,r5,lsl #12\n"
 "adds.w r1,r1,#0x228\nldr r2,[r1]\nlsrs r2,r2,#1\nlsls r2,r2,#1\n"
 "str r2,[r1]\nadds.w r1,r0,r5,lsl #12\nadds.w r1,r1,#0x218\n"
 "ldr r2,[r1]\nlsrs r2,r2,#1\nlsls r2,r2,#1\nstr r2,[r1]\n"
 "movs r1,#0\nadds.w r0,r0,r5,lsl #12\nstr.w r1,[r0,#0x224]\n"
 "ands.w r8,r9,r8\nmov r1,r8\nmovs r0,r6\n"
 "bl open_cfw_bootloader_hw_event_apply_42c0b2\n"
 "ldr.w r0,[r6,#0x828]\nbl open_cfw_bootloader_cmdq_error_resume_427b38\n"
 "ldr r0,[r6,#0x24]\ncmp r0,#0\nbeq adapter_state\nmovs r0,r6\n"
 "bl open_cfw_bootloader_cmdq_adapter_enable_42c420\n"
 "adapter_state: ldr r0,[r6,#0x24]\ncmp r0,#0\nbne cleanup_adapter\n"
 "movs r0,r4\nbl open_cfw_bootloader_cmdq_adapter_disable_42c44e\n"
 "cleanup_adapter: ldr r0,[r6,#0x24]\ncmp r0,#0\nbne return_status\n"
 "ldr.w r0,[pc,#0x468]\nmovs r1,#0\nadds.w r2,r0,r5,lsl #12\n"
 "str.w r1,[r2,#0x200]\nmovs.w r1,#-1\nadds.w r2,r0,r5,lsl #12\n"
 "str.w r1,[r2,#0x208]\nldr r1,[r6,#0x14]\nadds.w r0,r0,r5,lsl #12\n"
 "str.w r1,[r0,#0x200]\n"
 "return_status: movs r0,r7\nfinish: add sp,#0x10\npop.w {r4,r5,r6,r7,r8,r9,r10,pc}\n");}
#else
typedef struct {
    open_cfw_hw_event_u32 header;
    open_cfw_hw_event_u32 event_bits;
    open_cfw_hw_event_u32 producer;
    open_cfw_hw_event_u32 pending;
    open_cfw_hw_event_u32 ring_size;
    open_cfw_hw_event_u32 callback_present;
    open_cfw_hw_event_u32 callback_count;
    open_cfw_hw_event_u32 descriptor_publish_count;
    open_cfw_hw_event_u32 applied_event_bits;
    open_cfw_hw_event_u32 register_200;
    open_cfw_hw_event_u32 register_208;
    open_cfw_hw_event_u32 register_218;
    open_cfw_hw_event_u32 register_224;
    open_cfw_hw_event_u32 register_238;
    open_cfw_hw_event_u8 active_service;
} open_cfw_hw_event_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_hw_event_u32 open_cfw_bootloader_hw_event_service_42c6f8_portable(
    open_cfw_hw_event_model *state,
    open_cfw_hw_event_u32 incoming_events,
    open_cfw_hw_event_u32 descriptor_ready,
    open_cfw_hw_event_u32 cmdq_status)
{
    open_cfw_hw_event_u32 gated;
    if(state==0 || (state->header&0x01FFFFFFU)!=0x01123456U)return 2U;
    if(state->active_service!=0U){
        state->event_bits|=incoming_events;
        gated=state->event_bits&0x00000801U;
        if(gated!=0U && (descriptor_ready!=0U ||
                         (state->event_bits&0x00004E7CU)!=0U)){
            state->producer++;
            if(state->pending!=0U)state->pending--;
            if(state->callback_present!=0U){
                state->callback_count++;
                state->callback_present=0U;
            }
            if((state->event_bits&0x00004A7CU)!=0U){
                state->register_218&=~1U;
                state->register_224=0U;
                state->applied_event_bits=state->event_bits&0x00004A7CU;
            }
            if(state->pending!=0U){
                state->event_bits=0U;
                state->register_224=0U;
                state->descriptor_publish_count++;
            }else{
                state->active_service=0U;
                state->register_200&=0xFFFFFBFEU;
                state->register_238=0x00800000U;
            }
        }
        return 0U;
    }
    if(state->pending==0U)return 0U;
    if(cmdq_status!=0U)return cmdq_status;
    if((incoming_events&0x00004A7CU)!=0U){
        state->register_218&=~1U;
        state->register_224=0U;
        state->applied_event_bits=incoming_events&0x00004A7CU;
    }
    if(state->pending==0U){
        state->register_200=0U;
        state->register_208=0xFFFFFFFFU;
    }
    return 0U;
}
#endif
