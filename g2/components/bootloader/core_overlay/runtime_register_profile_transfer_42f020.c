/* SPDX-License-Identifier: MIT */
/* Clean-room validated hardware register-profile capture/apply service. */
typedef __UINT8_TYPE__ open_cfw_profile_transfer_u8;
typedef __UINT32_TYPE__ open_cfw_profile_transfer_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_query_41bf84(void);
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);
extern void open_cfw_bootloader_clock_config_422364(void);
extern void open_cfw_bootloader_delay_status_41c17a(void);
__attribute__((used,noinline,naked,visibility("default")))
open_cfw_profile_transfer_u32 open_cfw_bootloader_register_profile_transfer_42f020(void)
{
    __asm volatile(
        "push {r3,r4,r5,lr}\nmovs r5,r2\nmovs r4,r0\nldr r2,[r4,#4]\n"
        "cmp r0,#0\nbeq invalid_handle\nldr r0,[r0]\nbic r0,r0,#0xfe000000\n"
        "ldr r2,[pc,#0x148]\ncmp r0,r2\nbeq operation_select\n"
        "invalid_handle:\nmovs r0,#2\nb return_status\n"
        "operation_select:\nuxtb r1,r1\ncmp r1,#0\nbeq apply_profile\n"
        "cmp r1,#2\nbeq capture_profile\nblo capture_profile\nb unsupported\n"
        "apply_profile:\nmovs r0,r5\nuxtb r0,r0\ncmp r0,#0\nbeq apply_ready\n"
        "ldrb r0,[r4,#0xc]\ncmp r0,#0\nbne apply_ready\nmovs r0,#7\nb return_status\n"
        "apply_ready:\nmovs r0,#0xf\nbl open_cfw_bootloader_mode_query_41bf84\n"
        "uxtb r5,r5\ncmp r5,#0\nbeq return_zero\nmovs r1,#0xf\nmovs r0,#4\n"
        "bl open_cfw_bootloader_mode_enable_route_4222f0\ncmp r0,#0\nbne return_status\n"
        "ldr r0,[r4,#0x14]\nldr r1,[pc,#0x10c]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x18]\nldr r1,[pc,#0x128]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x1c]\nldr r1,[pc,#0x128]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x20]\nldr r1,[pc,#0x124]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x24]\nldr r1,[pc,#0x124]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x28]\nldr r1,[pc,#0x120]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x2c]\nldr r1,[pc,#0x120]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x30]\nldr r1,[pc,#0x11c]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x34]\nldr r1,[pc,#0xe0]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x38]\nldr r1,[pc,#0xdc]\nstr r0,[r1]\n"
        "ldr r0,[r4,#0x3c]\nldr r1,[pc,#0xdc]\nstr r0,[r1]\n"
        "ldr r0,[pc,#0xe8]\nmovs r1,#0\nstr r1,[r0]\nldr r1,[pc,#0xc0]\n"
        "ldr r2,[r4,#0x10]\nlsrs r2,r2,#1\nlsls r2,r2,#1\nstr r2,[r1]\n"
        "ldrb r2,[r4,#0x10]\nands r2,r2,#1\nldr r3,[r1]\nlsrs r3,r3,#1\n"
        "lsls r3,r3,#1\norrs r2,r3\nstr r2,[r1]\nldr r1,[r4,#0x40]\n"
        "str r1,[r0]\nmovs r0,#0\nstrb r0,[r4,#0xc]\n"
        "return_zero:\nmovs r0,#0\nreturn_status:\npop {r1,r4,r5,pc}\n"
        "capture_profile:\nuxtb r5,r5\ncmp r5,#0\nbeq capture_finish\n"
        "ldr r0,[pc,#0x98]\nldr r0,[r0]\nstr r0,[r4,#0x14]\n"
        "ldr r0,[pc,#0xb8]\nldr r0,[r0]\nstr r0,[r4,#0x18]\n"
        "ldr r0,[pc,#0xb4]\nldr r0,[r0]\nstr r0,[r4,#0x1c]\n"
        "ldr r0,[pc,#0xb4]\nldr r0,[r0]\nstr r0,[r4,#0x20]\n"
        "ldr r0,[pc,#0xb0]\nldr r0,[r0]\nstr r0,[r4,#0x24]\n"
        "ldr r0,[pc,#0xb0]\nldr r0,[r0]\nstr r0,[r4,#0x28]\n"
        "ldr r0,[pc,#0xac]\nldr r0,[r0]\nstr r0,[r4,#0x2c]\n"
        "ldr r0,[pc,#0xac]\nldr r0,[r0]\nstr r0,[r4,#0x30]\n"
        "ldr r0,[pc,#0x6c]\nldr r0,[r0]\nstr r0,[r4,#0x34]\n"
        "ldr r0,[pc,#0x6c]\nldr r0,[r0]\nstr r0,[r4,#0x38]\n"
        "ldr r0,[pc,#0x68]\nldr r0,[r0]\nstr r0,[r4,#0x3c]\n"
        "ldr r0,[pc,#0x74]\nldr r0,[r0]\nstr r0,[r4,#0x40]\n"
        "ldr r0,[pc,#0x4c]\nldr r0,[r0]\nstr r0,[r4,#0x10]\n"
        "movs r0,#1\nstrb r0,[r4,#0xc]\n"
        "capture_finish:\nmovs r1,#0xf\nmovs r0,#4\nbl open_cfw_bootloader_clock_config_422364\n"
        "movs r0,#0xf\nbl open_cfw_bootloader_delay_status_41c17a\nb return_zero\n"
        "unsupported:\nmovs r0,#6\nb return_status\n");
}
#else
typedef struct {
    open_cfw_profile_transfer_u32 header;
    open_cfw_profile_transfer_u8 valid;
    open_cfw_profile_transfer_u32 control;
    open_cfw_profile_transfer_u32 field[11];
    open_cfw_profile_transfer_u32 auxiliary;
    open_cfw_profile_transfer_u32 hardware_control;
    open_cfw_profile_transfer_u32 hardware_field[11];
    open_cfw_profile_transfer_u32 hardware_auxiliary;
    open_cfw_profile_transfer_u32 route_status;
    open_cfw_profile_transfer_u32 mode_query_calls;
    open_cfw_profile_transfer_u32 clock_config_calls;
    open_cfw_profile_transfer_u32 delay_status_calls;
} open_cfw_profile_transfer_model;

__attribute__((used,noinline,visibility("default")))
open_cfw_profile_transfer_u32 open_cfw_bootloader_register_profile_transfer_42f020_portable(
    open_cfw_profile_transfer_model *state, open_cfw_profile_transfer_u32 operation,
    open_cfw_profile_transfer_u32 enabled)
{
    open_cfw_profile_transfer_u32 i;
    if (state == 0U || (state->header & 0x01ffffffU) != 0x01afafafU) return 2U;
    operation = (open_cfw_profile_transfer_u8)operation;
    enabled = (open_cfw_profile_transfer_u8)enabled;
    if (operation == 0U) {
        if (enabled != 0U && state->valid == 0U) return 7U;
        state->mode_query_calls++;
        if (enabled == 0U) return 0U;
        if (state->route_status != 0U) return state->route_status;
        for (i = 0U; i < 11U; i++) state->hardware_field[i] = state->field[i];
        state->hardware_control = state->control;
        state->hardware_auxiliary = state->auxiliary;
        state->valid = 0U;
        return 0U;
    }
    if (operation > 2U) return 6U;
    if (enabled != 0U) {
        for (i = 0U; i < 11U; i++) state->field[i] = state->hardware_field[i];
        state->control = state->hardware_control;
        state->auxiliary = state->hardware_auxiliary;
        state->valid = 1U;
    }
    state->clock_config_calls++;
    state->delay_status_calls++;
    return 0U;
}
#endif
