/* SPDX-License-Identifier: MIT */
/* Clean-room event-value hardware-profile publisher and saved-field updater. */
typedef __UINT8_TYPE__ open_cfw_event_profile_u8;
typedef __UINT32_TYPE__ open_cfw_event_profile_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_finalize_41cde0(void);
extern void open_cfw_bootloader_register_power_toggle_42f1c8(void);
extern void open_cfw_bootloader_delay_cycles_41d1c0(void);

__attribute__((used,noinline,naked,visibility("default")))
open_cfw_event_profile_u32 open_cfw_bootloader_event_value_provider_42f204(void)
{
    __asm volatile(
        "push {r7,lr}\nuxtb r0,r0\ncmp r0,#2\nbeq mode_ready\n"
        "movs r1,#0\nmovs r0,#1\nbl open_cfw_bootloader_mode_finalize_41cde0\n"
        "mode_ready:\nldr.w r0,[pc,#0x3dc]\nldr r0,[r0]\n"
        "ubfx r0,r0,#4,#2\ncmp r0,#3\nbeq active_profile\n"
        "ldr.w r0,[pc,#0x3d4]\nldr r1,[r0]\nubfx r1,r1,#0xa,#4\n"
        "ldr.w r2,[pc,#0x3cc]\nstr r1,[r2]\nmovs r1,#2\n"
        "ldr r2,[r0]\nbfi r2,r1,#0xa,#4\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x3c0]\nldr r1,[r0]\nands r1,r1,#0x3f\n"
        "ldr.w r2,[pc,#0x3bc]\nstr r1,[r2]\nldr r1,[r0]\n"
        "ands r1,r1,#0x3f\nadds r1,r1,#5\ncmp r1,#0x40\n"
        "blo short_increment\nmovs r1,#0x3f\nb publish_six_bit\n"
        "active_profile:\nldr.w r0,[pc,#0x3a8]\nldrb r0,[r0]\n"
        "cmp r0,#0\nbeq finish\nmovs r0,#0\n"
        "bl open_cfw_bootloader_register_power_toggle_42f1c8\n"
        "ldr.w r0,[pc,#0x388]\nmovs r1,#1\nldr r2,[r0]\n"
        "bfi r2,r1,#0xa,#4\nstr r2,[r0]\n"
        "ldr.w r0,[pc,#0x390]\nldr r1,[r0]\nadds r1,#9\n"
        "cmp r1,#0x80\nblo active_first_short\nmovs r0,#0x7f\nb active_first_ready\n"
        "active_first_short:\nldr r0,[r0]\nadds r0,#9\n"
        "active_first_ready:\nldr.w r1,[pc,#0x380]\nldr r2,[r1]\n"
        "bfi r2,r0,#0,#7\nstr r2,[r1]\n"
        "ldr.w r0,[pc,#0x378]\nldr r1,[r0]\norrs r1,r1,#0x100\nstr r1,[r0]\n"
        "ldr.w r0,[pc,#0x370]\nldr r1,[r0]\nadds r1,#0xf\n"
        "cmp r1,#0x80\nblo active_second_short\nmovs r0,#0x7f\nb active_second_ready\n"
        "active_second_short:\nldr r0,[r0]\nadds r0,#0xf\n"
        "active_second_ready:\nldr.w r1,[pc,#0x360]\nldr r2,[r1]\n"
        "bfi r2,r0,#0,#7\nstr r2,[r1]\n"
        "ldr.w r0,[pc,#0x358]\nldr r1,[r0]\n"
        "orrs r1,r1,#0x60000000\nstr r1,[r0]\nmovs r0,#1\n"
        "bl open_cfw_bootloader_register_power_toggle_42f1c8\n"
        "movs r0,#0xf\nbl open_cfw_bootloader_delay_cycles_41d1c0\nb finish\n"
        "short_increment:\nldr r1,[r0]\nands r1,r1,#0x3f\nadds r1,r1,#5\n"
        "publish_six_bit:\nldr r2,[r0]\nbfi r2,r1,#0,#6\nstr r2,[r0]\n"
        "movs r0,#0xf\nbl open_cfw_bootloader_delay_cycles_41d1c0\n"
        "finish:\nmovs r0,#0\npop {r1,pc}\n");
}
#else
typedef struct {
    open_cfw_event_profile_u32 status_40021108;
    open_cfw_event_profile_u32 control_40020080;
    open_cfw_event_profile_u32 trim_40020088;
    open_cfw_event_profile_u32 saved_control_field;
    open_cfw_event_profile_u32 saved_trim_field;
    open_cfw_event_profile_u8 active_allowed;
    open_cfw_event_profile_u32 source_first;
    open_cfw_event_profile_u32 target_first;
    open_cfw_event_profile_u32 feature_400201b0;
    open_cfw_event_profile_u32 source_second;
    open_cfw_event_profile_u32 target_second;
    open_cfw_event_profile_u32 feature_40020374;
    open_cfw_event_profile_u32 finalize_calls;
    open_cfw_event_profile_u32 power_off_calls;
    open_cfw_event_profile_u32 power_on_calls;
    open_cfw_event_profile_u32 delay_cycles;
} open_cfw_event_profile_model;

static open_cfw_event_profile_u32 open_cfw_event_profile_sat(
    open_cfw_event_profile_u32 value, open_cfw_event_profile_u32 increment,
    open_cfw_event_profile_u32 limit)
{
    return value + increment < limit ? value + increment : limit - 1U;
}

__attribute__((used,noinline,visibility("default")))
open_cfw_event_profile_u32 open_cfw_bootloader_event_value_provider_42f204_portable(
    open_cfw_event_profile_u32 event_value, open_cfw_event_profile_model *state)
{
    open_cfw_event_profile_u32 value;
    if (state == 0U) return ~0U;
    if ((open_cfw_event_profile_u8)event_value != 2U) state->finalize_calls++;
    if (((state->status_40021108 >> 4U) & 3U) != 3U) {
        state->saved_control_field = (state->control_40020080 >> 10U) & 15U;
        state->control_40020080 =
            (state->control_40020080 & ~(15U << 10U)) | (2U << 10U);
        value = state->trim_40020088 & 63U;
        state->saved_trim_field = value;
        value = open_cfw_event_profile_sat(value, 5U, 64U);
        state->trim_40020088 = (state->trim_40020088 & ~63U) | value;
        state->delay_cycles = 15U;
        return 0U;
    }
    if (state->active_allowed == 0U) return 0U;
    state->power_off_calls++;
    state->control_40020080 =
        (state->control_40020080 & ~(15U << 10U)) | (1U << 10U);
    value = open_cfw_event_profile_sat(state->source_first, 9U, 128U);
    state->target_first = (state->target_first & ~127U) | value;
    state->feature_400201b0 |= 0x100U;
    value = open_cfw_event_profile_sat(state->source_second, 15U, 128U);
    state->target_second = (state->target_second & ~127U) | value;
    state->feature_40020374 |= 0x60000000U;
    state->power_on_calls++;
    state->delay_cycles = 15U;
    return 0U;
}
#endif
