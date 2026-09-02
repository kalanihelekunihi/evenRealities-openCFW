/* SPDX-License-Identifier: MIT */
/* Clean-room mode-to-service router with an interrupt-safe aggregate bitset. */
typedef __UINT8_TYPE__ open_cfw_mode_apply_u8;
typedef __UINT32_TYPE__ open_cfw_mode_apply_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_critical_enter_41b8ec(void);
extern void open_cfw_bootloader_boolean_route_status_4303bc(void);

__attribute__((used,noinline,naked,visibility("default")))
void open_cfw_bootloader_mode_apply_42ff00(void)
{
    __asm volatile(
        "push {r3,r4,r5,lr}\n"
        "movs r4,r0\nmovs r5,r1\nmovs r0,r4\nuxtb r0,r0\n"
        "cmp r0,#1\nbeq mode_1\ncmp r0,#2\nbeq mode_2\n"
        "cmp r0,#3\nbeq mode_3\ncmp r0,#4\nbeq mode_4\n"
        "cmp r0,#6\nbeq bit_mode\ncmp r0,#7\nbeq bit_mode\n"
        "cmp r0,#8\nbeq mode_8\ncmp r0,#9\nbeq bit_mode\nb finish\n"
        "mode_1:\nuxtb r5,r5\ncmp r5,#1\nbne mode_1_false\n"
        "movs r1,#1\nb mode_1_ready\nmode_1_false:\nmovs r1,#0\n"
        "mode_1_ready:\nuxtb r1,r1\nmovs r0,#0x81\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb finish\n"
        "mode_2:\nuxtb r5,r5\ncmp r5,#1\nbne mode_2_false\n"
        "movs r1,#1\nb mode_2_ready\nmode_2_false:\nmovs r1,#0\n"
        "mode_2_ready:\nuxtb r1,r1\nmovs r0,#0x7d\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb finish\n"
        "mode_3:\nuxtb r5,r5\ncmp r5,#1\nbne mode_3_false\n"
        "movs r1,#1\nb mode_3_ready\nmode_3_false:\nmovs r1,#0\n"
        "mode_3_ready:\nuxtb r1,r1\nmovs r0,#0x80\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb finish\n"
        "mode_4:\nuxtb r5,r5\ncmp r5,#1\nbne mode_4_false\n"
        "movs r1,#1\nb mode_4_ready\nmode_4_false:\nmovs r1,#0\n"
        "mode_4_ready:\nuxtb r1,r1\nmovs r0,#0x8e\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb finish\n"
        "bit_mode:\nbl open_cfw_bootloader_critical_enter_41b8ec\nstr r0,[sp]\n"
        "movs r0,r5\nuxtb r0,r0\ncmp r0,#1\nbne bit_clear_test\n"
        "ldr r0,[pc,#0x270]\nldr r1,[r0]\nmovs r2,#1\n"
        "lsls.w r4,r2,r4\norrs r4,r1\nstr r4,[r0]\nb bit_publish\n"
        "bit_clear_test:\nuxtb r5,r5\ncmp r5,#0\nbne bit_publish\n"
        "ldr r0,[pc,#0x258]\nldr r1,[r0]\nmovs r2,#1\n"
        "lsls.w r4,r2,r4\nbics.w r4,r1,r4\nstr r4,[r0]\n"
        "bit_publish:\nldr r0,[pc,#0x248]\nldr r0,[r0]\ncmp r0,#0\n"
        "bne bit_nonzero\nmovs r1,#0\nmovs r0,#0x86\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb bit_restore\n"
        "bit_nonzero:\nmovs r1,#1\nmovs r0,#0x86\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\n"
        "bit_restore:\nldr r0,[sp]\nmsr primask,r0\nb finish\n"
        "mode_8:\nuxtb r5,r5\ncmp r5,#1\nbne mode_8_false\n"
        "movs r1,#1\nb mode_8_ready\nmode_8_false:\nmovs r1,#0\n"
        "mode_8_ready:\nuxtb r1,r1\nmovs r0,#0x92\n"
        "bl open_cfw_bootloader_boolean_route_status_4303bc\nb finish\n"
        "finish:\npop {r0,r4,r5,pc}\n");
}
#else
typedef open_cfw_mode_apply_u32 (*open_cfw_mode_apply_route_fn)(
    open_cfw_mode_apply_u32, open_cfw_mode_apply_u32);

__attribute__((used,noinline,visibility("default")))
void open_cfw_bootloader_mode_apply_42ff00_portable(
    open_cfw_mode_apply_u32 mode, open_cfw_mode_apply_u32 value,
    open_cfw_mode_apply_u32 *aggregate_bits,
    open_cfw_mode_apply_route_fn route)
{
    open_cfw_mode_apply_u32 service = 0U;
    open_cfw_mode_apply_u32 normalized =
        (open_cfw_mode_apply_u8)value == 1U ? 1U : 0U;
    open_cfw_mode_apply_u32 compact_mode = (open_cfw_mode_apply_u8)mode;

    if (route == 0U) {
        return;
    }
    if (compact_mode == 1U) service = 0x81U;
    else if (compact_mode == 2U) service = 0x7dU;
    else if (compact_mode == 3U) service = 0x80U;
    else if (compact_mode == 4U) service = 0x8eU;
    else if (compact_mode == 8U) service = 0x92U;
    else if (compact_mode == 6U || compact_mode == 7U || compact_mode == 9U) {
        open_cfw_mode_apply_u32 bit;
        if (aggregate_bits == 0U) {
            return;
        }
        bit = mode < 32U ? (1U << mode) : 0U;
        if ((open_cfw_mode_apply_u8)value == 1U) *aggregate_bits |= bit;
        else if ((open_cfw_mode_apply_u8)value == 0U) *aggregate_bits &= ~bit;
        (void)route(0x86U, *aggregate_bits != 0U ? 1U : 0U);
        return;
    } else {
        return;
    }
    (void)route(service, normalized);
}
#endif
