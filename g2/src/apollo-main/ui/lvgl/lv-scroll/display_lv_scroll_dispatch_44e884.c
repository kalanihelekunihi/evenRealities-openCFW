/* Apollo Main scroll dispatch 0x44e884..0x44e9b9 and finish callback 0x44f3f0. */
#include <stdint.h>

extern void *audio_uart_lv_display_for_object(void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern int32_t audio_uart_lv_display_width_44fa7e(void *);
extern int32_t audio_uart_lv_display_height_44faa8(void *);
extern int32_t audio_uart_lv_anim_duration_clamp_4505a2(int32_t, int32_t, int32_t);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lv_anim_path_450672(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern int32_t audio_uart_lv_obj_x_44e486(void *);
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_uart_lv_style_unlink_450500(void *, void *);
extern uint32_t audio_uart_lv_scroll_by_44ea98(void *, int32_t, int32_t);
extern void audio_uart_lv_scroll_anim_x_44f3b8(void *, int32_t);
extern void audio_uart_lv_scroll_anim_y_44f3d4(void *, int32_t);

typedef struct {
    uint8_t bytes[0x60];
} scroll_anim_descriptor;

static void write_word(scroll_anim_descriptor *descriptor, uint32_t offset, uintptr_t value) {
    *(uint32_t *)(void *)(descriptor->bytes + offset) = (uint32_t)value;
}

void audio_uart_lv_scroll_anim_finish_44f3f0(void *descriptor) {
    const uint8_t *const bytes = (const uint8_t *)descriptor;
    if ((bytes[0x5cu] & 8u) != 0u) {
        void *object = *(void *const *)descriptor;
        (void)audio_uart_lv_obj_event_451670(object, 0x0eu, 0);
    }
}

void audio_uart_lv_scroll_dispatch_44e884(void *object, int32_t x, int32_t y,
                                            uint32_t animated) {
    if ((x | y) == 0) return;
    if ((uint8_t)animated == 0u) {
        (void)audio_uart_lv_style_unlink_450500(
            object, (void *)audio_uart_lv_scroll_anim_y_44f3d4);
        (void)audio_uart_lv_style_unlink_450500(
            object, (void *)audio_uart_lv_scroll_anim_x_44f3b8);
        if ((uint8_t)audio_uart_lv_obj_event_451670(object, 0x0cu, 0) == 1u &&
            (uint8_t)audio_uart_lv_scroll_by_44ea98(object, x, y) == 1u)
            (void)audio_uart_lv_obj_event_451670(object, 0x0eu, 0);
        return;
    }
    void *const display = audio_uart_lv_display_for_object(object);
    scroll_anim_descriptor animation;
    audio_uart_lv_anim_init_4503d6(&animation);
    write_word(&animation, 0u, (uintptr_t)object);
    write_word(&animation, 0x14u, (uintptr_t)audio_uart_lv_scroll_anim_finish_44f3f0);
    if (x != 0) {
        write_word(&animation, 0x30u, (uint32_t)audio_uart_lv_anim_duration_clamp_4505a2(
            audio_uart_lv_display_width_44fa7e(display) >> 1, 200, 400));
        const int32_t current = audio_uart_lv_obj_x_44e486(object);
        audio_uart_lv_anim_values_4506ce(&animation,
                                          (int32_t)(0u - (uint32_t)current),
                                          (int32_t)((uint32_t)x - (uint32_t)current));
        write_word(&animation, 4u, (uintptr_t)audio_uart_lv_scroll_anim_x_44f3b8);
        write_word(&animation, 0x20u, (uintptr_t)audio_uart_lv_anim_path_450672);
        if ((uint8_t)audio_uart_lv_obj_event_451670(object, 0x0cu, &animation) != 1u)
            return;
        audio_uart_lv_anim_start_450408(&animation);
    }
    if (y != 0) {
        write_word(&animation, 0x30u, (uint32_t)audio_uart_lv_anim_duration_clamp_4505a2(
            audio_uart_lv_display_height_44faa8(display) >> 1, 200, 400));
        const int32_t current = audio_uart_lv_obj_y_44e498(object);
        audio_uart_lv_anim_values_4506ce(&animation,
                                          (int32_t)(0u - (uint32_t)current),
                                          (int32_t)((uint32_t)y - (uint32_t)current));
        write_word(&animation, 4u, (uintptr_t)audio_uart_lv_scroll_anim_y_44f3d4);
        write_word(&animation, 0x20u, (uintptr_t)audio_uart_lv_anim_path_450672);
        if ((uint8_t)audio_uart_lv_obj_event_451670(object, 0x0cu, &animation) == 1u)
            audio_uart_lv_anim_start_450408(&animation);
    }
}
