/* SPDX-License-Identifier: MIT */
/* Clean-room bounded descriptor, callback, and interrupt registrar. */
typedef __UINT8_TYPE__ open_cfw_descriptor_u8;
typedef __UINT32_TYPE__ open_cfw_descriptor_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_callback_register_41d92c(void);
extern void open_cfw_bootloader_memset_415ff4(void);
extern void open_cfw_bootloader_irq_mask_control_41dcca(void);
extern void open_cfw_bootloader_irq_mask_apply_41de3c(void);
extern void open_cfw_bootloader_irq_handler_bind_41e000(void);
extern void open_cfw_bootloader_irq_state_publish_41da84(void);
extern void open_cfw_bootloader_scb_priority_nibble_43025c(void);
extern void open_cfw_bootloader_nvic_enable_bit_430240(void);
extern void open_cfw_bootloader_boolean_route_41d9aa(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_descriptor_u32 open_cfw_bootloader_descriptor_register_430280(void)
{
    __asm volatile(
        "push.w {r4,r5,r6,r7,r8,lr}\nsub sp,#0x20\nmovs r4,r0\nmovs r5,r1\n"
        "cmp r4,#0\nbeq invalid\ncmp r5,#0\nbne loop_init\n"
        "invalid:\nmovs.w r0,#-1\nb finish\nloop_init:\nmovs r6,#0\nb loop_test\n"
        "type_other:\nmul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#4]\n"
        "cmp r0,#4\nbne loop_next\nldr r0,[pc,#0x1b4]\nldr r1,[r0]\n"
        "mul r7,r7,r6\nldr r0,[r4,r7]\nbl open_cfw_bootloader_callback_register_41d92c\n"
        "b loop_next\ntype_not_one:\nmul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#4]\n"
        "cmp r0,#2\nbne type_other\nldr r0,[pc,#0x19c]\nldr r1,[r0]\n"
        "mul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#6]\nands r0,r0,#3\n"
        "bfi r1,r0,#6,#2\nmul r0,r7,r6\nldr r0,[r4,r0]\n"
        "bl open_cfw_bootloader_callback_register_41d92c\n"
        "mul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#6]\ncmp r0,#0\nbeq loop_next\n"
        "mul r0,r7,r6\nadd r0,r4\nldr r0,[r0,#8]\ncmp r0,#0\nbeq loop_next\n"
        "mul r0,r7,r6\nldr r0,[r4,r0]\nstr r0,[sp]\nadd r0,sp,#4\n"
        "movs r1,#0x1c\nbl open_cfw_bootloader_memset_415ff4\nmovs r0,#1\n"
        "ldr r1,[sp]\nands r1,r1,#0x1f\nlsls r0,r1\nadd r1,sp,#4\n"
        "ldr r2,[sp]\nlsrs r2,r2,#5\nstr.w r0,[r1,r2,lsl #2]\n"
        "add r2,sp,#4\nmovs r1,#1\nmovs r0,#0\n"
        "bl open_cfw_bootloader_irq_mask_control_41dcca\nadd r1,sp,#4\nmovs r0,#0\n"
        "bl open_cfw_bootloader_irq_mask_apply_41de3c\nmovs r3,#0\n"
        "mul r0,r7,r6\nadd r0,r4\nldr r2,[r0,#8]\nldr r1,[sp]\nmovs r0,#0\n"
        "bl open_cfw_bootloader_irq_handler_bind_41e000\nmov r2,sp\nmovs r1,#1\nmovs r0,#0\n"
        "bl open_cfw_bootloader_irq_state_publish_41da84\nldr.w r8,[pc,#0x118]\n"
        "movs r1,#4\nmul r0,r7,r6\nldr r0,[r4,r0]\nlsrs r0,r0,#5\n"
        "ldrsh.w r0,[r8,r0,lsl #1]\nbl open_cfw_bootloader_scb_priority_nibble_43025c\n"
        "mul r7,r7,r6\nldr r0,[r4,r7]\nlsrs r0,r0,#5\n"
        "ldrsh.w r0,[r8,r0,lsl #1]\nbl open_cfw_bootloader_nvic_enable_bit_430240\n"
        "loop_next:\nadds r6,r6,#1\nloop_test:\ncmp r6,r5\nbhs success\n"
        "movs r7,#0xc\nmul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#4]\n"
        "cmp r0,#1\nbne type_not_one\nldr r0,[pc,#0xe4]\nldr r1,[r0]\n"
        "mul r0,r7,r6\nldr r0,[r4,r0]\nbl open_cfw_bootloader_callback_register_41d92c\n"
        "mul r0,r7,r6\nadd r0,r4\nldrb r0,[r0,#5]\ncmp r0,#1\n"
        "bne type_one_false\nmovs r1,#1\nb type_one_ready\n"
        "type_one_false:\nmovs r1,#0\ntype_one_ready:\nuxtb r1,r1\n"
        "mul r7,r7,r6\nldr r0,[r4,r7]\nbl open_cfw_bootloader_boolean_route_41d9aa\n"
        "b loop_next\nsuccess:\nmovs r0,#0\nfinish:\nadd sp,#0x20\n"
        "pop.w {r4,r5,r6,r7,r8,pc}\n");
}
#else
typedef struct {
    open_cfw_descriptor_u32 identifier;
    open_cfw_descriptor_u8 type;
    open_cfw_descriptor_u8 enabled;
    open_cfw_descriptor_u8 mode;
    open_cfw_descriptor_u32 payload;
} open_cfw_descriptor_record;
typedef struct {
    open_cfw_descriptor_u32 callback_calls;
    open_cfw_descriptor_u32 boolean_calls;
    open_cfw_descriptor_u32 irq_setup_calls;
    open_cfw_descriptor_u32 priority_calls;
    open_cfw_descriptor_u32 enable_calls;
    open_cfw_descriptor_u32 last_mask_word;
    open_cfw_descriptor_u32 last_mask_bit;
    open_cfw_descriptor_u32 last_boolean;
} open_cfw_descriptor_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_descriptor_u32 open_cfw_bootloader_descriptor_register_430280_portable(
    const open_cfw_descriptor_record *record, open_cfw_descriptor_u32 count,
    open_cfw_descriptor_model *state)
{
    open_cfw_descriptor_u32 index;
    if (record == 0U || count == 0U || state == 0U) return ~0U;
    for (index = 0U; index < count; index++) {
        if (record[index].type == 1U) {
            state->callback_calls++;
            state->boolean_calls++;
            state->last_boolean = record[index].enabled == 1U ? 1U : 0U;
        } else if (record[index].type == 2U) {
            state->callback_calls++;
            if (record[index].mode != 0U && record[index].payload != 0U) {
                state->irq_setup_calls++;
                state->priority_calls++;
                state->enable_calls++;
                state->last_mask_word = record[index].identifier >> 5U;
                state->last_mask_bit = record[index].identifier & 31U;
            }
        } else if (record[index].type == 4U) {
            state->callback_calls++;
        }
    }
    return 0U;
}
#endif
