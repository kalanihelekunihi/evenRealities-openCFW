/* Apollo Main LVGL animation scheduler entry, native span 0x450408..0x4504ff. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void audio_uart_lv_anim_cancel_matching_450a74(void *);
extern void *audio_uart_lv_list_prepend_482b12(void *);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_tick(void); /* native 0x473482 */
extern void audio_uart_lv_anim_normalize_450a3e(void *);
extern void audio_uart_lv_transition_schedule_4509da(void);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char scheduler_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_anim.c";

static uint32_t read_word(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}
static void write_word(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void *audio_uart_lv_anim_start_450408(void *descriptor) {
    uint8_t *const input = (uint8_t *)descriptor;
    if ((input[0x5cu] & 0x10u) != 0u &&
        (read_word(input, 4u) != 0u || read_word(input, 8u) != 0u))
        audio_uart_lv_anim_cancel_matching_450a74(descriptor);
    uint8_t *const state = audio_uart_display_lv_state;
    uint8_t *const active = (uint8_t *)audio_uart_lv_list_prepend_482b12(state + 0xacu);
    if (active == 0) {
        audio_uart_lvgl_log(3u, scheduler_source, 0x69u, "lv_anim_start",
                            "out of memory");
        __builtin_trap();
    }
    audio_uart_lv_grid_copy_454738(active, input, 0x60u);
    if (read_word(input, 0u) == (uint32_t)(uintptr_t)input)
        write_word(active, 0u, (uint32_t)(uintptr_t)active);
    active[0x5cu] = (uint8_t)((active[0x5cu] & ~4u) | ((state[0xa5u] & 1u) << 2));
    write_word(active, 0x50u, audio_uart_lv_tick());
    active[0x5cu] &= (uint8_t)~1u;
    if ((active[0x5cu] & 0x10u) != 0u) {
        const uint32_t delay_callback = read_word(active, 0x18u);
        if (delay_callback != 0u) {
            const int32_t shift = ((int32_t (*)(void *))(uintptr_t)delay_callback)(active);
            write_word(active, 0x24u, read_word(active, 0x24u) + (uint32_t)shift);
            write_word(active, 0x2cu, read_word(active, 0x2cu) + (uint32_t)shift);
        }
        audio_uart_lv_anim_normalize_450a3e(active);
        const uint32_t path_callback = read_word(active, 0x20u);
        const uint32_t value = ((uint32_t (*)(void *))(uintptr_t)path_callback)(active);
        write_word(active, 0x28u, value);
        const uint32_t exec_callback = read_word(active, 4u);
        if (exec_callback != 0u)
            ((void (*)(void *, uint32_t))(uintptr_t)exec_callback)(
                (void *)(uintptr_t)read_word(active, 0u), value);
        const uint32_t custom_callback = read_word(active, 8u);
        if (custom_callback != 0u)
            ((void (*)(void *, uint32_t))(uintptr_t)custom_callback)(active, value);
    }
    audio_uart_lv_transition_schedule_4509da();
    return active;
}
