/* SPDX-License-Identifier: MIT */
/* Clean-room sixteen-channel state/event fault classifier. */
typedef __UINT8_TYPE__ open_cfw_state_zero_u8;
typedef __UINT32_TYPE__ open_cfw_state_zero_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_state_probe_41f3f0(void);
__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_state_event_zero_42cfe0(void)
{
    __asm volatile(
        "push {r7,lr}\nldr.w r0,[pc,#0x7e0]\nldrb r0,[r0]\ncmp r0,#0\n"
        "beq.w finish\nldr.w r0,[pc,#0x7c8]\nldrb r0,[r0]\ncmp r0,#2\n"
        "bne probe_state\nmovs r0,#1\nldr.w r1,[pc,#0x7cc]\nstrb r0,[r1]\nb finish\n"
        "probe_state:\nbl open_cfw_bootloader_state_probe_41f3f0\ncmp r0,#0\nbeq scan_init\n"
        "ldr.w r0,[pc,#0x7c8]\nldr r1,[r0]\nands r1,r1,#0xf\ncmp r1,#1\n"
        "blt scan_init\nldr r0,[r0]\nands r0,r0,#0xf\ncmp r0,#3\nbge scan_init\n"
        "movs r0,#1\nldr.w r1,[pc,#0x7a0]\nstrb r0,[r1]\nb finish\n"
        "scan_init:\nmovs r0,#0\nb scan_test\nscan_next:\nadds r0,r0,#1\n"
        "scan_test:\ncmp r0,#0x10\nbhs scan_clear\nldr.w r1,[pc,#0x7a0]\n"
        "adds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\nlsls r2,r2,#0x1f\n"
        "bpl channel_ok\nldr.w r2,[pc,#0x794]\nldr r2,[r2]\nlsrs r2,r0\n"
        "lsls r2,r2,#0x1f\nbpl channel_ok\n"
        "adds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\n"
        "ubfx r2,r2,#8,#9\ncmp r2,#0\nbmi range_six_done\n"
        "adds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\n"
        "ubfx r2,r2,#8,#9\ncmp r2,#6\nblt channel_fault_inner\n"
        "range_six_done:\nadds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\n"
        "ubfx r2,r2,#8,#9\ncmp r2,#0x13\nblt middle_false\n"
        "adds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\n"
        "ubfx r2,r2,#8,#9\ncmp r2,#0x19\nbge middle_false\n"
        "movs r2,#1\nb middle_ready\nmiddle_false:\nmovs r2,#0\n"
        "middle_ready:\nuxtb r2,r2\ncmp r2,#0\nbne channel_fault_inner\n"
        "adds.w r2,r1,r0,lsl #5\nldr.w r2,[r2,#0x200]\n"
        "ubfx r2,r2,#8,#9\ncmp.w r2,#0x100\nblt high_false\n"
        "adds.w r1,r1,r0,lsl #5\nldr.w r1,[r1,#0x200]\n"
        "ubfx r1,r1,#8,#9\ncmp.w r1,#0x1e0\nbge high_false\n"
        "movs r1,#1\nb high_ready\nhigh_false:\nmovs r1,#0\n"
        "high_ready:\neors r1,r1,#1\nb invert_inner\n"
        "channel_fault_inner:\nmovs r1,#0\ninvert_inner:\neors r1,r1,#1\nb channel_ready\n"
        "channel_ok:\nmovs r1,#0\nchannel_ready:\nuxtb r1,r1\ncmp r1,#0\n"
        "beq scan_next\nmovs r0,#1\nldr.w r1,[pc,#0x6e4]\nstrb r0,[r1]\nb finish\n"
        "scan_clear:\nmovs r0,#0\nldr.w r1,[pc,#0x6dc]\nstrb r0,[r1]\n"
        "finish:\npop {r0,pc}\n");
}
#else
typedef struct {
    open_cfw_state_zero_u8 enabled;
    open_cfw_state_zero_u8 mode;
    open_cfw_state_zero_u32 probe_status;
    open_cfw_state_zero_u32 state_word;
    open_cfw_state_zero_u32 channel_bitmap;
    open_cfw_state_zero_u32 channel_register[16];
    open_cfw_state_zero_u8 output;
} open_cfw_state_zero_model;

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_state_event_zero_42cfe0_portable(
    open_cfw_state_zero_model *state)
{
    open_cfw_state_zero_u32 index;
    if (state == 0U || state->enabled == 0U) return;
    if (state->mode == 2U) { state->output = 1U; return; }
    if (state->probe_status != 0U) {
        open_cfw_state_zero_u32 value = state->state_word & 15U;
        if (value >= 1U && value < 3U) { state->output = 1U; return; }
    }
    for (index = 0U; index < 16U; index++) {
        open_cfw_state_zero_u32 reg = state->channel_register[index];
        open_cfw_state_zero_u32 value;
        if ((reg & 1U) == 0U || ((state->channel_bitmap >> index) & 1U) == 0U)
            continue;
        value = (reg >> 8U) & 0x1ffU;
        if (value < 6U || (value >= 19U && value < 25U) ||
            (value >= 0x100U && value < 0x1e0U)) {
            state->output = 1U;
            return;
        }
    }
    state->output = 0U;
}
#endif
